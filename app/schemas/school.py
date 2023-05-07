from typing import Any, List, Optional

import strawberry

from app import models
from app.schemas.auth import IsAdmin


@strawberry.type
class Query:
    @strawberry.field
    async def schools(self) -> List[School]:
        schools = await models.School.select().order_by("abbr")
        return [School(school) for school in schools]

    async def school(self, id: int) -> Optional[School]:
        school = await models.School.select().where(models.School.id == id).first()
        return School(school) if school else None

    @strawberry.field
    async def formations(self) -> List[Formation]:
        formations = await models.Formation.select().order_by("name")
        return [School(school) for school in schools]

    async def formation(self, id: int) -> Optional[Formation]:
        school = await models.School.select().where(models.School.id == id).first()
        return School(school) if school else None


@strawberry.type
class Mutation:
    @strawberry.mutation(permission_classes=[IsAdmin])
    async def school(
        self,
        abbr: str,
        full_name: str,
        street: Optional[str] = "",
        city: Optional[str] = "",
        plz: Optional[str] = "",
        phone: Optional[str] = "",
        email: Optional[str] = "",
        website: Optional[str] = "",
        id: Optional[int] = None,
    ) -> School:
        if id:
            await models.School.update(
                {
                    models.School.abbr: abbr,
                    models.School.full_name: full_name,
                    models.School.street: street,
                    models.School.city: city,
                    models.School.plz: plz,
                    models.School.phone: phone,
                    models.School.email: email,
                    models.School.website: website,
                }
            ).where(models.School.id == id)
        else:
            id = (
                await models.School.insert(
                    models.School(
                        abbr=abbr,
                        full_name=full_name,
                        street=street,
                        city=city,
                        plz=plz,
                        phone=phone,
                        email=email,
                        website=website,
                    )
                )
            )[0]["id"]
        return id
