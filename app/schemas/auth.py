from typing import Optional

import strawberry

from app.models import Profile, User

from .types import User


@strawberry.type
class LoginSuccess:
    user: User


@strawberry.type
class LoginError:
    message: str


LoginResult = strawberry.union("LoginResult", (LoginSuccess, LoginError))


@strawberry.type
class RegisterSuccess:
    success: bool


@strawberry.type
class RegisterError:
    message: str


RegisterResult = strawberry.union("RegisterResult", (RegisterSuccess, RegisterError))


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def login(self, email: str, password: str) -> LoginResult:
        user_id = await BaseUser.login(username=email, password=password)

        if user_id:
            profile = (
                await Profile.select(
                    Profile.all_columns(), Profile.user_id.all_columns()
                )
                .where(Profile.user_id == user_id)
                .first()
            )
            return LoginSuccess(
                user=User(
                    id=user_id,
                    first_name=profile["user_id.first_name"],
                    last_name=profile["user_id.last_name"],
                    email=profile["user_id.email"],
                    promotion=profile["promotion_id"],
                )
            )
        return LoginError(message="Something went wrong")

    @strawberry.mutation
    async def register(
        self,
        email: str,
        password: str,
        first_name: Optional[str] = "",
        last_name: Optional[str] = "",
        promotion: Optional[int] = None,
    ) -> RegisterResult:
        promotion_id = None

        try:
            user = await BaseUser.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                active=True,
            )
            await Profile.insert(Profile(user_id=user["id"], promotion_id=promotion_id))
        except ValueError as e:
            print(e)
            return RegisterError(message="Something went wrong")

        return RegisterSuccess(success=True)
