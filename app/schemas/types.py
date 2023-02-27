from typing import Optional

import strawberry

from app import models


@strawberry.type
class Promotion:
    id: strawberry.ID
    code: str
    start_year: int
    end_year: int


@strawberry.type
class User:
    id: strawberry.ID
    first_name: str
    last_name: str
    email: str

    @strawberry.field
    async def promotion(self) -> Optional[Promotion]:
        record = (
            await models.Promotion.select().where(models.Promotion.id == id).first()
        )
        return Promotion(
            id=record["id"],
            cpde=record["cpde"],
            start_year=record["start_year"],
            end_year=record["end_year"],
        )
