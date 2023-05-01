import re
from datetime import date, timedelta
from typing import Any, List, Optional

import strawberry

from app import models
from app.schemas.auth import IsAdmin
from app.schemas.school import Promotion


def daterange(start_date, end_date, inclusive=True):
    for n in range((end_date - start_date).days + inclusive):
        yield start_date + timedelta(n)


@strawberry.type
class Matter:
    _model: strawberry.Private[Any] = models.Matter

    id: int
    abbr: str
    name: str
    short_name: str
    parent_id: int


@strawberry.type
class Task:
    _model: strawberry.Private[Any] = models.Task

    id: int
    date: date
    promotion_id: int
    type: str
    matter_id: int
    title: str
    content: str
    test_id: int

    @strawberry.field
    async def matter(self) -> Optional[Matter]:
        matter = (
            await Matter._model.select()
            .where(Matter._model.id == self.matter_id)
            .first()
        )
        return Matter(**matter) if matter else None

    @strawberry.field
    async def promotion(self) -> Optional[Promotion]:
        promotion = (
            await Promotion._model.select()
            .where(Promotion._model.id == self.promotion_id)
            .first()
        )
        return Promotion(**promotion) if promotion else None

    # @strawberry.field
    # async def test(self) -> Optional[Test]:
    #     test = (
    #         await Test._model.select()
    #         .where(Test._model.id == self.test_id)
    #         .first()
    #     )
    #     return Test(**test) if test else None


@strawberry.type
class Day:
    date: date
    tasks: List[Task]


@strawberry.type
class Week:
    promotion_id: int
    number: int
    year: int
    date_from: date
    date_to: date
    days: List[Day]

    @strawberry.field
    async def promotion(self) -> Optional[Promotion]:
        promotion = (
            await Promotion._model.select()
            .where(Promotion._model.id == self.promotion_id)
            .first()
        )
        return Promotion(**promotion) if promotion else None


@strawberry.type
class Query:
    @strawberry.field
    async def matters(self) -> List[Matter]:
        matters = await Matter._model.select().order_by("name")
        return [Matter(**matter) for matter in matters]

    @strawberry.field
    async def week(
        self,
        promotion: str,
        number: Optional[int] = None,
        year: Optional[int] = None,
    ) -> Week:
        if number is None:
            number = date.today().isocalendar().week
        if year is None:
            year = date.today().year
        monday = date.fromisocalendar(year, number, 1)
        friday = date.fromisocalendar(year, number, 5)
        sunday = date.fromisocalendar(year, number, 7)

        db_tasks = await models.Task.select().where(
            (models.Task.promotion_id.code == promotion)
            & (models.Task.date >= monday)
            & (models.Task.date <= sunday)
        )
        days = []
        for d in daterange(monday, sunday):
            tasks = [Task(**task) for task in db_tasks if task["date"] == d]
            days.append(Day(date=d, tasks=tasks))

        return Week(
            promotion=promotion,
            number=number,
            year=year,
            date_from=monday,
            date_to=friday,
            days=days,
        )


@strawberry.type
class Mutation:
    @strawberry.mutation(permission_classes=[IsAdmin])
    async def task(
        self,
        date: date,
        promotion: str,
        type: str,
        matter_id: int,
        title: str,
        content: Optional[str] = "",
        id: Optional[int] = None,
    ) -> Task:
        promotion = promotion.lower()
        if not re.match("^[a-z0-9]{3,6}$", promotion):
            raise Exception("Unconventional promotion name provided.")

        allowed_types = ("homework", "test", "info", "summary")
        if type not in allowed_types:
            raise Exception("Only allowed types are: " + ", ".join(allowed_types))

        if id:
            await models.Task.update(
                {
                    models.Task.date: date,
                    models.Task.promotion: promotion,
                    models.Task.type: type,
                    models.Task.matter_id: matter_id,
                    models.Task.title: title,
                    models.Task.content: content,
                }
            ).where(models.Task.id == id)
        else:
            id = (
                await models.Task.insert(
                    models.Task(
                        date=date,
                        promotion=promotion,
                        type=type,
                        matter_id=matter_id,
                        title=title,
                        content=content,
                    )
                )
            )[0]["id"]

        return Task(
            id=id,
            date=date,
            promotion=promotion,
            type=type,
            title=title,
            content=content,
        )

    @strawberry.mutation(permission_classes=[IsAdmin])
    async def delete_task(self, id: int) -> bool:
        await models.Task.delete().where(models.Task.id == id)
        return True
