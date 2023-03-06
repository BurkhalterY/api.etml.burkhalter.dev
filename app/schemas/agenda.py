from datetime import date, timedelta
from typing import List, Optional

import strawberry
from strawberry.types import Info

from app.models import Matter, Profile, Task

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
        # info: Info,
        promotion: int,
        number: Optional[int] = None,
        year: Optional[int] = None,
    ) -> types.Week:
        # allowed = await Profile.count().where(
        #     (Profile.user_id == info.context["user"].id)
        #     & (Profile.promotion_id == promotion)
        # )
        # if not allowed:
        #     raise Exception("You are not a member of this promotion!")

        if number is None:
            number = date.today().isocalendar().week
        if year is None:
            year = date.today().year
        monday = date.fromisocalendar(year, number, 1)
        friday = date.fromisocalendar(year, number, 5)
        sunday = date.fromisocalendar(year, number, 7)

        days = []
        for d in daterange(monday, sunday):
            db_tasks = await Task.select().where(
                (Task.promotion_id == promotion) & (Task.date == d)
            )
            tasks = [
                types.Task(
                    id=task["id"],
                    date=task["date"],
                    type=task["type"],
                    title=task["title"],
                    content=task["content"],
                )
                for task in db_tasks
            ]
            days.append(types.Day(date=d, tasks=tasks))

        return types.Week(number=number, date_from=monday, date_to=friday, days=days)
