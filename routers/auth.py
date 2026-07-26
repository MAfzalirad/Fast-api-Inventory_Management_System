from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from database import SessionLocal
from starlette import status
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

router = APIRouter(
    prefix ='/auth',
    tags = ['auth']
)


SECRET_KEY = '36275d3e4e10a0f5ca9933d470e2b8ff0ffd027d7cfcbdf9b5726ff1f0b89d65'
ALGORITHM = 'HS256'


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

auth2bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


class UserCreate(BaseModel):
    user_name: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, user_request: UserCreate):
    user_model = Users(
        user_name = user_request.user_name,
        email = user_request.email,
        first_name = user_request.first_name,
        last_name = user_request.last_name,
        hash_password = bcrypt_context.hash(user_request.password),
        is_active = True,
        role = user_request.role
    )

    db.add(user_model)
    db.commit()
    return user_model


def authenticate_user(db, username: str, password: str):
    requested_user = db.query(Users).filter(Users.user_name == username).first()
    if requested_user is None:
        return False
    if bcrypt_context.verify(password, requested_user.hash_password):
        return requested_user
    else:
        return False


def create_access_token (user_name: str, user_id: int,user_role: str, expires_delta: timedelta):
    encode = {'username': user_name, 'id': user_id, 'role': user_role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post('/token', response_model=Token)
async def login_for_access_token(db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(db, username=form_data.username, password = form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    token = create_access_token(user.user_name, user.id,user.role, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}


async def get_current_user(token: Annotated[str, Depends(auth2bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get('username')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
        return {'username': username, 'id': user_id, 'role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')