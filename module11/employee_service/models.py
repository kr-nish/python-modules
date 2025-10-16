from sqlalchemy import Column, Integer, String, Float
from .database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    department = Column(String(50))
    salary = Column(Float)
    email = Column(String(120), unique=True, index=True)