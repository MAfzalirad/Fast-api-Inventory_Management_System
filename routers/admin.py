from fastapi import APIRouter, Depends, HTTPException, Query, Path
from starlette import status
from models import Items
from dependencies import db_dependency, require_role, user_dependency, bcrypt_context
from typing_extensions import Annotated


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