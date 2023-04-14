from datetime import datetime
from typing import Any, List, Optional

import jwt
import strawberry
from strawberry.permission import BasePermission
from strawberry.types import Info

from app import models

SECRET = "secret"


def create_token(user_id):
    payload = {
        "sub": str(user_id),
        "iat": int(datetime.now().timestamp()),
    }
    return jwt.encode(payload, SECRET)


@strawberry.type
class User:
    id: int
    email: str
    first_name: str
    last_name: str
    admin: bool

    @strawberry.field
    async def profiles(self) -> List["Profile"]:
        profiles = await models.Profile.select().where(
            models.Profile.user_id == self.id
        )
        return [
            Profile(
                id=profile["id"],
                promotion=profile["promotion"],
                is_public=profile["is_public"],
            )
            for profile in profiles
        ]


@strawberry.type
class Profile:
    id: int
    promotion: str
    is_public: bool

    @strawberry.field
    async def user(self, info: Info) -> Optional["User"]:
        my_id = getattr(info.context.get("user", None), "id", None)

        profile = (
            await models.Profile.select(models.Profile.user_id.all_columns())
            .where(models.Profile.id == self.id)
            .first()
        )
        return (
            User(
                id=profile["user_id.id"],
                first_name=profile["user_id.first_name"],
                last_name=profile["user_id.last_name"],
                email=profile["user_id.email"]
                if profile["user_id.id"] == my_id
                else "",
                admin=profile["user_id.admin"]
                if profile["user_id.id"] == my_id
                else False,
            )
            if profile["user_id.id"]
            else None
        )


@strawberry.type
class AuthResult:
    user: User
    token: str


class IsAuthenticated(BasePermission):
    message = "User is not authenticated"

    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        user = info.context["user"]
        return bool(user)


class IsAdmin(BasePermission):
    message = "User is not admin"

    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        user = info.context["user"]
        return user.admin if user else False


@strawberry.type
class Query:
    @strawberry.field(permission_classes=[IsAuthenticated])
    async def me(self, info: Info) -> User:
        return info.context["user"]

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def profiles(self, promotion: str) -> List[Profile]:
        profiles = await models.Profile.select().where(
            (models.Profile.promotion == promotion)
            & (models.Profile.is_public.eq(True))
        )
        return [
            Profile(
                id=profile["id"],
                promotion=profile["promotion"],
                is_public=profile["is_public"],
            )
            for profile in profiles
        ]


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def login(self, email: str, password: str) -> AuthResult:
        user_id = await models.User.login(username=email, password=password)

        if user_id:
            user = await models.User.select().where(models.User.id == user_id).first()
            return AuthResult(
                user=User(
                    id=user["id"],
                    first_name=user["first_name"],
                    last_name=user["last_name"],
                    email=user["email"],
                    admin=user["admin"],
                ),
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
        promotion: Optional[str] = "",
        is_public: Optional[bool] = False,
    ) -> AuthResult:
        try:
            user = await models.User.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                active=True,
            )
            await models.Profile.insert(
                models.Profile(
                    user_id=user["id"],
                    promotion=promotion,
                    is_public=is_public,
                )
            )
        except Exception:
            raise Exception("Something went wrong")

        return AuthResult(
            user=User(
                id=user["id"],
                first_name=user["first_name"],
                last_name=user["last_name"],
                email=user["email"],
                admin=user["admin"],
            ),
            token=create_token(user["id"]),
        )
