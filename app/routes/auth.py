import bcrypt
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from app.dependencies import create_access_token
from app.database import engine
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
def register_user(user: CreateUser):
    with Session(engine) as session:
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
def login_user(payload: LoginUser):
    with Session(engine) as session:
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
