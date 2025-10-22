from fastapi import FastAPI, Depends, HTTPException, status, Response, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.future import select
from typing import List
import asyncio, random
from jose import JWTError, jwt
from datetime import datetime
from . import models, schemas
from .database import engine, Base, get_db
from fastapi.responses import StreamingResponse #this is req for streaming
import json
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
import redis.asyncio as redis 

SECRET_KEY = "this_is_a_fast_api_session_12"
ALGORITHM = "HS256"
CHANNEL = "employees_events"

app = FastAPI(title="Employee Management Service")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") #client docs

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database schema created")

    redis_client = redis.from_url("redis://localhost:14879", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")
    print("Cache init!!")

employee_redis = redis.from_url("redis://localhost:14879", encoding="utf8", decode_responses=True)

async def send_welcome_email(employee_name: str):
    await asyncio.sleep(2)
    print(f"Email sent to {employee_name}: welcome to the team!!!!")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate the token",
        headers={"WWW-Authenticate":"Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return {"username":username}


@app.post("/employees/", response_model= schemas.EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee: schemas.EmployeeCreate,
    background_tasks: BackgroundTasks,
    response: Response,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    new_emp = models.Employee(**employee.dict())
    db.add(new_emp)
    await db.commit()
    event = {"type" :"employee_created", "data" : {"id" : new_emp.id, "name" : new_emp.name} , "timestamp" : datetime.now().isoformat()}
    await employee_redis.publish(CHANNEL, json.dumps(event))
    await db.refresh(new_emp)
    response.headers["X-Request-ID"]=f"req-{random.randint(1000,9999)}"
    background_tasks.add_task(send_welcome_email, new_emp.name)
    return new_emp

@app.get("/employees/", response_model=List[schemas.EmployeeResponse])
@cache(expire=60)
async def get_employees(db: AsyncSession = Depends(get_db),  current_user: dict = Depends(get_current_user)):
    await asyncio.sleep(1)
    result = await db.execute(select(models.Employee))
    employees = result.scalars().all()
    return employees

#Get employee by Id
@app.get("/employees/{emp_id}", response_model=schemas.EmployeeResponse)
async def get_employee(emp_id: int, db: AsyncSession = Depends(get_db),  current_user: dict = Depends(get_current_user)):
    result = await db.execute(select(models.Employee).where(models.Employee.id == emp_id))
    employee = result.scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


#update an employee
@app.put("/employees/{emp_id}", response_model=schemas.EmployeeResponse)
async def update_employee(emp_id: int, emp_update: schemas.EmployeeUpdate, db: AsyncSession = Depends(get_db),  current_user: dict = Depends(get_current_user)):
    result = await db.execute(select(models.Employee).where(models.Employee.id == emp_id))
    employee = result.scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    for key, value in emp_update.dict(exclude_unset=True).items():
        setattr(employee, key, value)
    await db.commit()
    await db.refresh(employee)
    return employee


#Delete an employee func 
@app.delete("/employees/{emp_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(emp_id: int, db: AsyncSession= Depends(get_db),  current_user: dict = Depends(get_current_user)):
    result = await db.execute(select(models.Employee).where(models.Employee.id == emp_id))
    employee = result.scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    await db.delete(employee)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)  

#SSE endpoint
@app.get("/stream/employees")
async def stream_employees(
    current_user: dict = Depends(get_current_user)
):
    async def event_generator():
        while True:
            update = {"timestamp": datetime.now().isoformat(), "message": f"Employee Count: {random.randint(10,100)}",
                       "user":current_user["username"]}
            yield f"data : {json.dumps(update)}\n\n"
            await asyncio.sleep(5)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control":"no-cache","Connection":"keep-alive"}
    )
  