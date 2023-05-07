import os
from datetime import datetime
from typing import Optional

import jwt
import strawberry
from strawberry.types import Info

from app.schemas.schema_types import IsAuthenticated, User

SECRET = os.environ.get("JWT_SECRET", "")
assert len(SECRET) >= 31


def create_token(user_id):
    payload = {
        "sub": str(user_id),
        "iat": int(datetime.now().timestamp()),
    }
    return jwt.encode(payload, SECRET)


@strawberry.type
class AuthResult:
    uid: int
    email: str
    token: str


@strawberry.type
class Query:
    @strawberry.field(permission_classes=[IsAuthenticated])
    async def me(self, info: Info) -> User:
        return info.context["user"]


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def login(self, email: str, password: str) -> AuthResult:
        user_id = await User._model.login(username=email, password=password)

        if user_id:
            user = await User._model.select().where(User._model.id == user_id).first()
            return AuthResult(
                uid=user["id"],
                email=user["email"],
                token=create_token(user_id),
            )
        raise Exception("Something went wrong")

    @strawberry.mutation
    async def register(
        self,
        email: str,
        password: str,
        first_name: Optional[str] = "",
        last_name: Optional[str] = "",
    ) -> AuthResult:
        try:
            user = await User._model.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
        except Exception:
            raise Exception("Something went wrong")

        return AuthResult(
            uid=user["id"],
            email=user["email"],
            token=create_token(user["id"]),
        )
