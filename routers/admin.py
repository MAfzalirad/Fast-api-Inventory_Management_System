from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pydantic import Field
from starlette import status
from models import Items, Users
from dependencies import db_dependency, require_role, user_dependency, bcrypt_context
from typing_extensions import Annotated
from schemas import UserCreate, UserResponse
from sqlalchemy.exc import IntegrityError


router = APIRouter(
    prefix='/admin',
    tags=['admin']
)


@router.get('/items', status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency, user: user_dependency, role_check: Annotated[dict, Depends(require_role('admin', 'manager'))]):
    return db.query(Items).all()

@router.get('/items/{item_id}', status_code=status.HTTP_200_OK)
async def get_item(db: db_dependency, user: user_dependency, role_check: Annotated[dict, Depends(require_role('admin', 'manager'))], item_id: int = Path(gt=0)):
    requested_item = db.query(Items).filter(Items.id == item_id).first()
    if requested_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does't have access")
    return requested_item


@router.post('/create-user', status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(db: db_dependency, user_request: UserCreate, role_check: Annotated[dict, Depends(require_role('admin', 'manager'))]):
    user_model = Users(
        username = user_request.username,
        email = user_request.email,
        first_name = user_request.first_name,
        last_name = user_request.last_name,
        hash_password = bcrypt_context.hash(user_request.password),
        is_active = True,
        role = user_request.role
    )
    if user_model.role == 'manager':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Cannot create a manager user.')
    try:
        db.add(user_model)
        db.commit()
        db.refresh(user_model)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Username or email already exists')
    return user_model