from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status

from ..db.database import db_dependency
from ..db.models import Todos
from .auth import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform this action",
        )
    return db.query(Todos).all()


@router.delete("todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)
):
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform this action",
        )
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail="To-do not found!")

    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()
