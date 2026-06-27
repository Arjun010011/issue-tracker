from fastapi import APIRouter, HTTPException, status
from sqlalchemy import insert, select, update
from sqlalchemy.orm import Session

import bcrypt

from app.database import engine
from app.models import users
from app.schemas import CreateUser, UpdateUser, UserOut

router = APIRouter(prefix="/api/v1/auth/register/users", tags=["register user"])


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: CreateUser):
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
        return created_user


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    with Session(engine) as session:
        result = (
            session.execute(select(users).where(users.c.id == user_id))
            .mappings()
            .first()
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
            )

        return result


@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UpdateUser):
    update_data = payload.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="no fields provided to update",
        )

    if "password" in update_data:
        update_data["password"] = bcrypt.hashpw(
            update_data["password"].encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8")

    with Session(engine) as session:
        existing_user = (
            session.execute(select(users).where(users.c.id == user_id))
            .mappings()
            .first()
        )

        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
            )

        if "email" in update_data:
            email_in_use = (
                session.execute(
                    select(users).where(
                        users.c.email == update_data["email"],
                        users.c.id != user_id,
                    )
                )
                .mappings()
                .first()
            )

            if email_in_use:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="a user with the same email already exists",
                )

        session.execute(update(users).where(users.c.id == user_id).values(**update_data))
        session.commit()

        updated_user = (
            session.execute(select(users).where(users.c.id == user_id))
            .mappings()
            .first()
        )
        return updated_user
