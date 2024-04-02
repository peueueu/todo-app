from typing import Optional
from fastapi import APIRouter, Path, HTTPException
from pydantic import BaseModel, Field
from starlette import status

from ..db.models import Todos
from ..db.database import db_dependency

router = APIRouter(prefix="/todo")


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: Optional[bool] = Field(default=False)


class TodoUpdateRequest(BaseModel):
    title: Optional[str] = Field(min_length=3, default=None)
    description: Optional[str] = Field(min_length=3, max_length=100, default=None)
    priority: Optional[int] = Field(gt=0, lt=6, default=None)
    complete: Optional[bool] = Field(default=False)


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Todos).all()


@router.get("/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail="To-do not found!")

    return todo_model


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_request: TodoRequest):
    todo_model = Todos(**todo_request.model_dump())

    if todo_model is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not possible to create To-do.",
        )

    db.add(todo_model)
    db.commit()
    return {"message": "To-do created with success!"}


@router.put(
    "/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model_exclude_none=True,
)
async def update_todo(
    db: db_dependency, todo_request: TodoUpdateRequest, todo_id: int = Path(gt=0)
):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail="To-do not found!")

    todo_model.title = (
        todo_request.title if todo_request.title is not None else todo_model.title
    )
    todo_model.description = (
        todo_request.description
        if todo_request.description is not None
        else todo_model.description
    )
    todo_model.priority = (
        todo_request.priority
        if todo_request.priority is not None
        else todo_model.priority
    )
    todo_model.complete = (
        todo_request.complete
        if todo_request.complete is not None
        else todo_model.complete
    )

    db.add(todo_model)
    db.commit()


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail="To-do not found!")

    db.delete(todo_model)
    db.commit()
