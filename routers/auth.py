from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from models import Users
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from dependencies import db_dependency, SECRET_KEY, ALGORITHM, bcrypt_context
from schemas import UserResponse, UserRegister
from sqlalchemy.exc import IntegrityError


router = APIRouter(
    prefix ='/auth',
    tags = ['auth']
)


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(db: db_dependency, user_request: UserRegister):
    user_model = Users(
        username = user_request.username,
        email = user_request.email,
        first_name = user_request.first_name,
        last_name = user_request.last_name,
        hash_password = bcrypt_context.hash(user_request.password),
        is_active = True,
    )
    user_model.role = 'viewer'
    try:
        db.add(user_model)
        db.commit()
        db.refresh(user_model)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Username or email already exists')
    return user_model


def authenticate_user(db, username: str, password: str):
    requested_user = db.query(Users).filter(Users.username == username).first()
    if requested_user is None:
        return False
    if bcrypt_context.verify(password, requested_user.hash_password):
        return requested_user
    else:
        return False


def create_access_token (username: str, user_id: int,user_role: str, expires_delta: timedelta):
    encode = {'username': username, 'id': user_id, 'role': user_role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post('/token', response_model=Token)
async def login_for_access_token(db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(db, username=form_data.username, password = form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    token = create_access_token(user.username, user.id,user.role, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}