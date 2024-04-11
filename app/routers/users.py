from typing import Annotated

from bcrypt import checkpw, gensalt, hashpw
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from starlette import status

from ..db.database import db_dependency
from ..db.models import Users
from .auth import get_current_user

router = APIRouter(prefix="/users", tags=["User"])
user_dependency = Annotated[dict, Depends(get_current_user)]


class PasswordChangeRequest(BaseModel):
    password: str = Field(min_length=8)
    new_password: str = Field(min_length=8)


class PhoneNumberChangeRequest(BaseModel):
    phone_number: str = Field(min_length=5)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    return db.query(Users).filter(Users.id == user.get("user_id")).first()


@router.put("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_user_password(
    user: user_dependency,
    db: db_dependency,
    password_change_request: PasswordChangeRequest,
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    user_to_update = db.query(Users).filter(Users.id == user.get("user_id")).first()
    if not checkpw(
        password_change_request.password.encode("utf-8"),
        user_to_update.password.encode("utf-8"),
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error on password change.",
        )
    user_to_update.password = hashpw(
        password=password_change_request.new_password.encode("utf-8"), salt=gensalt()
    ).decode("utf-8")
    db.add(user_to_update)
    db.commit()


@router.put("/change-phone-number", status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(
    user: user_dependency,
    db: db_dependency,
    phone_number_change_request: PhoneNumberChangeRequest,
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    user_to_update = db.query(Users).filter(Users.id == user.get("user_id")).first()

    user_to_update.phone_number = phone_number_change_request.phone_number
    db.add(user_to_update)
    db.commit()
