import re
from datetime import date, timedelta
from typing import List, Optional

import strawberry

from app.models import Matter, Task
from app.schemas import types


def daterange(start_date, end_date, inclusive=True):
    for n in range((end_date - start_date).days + inclusive):
        yield start_date + timedelta(n)


@strawberry.type
class Query:
    @strawberry.field
    async def matters(self) -> List[types.Matter]:
        matters = await Matter.select()
        return [
            types.Matter(
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
    ) -> types.Week:
        if number is None:
            number = date.today().isocalendar().week
        if year is None:
            year = date.today().year
        monday = date.fromisocalendar(year, number, 1)
        friday = date.fromisocalendar(year, number, 5)
        sunday = date.fromisocalendar(year, number, 7)

        db_tasks = await Task.select().where(
            (Task.promotion == promotion)
            & (Task.date >= monday)
            & (Task.date <= sunday)
        )
        days = []
        for d in daterange(monday, sunday):
            tasks = [
                types.Task(
                    id=task["id"],
                    date=task["date"],
                    promotion=task["promotion"],
                    type=task["type"],
                    title=task["title"],
                    content=task["content"],
                )
                for task in db_tasks
                if task["date"] == d
            ]
            days.append(types.Day(date=d, tasks=tasks))

        return types.Week(
            promotion=promotion,
            number=number,
            year=year,
            date_from=monday,
            date_to=friday,
            days=days,
        )


@strawberry.type
class Mutation:
    @strawberry.mutation(permission_classes=[types.IsAdmin])
    async def task(
        self,
        date: date,
        promotion: str,
        type: str,
        matter: str,
        title: str,
        content: Optional[str] = "",
        id: Optional[int] = None,
    ) -> types.Task:
        promotion = promotion.lower()
        if not re.match("^[a-z0-9]{3,6}$", promotion):
            raise Exception("Unconventional promotion name provided.")

        allowed_types = ("homework", "test", "info", "summary")
        if type not in allowed_types:
            raise Exception("Only allowed types are: " + ", ".join(allowed_types))

        matter_id = await Matter.select(Matter.id).where(Matter.abbr == matter).first()
        if matter_id is None:
            raise Exception(f"Matter with code {matter} doesn't exist")
        matter_id = matter_id["id"]

        if id:
            await Task.update(
                {
                    Task.date: date,
                    Task.promotion: promotion,
                    Task.type: type,
                    Task.matter_id: matter_id,
                    Task.title: title,
                    Task.content: content,
                }
            ).where(Task.id == id)
        else:
            id = (
                await Task.insert(
                    Task(
                        date=date,
                        promotion=promotion,
                        type=type,
                        matter_id=matter_id,
                        title=title,
                        content=content,
                    )
                )
            )[0]["id"]

        return types.Task(
            id=id,
            date=date,
            promotion=promotion,
            type=type,
            title=title,
            content=content,
        )
