from datetime import date, datetime
from typing import Any, List, Optional

import strawberry
from strawberry.permission import BasePermission
from strawberry.types import Info

from app import models


class IsAuthenticated(BasePermission):
    message = "User is not authenticated"

    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        user = info.context["user"]
        return bool(user)


class IsAdmin(BasePermission):
    message = "User is not admin"

    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        user = info.context["user"]
        return user.admin if user else False


class HavePublicProfile(BasePermission):
    message = "User visibility is not public"

    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        user = info.context["user"]
        return user.is_public if user else False


@strawberry.type
class User:
    _model: strawberry.Private[Any] = models.User

    id: int
    username: str
    first_name: str
    last_name: str
    admin: bool
    is_public: bool

    email: strawberry.Private[str]
    password: strawberry.Private[str]
    active: strawberry.Private[bool]
    superuser: strawberry.Private[bool]
    last_login: strawberry.Private[datetime]

    @strawberry.field
    async def threads_ids(self) -> List[int]:
        user = (
            await User._model.select(
                User._model.threads_ids(Thread._model.id, as_list=True)
            )
            .where((User._model.id == self.id) & User._model.is_public.eq(True))
            .first()
        )
        return user["threads_ids"] if user else []

    @strawberry.field
    async def threads(self) -> List["Thread"]:
        user = (
            await User._model.select(User._model.threads_ids())
            .where((User._model.id == self.id) & User._model.is_public.eq(True))
            .first()
        )
        return [Thread(**thread) for thread in user["threads_ids"]] if user else []


@strawberry.type
class Formation:
    _model: strawberry.Private[Any] = models.Formation

    id: int
    name: str
    title_m: str
    title_f: str
    duration: int
    eqf_level: int


@strawberry.type
class School:
    _model: strawberry.Private[Any] = models.School

    id: int
    abbr: str
    full_name: str
    street: str
    city: str
    plz: str
    phone: str
    email: str
    website: str


@strawberry.type
class Thread:
    _model: strawberry.Private[Any] = models.Thread

    id: int
    formation_id: int
    code: str
    school_id: int
    year_start: int
    year_end: int

    @strawberry.field
    async def formation(self) -> Optional[Formation]:
        formation = (
            await Formation._model.select()
            .where(Formation._model.id == self.formation_id)
            .first()
        )
        return Formation(**formation) if formation else None

    @strawberry.field
    async def school(self) -> Optional[School]:
        school = (
            await School._model.select()
            .where(School._model.id == self.school_id)
            .first()
        )
        return School(**school) if school else None

    @strawberry.field
    async def tests_ids(self) -> List[int]:
        return (
            await Test._model.select(Test._model.id)
            .where(Test._model.thread_id == self.id)
            .output(as_list=True)
        )

    @strawberry.field
    async def tests(self) -> List["Test"]:
        tests = await Test._model.select().where(Test._model.thread_id == self.id)
        return [Test(**test) for test in tests]

    @strawberry.field
    async def tasks_ids(self) -> List[int]:
        return (
            await Task._model.select(Task._model.id)
            .where(Task._model.thread_id == self.id)
            .output(as_list=True)
        )

    @strawberry.field
    async def tasks(self) -> List["Task"]:
        tasks = await Task._model.select().where(Task._model.thread_id == self.id)
        return [Task(**task) for task in tasks]

    @strawberry.field(permission_classes=[HavePublicProfile])
    async def users(self) -> List["User"]:
        thread = (
            await Thread._model.select(Thread._model.users_ids())
            .where(
                (Thread._model.id == self.id)
                & User._model.is_public.eq(True)  # TODO: test, don't sure if it works
            )
            .first()
        )
        return [User(**user) for user in thread.users_ids] if thread else []


