import typing
from datetime import date
from typing import List, Optional

import strawberry
from strawberry.permission import BasePermission
from strawberry.types import Info

from app import models


@strawberry.type
class User:
    id: int
    email: str
    first_name: str
    last_name: str
    admin: bool

    @strawberry.field
    async def profiles(self) -> List["Profile"]:
        profiles = await models.Profile.select().where(
            models.Profile.user_id == self.id
        )
        return [
            Profile(
                id=profile["id"],
                promotion=profile["promotion"],
                is_public=profile["is_public"],
            )
            for profile in profiles
        ]


@strawberry.type
class Profile:
    id: int
    promotion: str
    is_public: bool

    @strawberry.field
    async def user(self, info: Info) -> Optional["User"]:
        my_id = getattr(info.context.get("user", None), "id", None)

        profile = (
            await models.Profile.select(models.Profile.user_id.all_columns())
            .where(models.Profile.id == self.id)
            .first()
        )
        return (
            User(
                id=profile["user_id.id"],
                first_name=profile["user_id.first_name"],
                last_name=profile["user_id.last_name"],
                email=profile["user_id.email"]
                if profile["user_id.id"] == my_id
                else "",
                admin=profile["user_id.admin"]
                if profile["user_id.id"] == my_id
                else False,
            )
            if profile["user_id.id"]
            else None
        )


@strawberry.type
class Matter:
    id: int
    abbr: str
    name: str
    short_name: str


@strawberry.type
class Task:
    id: int
    date: date
    promotion: str
    type: str
    title: str
    content: str

    @strawberry.field
    async def matter(self) -> Optional["Matter"]:
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
class AuthResult:
    user: "User"
    token: str


@strawberry.type
class Week:
    promotion: str
    number: int
    year: int
    date_from: date
    date_to: date
    days: List["Day"]


@strawberry.type
class Day:
    date: date
    tasks: List["Task"]


@strawberry.type
class Grade:
    id: Optional[int]
    value: float
    parent_grade: Optional["Grade"]
    subgrades: List["Grade"]


@strawberry.type
class Gradebook:
    semester_average: float
    sub_4_matters: int
    negative_points: float
    success: bool
    averages: List["Grade"]


class IsAuthenticated(BasePermission):
    message = "User is not authenticated"

    def has_permission(self, source: typing.Any, info: Info, **kwargs) -> bool:
        user = info.context["user"]
        return bool(user)


class IsAdmin(BasePermission):
    message = "User is not admin"

    def has_permission(self, source: typing.Any, info: Info, **kwargs) -> bool:
        user = info.context["user"]
        return user.admin if user else False
