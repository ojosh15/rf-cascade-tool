from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import Select
from sqlalchemy.orm import Session
from typing import Annotated
from datetime import datetime, timedelta, timezone

from app.database import get_db
from app.database.models.users import User, UserResponseModel, UserCreateModel, Token
from app.crud.crud_users import authenticate_user, create_access_token, get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash, get_user_by_email

router = APIRouter(tags=["_auth_"])

@router.post("/register", response_model=UserResponseModel, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreateModel, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create and save new user
    hashed_pw = get_password_hash(user_in.password)
    new_user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hashed_pw
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/token")
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db),
) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/users/me/", response_model=UserResponseModel)
def read_users_me(
    current_user: Annotated[UserResponseModel, Depends(get_current_active_user)],
):
    return current_user