from functools import cached_property
from typing import Optional

import strawberry

from app import models

# from . import auth


@strawberry.type
class User:
    id: int

    @cached_property
    def record(self) -> strawberry.Private[Optional[models.User]]:
        print("shit")
        return models.User.select().where(models.User.id == self.id).first().run_sync()

    @strawberry.field
    async def first_name(self) -> Optional[str]:
        if self.record:
            return self.record["first_name"]
        return None

    @strawberry.field
    async def last_name(self) -> Optional[str]:
        if self.record:
            return self.record["last_name"]
        return None

    @strawberry.field
    async def email(self) -> Optional[str]:
        if self.record:
            return self.record["email"]
        return None


@strawberry.type
class Query:
    @strawberry.field
    async def user(self, id: int) -> Optional[User]:
        return User(id=id)


# @strawberry.type
# class Mutation(auth.Mutation):
#     pass


schema = strawberry.Schema(Query)
