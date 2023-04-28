import re
from datetime import date, timedelta
from typing import List, Optional

import strawberry

from app import models
from app.schemas.auth import IsAdmin


def daterange(start_date, end_date, inclusive=True):
    for n in range((end_date - start_date).days + inclusive):
        yield start_date + timedelta(n)


@strawberry.type
class Matter:
    id: int
    abbr: str
    name: str
    short_name: str


@strawberry.type
class Task:
    _model = models.Task

    id: int
    date: date
    promotion: str
    type: str
    title: str
    content: str

    @strawberry.field
    async def matter(self) -> Optional[Matter]:
        task = (
            await models.Task.select(models.Task.matter_id.all_columns())
            .where(models.Task.id == self.id)
            .first()
        )
        return (
            Matter(
                id=task["matter_id.id"],
                abbr=task["matter_id.abbr"],
                name=task["matter_id.name"],
                short_name=task["matter_id.short_name"],
            )
            if task["matter_id.id"]
            else None
        )


@strawberry.type
class Day:
    date: date
    tasks: List[Task]


@strawberry.type
class Week:
    promotion: str
    number: int
    year: int
    date_from: date
    date_to: date
    days: List[Day]


@strawberry.type
class Query:
    @strawberry.field
    async def test(self) -> List[Task]:
        tasks = await models.Matter.select().order_by("name")
        return [Task(task) for task in tasks]

    @strawberry.field
    async def matters(self) -> List[Matter]:
        matters = await models.Matter.select().order_by("name")
        return [
            Matter(
                id=matter["id"],
                abbr=matter["abbr"],
                name=matter["name"],
                short_name=matter["short_name"],
            )
            for matter in matters
        ]

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
            tasks = [
                Task(
                    id=task["id"],
                    date=task["date"],
                    promotion=promotion,
                    type=task["type"],
                    title=task["title"],
                    content=task["content"],
                )
                for task in db_tasks
                if task["date"] == d
            ]
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
