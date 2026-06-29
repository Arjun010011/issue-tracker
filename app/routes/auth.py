import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from app.dependencies import create_access_token, get_db
from app.models import users
from app.schemas import AuthResponse, CreateUser, LoginUser

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def _build_auth_response(user_row) -> AuthResponse:
    token = create_access_token(
        {
            "sub": user_row["email"],
            "user_id": user_row["id"],
            "role": user_row["role"].value if hasattr(user_row["role"], "value") else user_row["role"],
        }
    )
    return AuthResponse(access_token=token, user=user_row)


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: CreateUser, session: Session = Depends(get_db)):
    existing_user = (
        session.execute(select(users).where(users.c.email == user.email))
        .mappings()
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="a user with the same email already exists",
        )

    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
    new_user = {
        "name": user.name,
        "email": user.email,
        "password": hashed_password.decode("utf-8"),
        "role": user.role,
    }

    result = session.execute(insert(users).values(**new_user).returning(users))
    created_user = result.mappings().first()
    session.commit()

    return _build_auth_response(created_user)


@router.post("/login", response_model=AuthResponse)
def login_user(payload: LoginUser, session: Session = Depends(get_db)):
    user_row = (
        session.execute(select(users).where(users.c.email == payload.email))
        .mappings()
        .first()
    )

    if not user_row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid email or password",
        )

    is_password_valid = bcrypt.checkpw(
        payload.password.encode("utf-8"),
        user_row["password"].encode("utf-8"),
    )

    if not is_password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid email or password",
        )

    return _build_auth_response(user_row)
