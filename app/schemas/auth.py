from datetime import datetime
from typing import Optional

import jwt
import strawberry
from strawberry.types import Info

from app.models import Profile, User

from . import types

SECRET = "secret"


def create_token(user_id):
    payload = {
        "sub": str(user_id),
        "iat": int(datetime.now().timestamp()),
    }
    return jwt.encode(payload, SECRET)


@strawberry.type
class Query:
    @strawberry.field
    async def me(self, info: Info) -> Optional[types.User]:
        return info.context.get("user", None)


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def login(self, email: str, password: str) -> types.AuthResult:
        user_id = await User.login(username=email, password=password)

        if user_id:
            user = await User.select().where(User.id == user_id).first()
            return types.AuthResult(
                user=types.User(
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
    ) -> types.AuthResult:
        try:
            user = await User.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                active=True,
            )
            await Profile.insert(
                Profile(
                    user_id=user["id"],
                    promotion=promotion,
                    is_public=is_public,
                )
            )
        except Exception:
            raise Exception("Something went wrong")

        return types.AuthResult(
            user=types.User(
                id=user["id"],
                first_name=user["first_name"],
                last_name=user["last_name"],
                email=user["email"],
                admin=user["admin"],
            ),
            token=create_token(user["id"]),
        )


# class IsAuthenticated(BasePermission):
#     message = "User is not authenticated"

#     def has_permission(self, source: typing.Any, info: Info, **kwargs) -> bool:
#         request: typing.Union[Request, WebSocket] = info.context["request"]

#         if "Authorization" in request.headers:
#             return authenticate_header(request)

#         if "auth" in request.query_params:
#             return authenticate_query_params(request)

#         return False
