from typing import Annotated

from bcrypt import checkpw, gensalt, hashpw
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field

from ..db.database import db_dependency
from ..db.models import Users

router = APIRouter(prefix="/auth")


class CreateUserRequest(BaseModel):
    username: str = Field(min_length=6)
    email: str
    first_name: str
    last_name: str
    password: str = Field(min_length=8)
    role: str


def authenticate_user(username: str, password: str, db: db_dependency):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    hashed_password = password.encode("utf-8")
    if not checkpw(hashed_password, user.password.encode("utf-8")):
        return False
    return True


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    create_user_model = Users(**create_user_request.model_dump())

    if create_user_model is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not possible to create user.",
        )
    hashed_password = hashpw(
        password=create_user_request.password.encode("utf-8"), salt=gensalt()
    ).decode("utf-8")
    create_user_model.password = hashed_password

    db.add(create_user_model)
    db.commit()

    return create_user_model


@router.post("/signin", status_code=status.HTTP_200_OK)
async def signin(
    db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(
        username=form_data.username, password=form_data.password, db=db
    )
    if not user:
        return "Failed Authentication"
    return "Successful Authentication"
