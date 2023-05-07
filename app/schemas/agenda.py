import re
from datetime import date, timedelta
from typing import List, Optional

import strawberry
from strawberry.types import Info

from app import models
from app.schemas.schema_types import IsAdmin, Matter, Task, Thread


@strawberry.type
class Day:
    date: date
    tasks: List[Task]


@strawberry.type
class Week:
    threads: List[Thread]
    include_self: bool
    number: int
    year: int
    date_from: date
    date_to: date
    days: List[Day]


@strawberry.type
class Query:
    @strawberry.field
    async def week(
        self,
        info: Info,
        threads: Optional[List[str]] = [],
        include_self: Optional[bool] = False,
        number: Optional[int] = None,
        year: Optional[int] = None,
    ) -> Week:
        def daterange(start_date, end_date, inclusive=True):
            for n in range((end_date - start_date).days + inclusive):
                yield start_date + timedelta(n)

        if number is None:
            number = date.today().isocalendar().week
        if year is None:
            year = date.today().year
        monday = date.fromisocalendar(year, number, 1)
        friday = date.fromisocalendar(year, number, 5)
        sunday = date.fromisocalendar(year, number, 7)

        db_threads = []
        if threads:
            db_threads = await Thread._model.select().where(
                Thread._model.code.is_in(threads)
                & (
                    (
                        Thread._model.year_start
                        if sunday >= date(year, 8, 1)
                        else Thread._model.year_end
                    )
                    == year
                )
            )
        threads_ids = [thread["id"] for thread in db_threads]

        individual_tasks_ids = []
        if include_self:
            individual_tasks_ids = (
                await models.TaskUser.select(models.TaskUser.task_id)
                .where(
                    (models.TaskUser.user_id == info.context["user"].id)
                    & models.TaskUser.task_id.thread_id.is_null()
                )
                .output(as_list=True)
            )

        query_sources = []
        if threads_ids:
            query_sources.append(Task._model.thread_id.is_in(threads_ids))
        if individual_tasks_ids:
            query_sources.append(Task._model.id.is_in(individual_tasks_ids))

        if query_sources:
            query = query_sources[0]
            for source in query_sources[1:]:
                query |= source

            db_tasks = await Task._model.select().where(
                query & (Task._model.date >= monday) & (Task._model.date <= sunday)
            )
            days = []
            for d in daterange(monday, sunday):
                tasks = [Task(**task) for task in db_tasks if task["date"] == d]
                days.append(Day(date=d, tasks=tasks))
        else:
            days = [Day(date=d, tasks=[]) for d in daterange(monday, sunday)]

        return Week(
            threads=[Thread(**thread) for thread in db_threads],
            include_self=include_self,
            number=number,
            year=year,
            date_from=monday,
            date_to=friday,
            days=days,
        )

    @strawberry.field(permission_classes=[IsAdmin])
    async def matters(self) -> List[Matter]:
        matters = await Matter._model.select().order_by("name")
        return [Matter(**matter) for matter in matters]

    @strawberry.field(permission_classes=[IsAdmin])
    async def threads(self) -> List[Thread]:
        threads = await Thread._model.select().order_by("code")
        return [Thread(**thread) for thread in threads]


@strawberry.type
class Mutation:
    @strawberry.mutation(permission_classes=[IsAdmin])
    async def task(
        self,
        thread_id: int,
        date: date,
        matter_id: int,
        type: str,
        title: str,
        id: Optional[int] = None,
    ) -> Task:
        allowed_types = [item.value for item in models.Task.Type]
        if type not in allowed_types:
            raise Exception("Only allowed types are: " + ", ".join(allowed_types))

        values = {
            "thread_id": thread_id,
            "date": date,
            "matter_id": matter_id,
            "type": type,
            "title": title,
        }

        if id:
            task = (
                await Task._model.update(**values)
                .where(Task._model.id == id)
                .returning(*Task._model.all_columns())
            )
        else:
            task = await Task._model.insert(Task._model(**values)).returning(
                *Task._model.all_columns()
            )

        return Task(**task[0])

    @strawberry.mutation(permission_classes=[IsAdmin])
    async def delete_task(self, id: int) -> bool:
        await Task._model.delete().where(Task._model.id == id)
        return True
