from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class EmployeeBase(BaseModel):
    name: str = Field(..., min_length=3, examples=["Peter"])
    department: Optional[str] = Field(default=None, examples=["Development"])
    salary: Optional[float] = Field(default=None, gt=0, examples=[80000.0])
    email: EmailStr = Field(..., examples=["peter@example.com"])

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=3, examples=["Peter Updated"])
    department: Optional[str] = Field(default=None, examples=["QA"])
    salary: Optional[float] = Field(default=None, gt=0, examples=[90000.0])
    email: Optional[EmailStr] = Field(default=None, examples=["peter.updated@example.com"])

class EmployeeResponse(EmployeeBase):
    id: int

    class Config:
        from_attributes = True  # ✅ replaces orm_mode in Pydantic v2
