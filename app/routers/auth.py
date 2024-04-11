from datetime import datetime, timedelta, timezone
from typing import Annotated

from bcrypt import checkpw, gensalt, hashpw
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import PyJWTError as JWTError
from jwt import decode as jwt_decode
from jwt import encode as jwt_encode
from pydantic import BaseModel, Field

from ..config.settings import settings
from ..db.database import db_dependency
from ..db.models import Users

router = APIRouter(prefix="/auth", tags=["Auth"])

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/signin")


class CreateUserRequest(BaseModel):
    username: str = Field(min_length=6)
    email: str
    first_name: str
    last_name: str
    password: str = Field(min_length=8)
    role: str
    phone_number: str = Field(min_length=5)


class Token(BaseModel):
    access_token: str
    token_type: str


def authenticate_user(username: str, password: str, db: db_dependency):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    hashed_password = password.encode("utf-8")
    if not checkpw(hashed_password, user.password.encode("utf-8")):
        return False
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt_decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")

        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials.",
            )
        return {"user_id": user_id, "username": username, "user_role": user_role}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
        )


def create_access_token(
    username: str, user_id: int, role: str, expires_delta: timedelta
):
    to_encode = {
        "sub": username,
        "id": user_id,
        "role": role,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + expires_delta,
    }
    return jwt_encode(
        payload=to_encode, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )


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


@router.post("/signin", response_model=Token, status_code=status.HTTP_200_OK)
async def signin(
    db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(
        username=form_data.username, password=form_data.password, db=db
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not authenticate user.",
        )
    token = create_access_token(
        username=user.username,
        user_id=user.id,
        role=user.role,
        expires_delta=timedelta(minutes=20),
    )
    return {"access_token": token, "token_type": "bearer"}
