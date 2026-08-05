import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status
from typing_extensions import Annotated
from database import SessionLocal
from fastapi.security import OAuth2PasswordBearer
from models import Users

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')

auth2bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


async def get_current_user(token: Annotated[str, Depends(auth2bearer)], db: db_dependency):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('username')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
        user_model = db.query(Users).filter(Users.id == user_id).first()
        if user_model is None or not user_model.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
        return {'username': username, 'id': user_id, 'role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')


user_dependency = Annotated[dict, Depends(get_current_user)]


def require_role(*roles):
    def role_dependency(user: user_dependency):
        if user.get('role') not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User does not have the required role.')
        return user
    return role_dependency

