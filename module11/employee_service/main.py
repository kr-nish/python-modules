from fastapi import FastAPI, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
import asyncio, random
from . import models, schemas
from .database import engine, Base, get_db

app = FastAPI(title="Employee Management Service")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database schema created")

@app.post("/employees/", response_model= schemas.EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee: schemas.EmployeeCreate,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    new_emp = models.Employee(**employee.dict())
    db.add(new_emp)
    await db.commit()
    await db.refresh(new_emp)
    response.headers["X-Request-ID"]=f"req-{random.randint(1000,9999)}"
    return new_emp

@app.get("/employees/", response_model=List[schemas.EmployeeResponse])
async def get_employees(db: AsyncSession = Depends(get_db)):
    await asyncio.sleep(1)
    result = await db.execute(select(models.Employee))
    employees = result.scalars().all()
    return employees

#Get employee by Id
@app.get("/employees/{emp_id}", response_model=schemas.EmployeeResponse)
async def get_employee(emp_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Employee).where(models.Employee.id == emp_id))
    employee = result.scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


#update an employee
@app.put("/employees/{emp_id}", response_model=schemas.EmployeeResponse)
async def update_employee(emp_id: int, emp_update: schemas.EmployeeUpdate, db: AsyncSession = Depends(get_db)):
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
async def delete_employee(emp_id: int, db: AsyncSession= Depends(get_db)):
    result = await db.execute(select(models.Employee).where(models.Employee.id == emp_id))
    employee = result.scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    await db.delete(employee)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)  
  