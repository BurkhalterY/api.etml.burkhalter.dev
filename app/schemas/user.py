from typing import List

import strawberry
from strawberry.types import Info

from app.models import Profile

from . import types


@strawberry.type
class Query:
    @strawberry.field
    async def me(self, info: Info) -> types.User:
        return info.context["user"]

    @strawberry.field
    async def profiles(self, promotion: str) -> List[types.Profile]:
        profiles = await Profile.select().where(
            (Profile.promotion == promotion) & (Profile.is_public.eq(True))
        )
        return [
            types.Profile(
                id=profile["id"],
                promotion=profile["promotion"],
                is_public=profile["is_public"],
            )
            for profile in profiles
        ]