@strawberry.type
class Matter:
    _model: strawberry.Private[Any] = models.Matter

    id: int
    abbr: str
    name: str
    short_name: str
    parent_id: int

    @strawberry.field
    async def parent(self) -> Optional["Matter"]:
        parent = (
            await Matter._model.select()
            .where(Matter._model.id == self.parent_id)
            .first()
        )
        return Matter(**parent) if parent else None

    @strawberry.field
    async def children(self) -> List["Matter"]:
        children = await Matter._model.select().where(
            Matter._model.parent_id == self.id
        )
        return [Matter(**child) for child in children]


@strawberry.type
class Test:
    _model: strawberry.Private[Any] = models.Test

    id: int
    thread_id: int
    matter_id: int
    title: str
    date: date

    @strawberry.field
    async def thread(self) -> Optional[Thread]:
        thread = (
            await Thread._model.select()
            .where(Thread._model.id == self.thread_id)
            .first()
        )
        return Thread(**thread) if thread else None

    @strawberry.field
    async def matter(self) -> Optional[Matter]:
        matter = (
            await Matter._model.select()
            .where(Matter._model.id == self.matter_id)
            .first()
        )
        return Matter(**matter) if matter else None

    @strawberry.field
    async def tasks_ids(self) -> List[int]:
        test = (
            await Test._model.select(
                Test._model.tasks_ids(Task._model.id, as_list=True)
            )
            .where(Test._model.id == self.id)
            .first()
        )
        return test.tasks_ids if test else []

    @strawberry.field
    async def task(self) -> List["Task"]:
        test = (
            await Test._model.select(Test._model.tasks_ids())
            .where(Test._model.id == self.id)
            .first()
        )
        return [Task(**task) for task in test.tasks_ids] if test else []


@strawberry.type
class Grade:
    _model: strawberry.Private[Any] = models.Grade

    id: int
    user_id: int
    value: float
    test_id: int
    matter_id: int
    title: str
    date: date

    @strawberry.field
    async def user(self) -> Optional[User]:
        user = (
            await User._model.select()
            .where((User._model.id == self.user_id) & User._model.is_public.eq(True))
            .first()
        )
        return User(**user) if user else None

    @strawberry.field
    async def test(self) -> Optional[Test]:
        test = await Test._model.select().where(Test._model.id == self.test_id).first()
        return Test(**test) if test else None

    @strawberry.field
    async def matter(self) -> Optional[Matter]:
        matter = (
            await Matter._model.select()
            .where(Matter._model.id == self.matter_id)
            .first()
        )
        return Matter(**matter) if matter else None


@strawberry.type
class Task:
    _model: strawberry.Private[Any] = models.Task

    id: int
    thread_id: int
    date: date
    matter_id: int
    type: str
    title: str

    @strawberry.field
    async def thread(self) -> Optional[Thread]:
        thread = (
            await Thread._model.select()
            .where(Thread._model.id == self.thread_id)
            .first()
        )
        return Thread(**thread) if thread else None

    @strawberry.field
    async def matter(self) -> Optional[Matter]:
        matter = (
            await Matter._model.select()
            .where(Matter._model.id == self.matter_id)
            .first()
        )
        return Matter(**matter) if matter else None

    @strawberry.field
    async def tests_ids(self) -> List[int]:
        task = (
            await Task._model.select(
                Task._model.tests_ids(Task._model.id, as_list=True)
            )
            .where(Task._model.id == self.id)
            .first()
        )
        return task.tests_ids if task else []

    @strawberry.field
    async def test(self) -> List["Test"]:
        task = (
            await Task._model.select(Task._model.tests_ids())
            .where(Task._model.id == self.id)
            .first()
        )
        return [Test(**test) for test in task.tests_ids] if task else []

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def done(self, info: Info) -> bool:
        status = (
            await models.TaskUser.select(models.TaskUser.done)
            .where(
                (models.TaskUser.user_id == info.context["user"].id)
                & (models.TaskUser.task_id == self.id)
            )
            .first()
        )
        return status["done"] if status else False
