from datetime import date, timedelta
from typing import List, Optional

import strawberry

from app.models import Matter, Task

from . import types


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
                    type=task["type"],
                    title=task["title"],
                    content=task["content"],
                )
                for task in db_tasks
                if task["date"] == d
            ]
            days.append(types.Day(date=d, tasks=tasks))

        return types.Week(number=number, date_from=monday, date_to=friday, days=days)
