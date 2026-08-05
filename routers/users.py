from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from models import Users
from schemas import UserResponse, UserVerification
from dependencies import db_dependency, user_dependency


router = APIRouter(
    prefix='/users',
    tags=['users']
)


@router.get('/', status_code=status.HTTP_200_OK)
async def read_user_info(db: db_dependency, user: user_dependency):
    requested_user = db.query(Users).filter(Users.id == user.get('id')).first()
    if requested_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    response_model = UserResponse.model_validate(requested_user)
    return response_model

@router.put('/password', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(db: db_dependency, user: user_dependency, user_verification: UserVerification):
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if user_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    if not bcrypt_context.verify( user_verification.password, user_model.hash_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not Authenticate User')
    user_model.hash_password = bcrypt_context.hash(user_verification.new_password)

    db.add(user_model)
    db.commit()