from sqlalchemy import Column, Integer, String
from passlib.context import CryptContext # hashing the password
from .auth_database import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__="users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)


    def verify_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, self.hashed_password)
    
    @staticmethod
    def get_passowrd_hash(password: str) -> str:
        return pwd_context.hash(password)