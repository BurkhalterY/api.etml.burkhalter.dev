from typing import List

import strawberry

from app.models import Profile
from app.schemas import types


@strawberry.type
class Query:
    @strawberry.field(permission_classes=[types.IsAuthenticated])
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
