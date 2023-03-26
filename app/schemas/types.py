import typing
from datetime import date
from typing import List, Optional

import strawberry
from strawberry.permission import BasePermission
from strawberry.types import Info

from app import models


def better_round(value, rounding):
    # mathematically useless but easier for Python floats rounding
    irounding = 1 / rounding  # ↲
    return int(round(value + rounding / 2, 10) * irounding) / irounding


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
class Gradebook:
    semesters: List["Semester"]
    _final_average: strawberry.Private[Optional[float]] = None
    _sub_4_matters: strawberry.Private[Optional[int]] = None
    _negative_points: strawberry.Private[Optional[float]] = None
    _success: strawberry.Private[Optional[bool]] = None

    @strawberry.field
    def final_average(self) -> Optional[float]:
        if not self.semesters:
            return None
        if self._final_average:
            return self._final_average
        averages = [semester.semester_average() for semester in self.semesters]
        self._final_average = better_round(sum(averages) / len(averages), 0.1)
        return self._final_average

    @strawberry.field
    def sub_4_matters(self) -> Optional[int]:
        if not self.semesters:
            return None
        if self._sub_4_matters:
            return self._sub_4_matters
        self._sub_4_matters = self.semesters[-1].sub_4_matters()
        return self._sub_4_matters

    @strawberry.field
    def negative_points(self) -> Optional[float]:
        if not self.semesters:
            return None
        if self._negative_points:
            return self._negative_points
        self._negative_points = self.semesters[-1].negative_points()
        return self._negative_points

    @strawberry.field
    def success(self) -> Optional[bool]:
        if not self.semesters:
            return None
        if self._success:
            return self._success
        self._success = (
            self.final_average() >= 4
            and self.sub_4_matters() <= 2
            and self.negative_points() >= -2
        )
        return self._success


@strawberry.type
class Semester:
    number: int
    date_from: date
    date_to: date
    averages: List["Average"]
    _semester_average: strawberry.Private[Optional[float]] = None
    _sub_4_matters: strawberry.Private[Optional[int]] = None
    _negative_points: strawberry.Private[Optional[float]] = None

    @strawberry.field
    def semester_average(self) -> Optional[float]:
        if not self.averages:
            return None
        if self._semester_average:
            return self._semester_average
        self._semester_average = better_round(
            sum(average.value() for average in self.averages) / len(self.averages), 0.1
        )
        return self._semester_average

    @strawberry.field
    def sub_4_matters(self) -> Optional[int]:
        if not self.averages:
            return None
        if self._sub_4_matters:
            return self._sub_4_matters
        self._sub_4_matters = len(
            [average for average in self.averages if average.value() < 4]
        )
        return self._sub_4_matters

    @strawberry.field
    def negative_points(self) -> Optional[float]:
        if not self.averages:
            return None
        if self._negative_points:
            return self._negative_points
        self._negative_points = -sum(
            4 - average.value() for average in self.averages if average.value() < 4
        )
        return self._negative_points


@strawberry.type
class Average:
    grades: List["Grade"]
    matter: "Matter"
    _value: strawberry.Private[Optional[float]] = None

    @strawberry.field
    def value(self) -> float:
        if self._value:
            return self._value
        average = sum(grade.value for grade in self.grades) / len(self.grades)
        self._value = better_round(average, 0.5)
        return self._value


@strawberry.type
class Grade:
    id: int
    value: float
    date: date

    @strawberry.field
    async def test(self) -> "Test":
        grade = (
            await models.Grade.select(models.Grade.test_id.all_columns())
            .where(models.Grade.id == self.id)
            .first()
        )
        return (
            Test(
                id=grade["test_id.id"],
                promotion=grade["test_id.promotion"],
                title=grade["test_id.title"],
                content=grade["test_id.content"],
            )
            if grade["test_id.id"]
            else None
        )

    @strawberry.field
    async def profile(self) -> "Profile":
        grade = (
            await models.Grade.select(models.Grade.profile_id.all_columns())
            .where(models.Grade.id == self.id)
            .first()
        )
        return (
            Profile(
                id=grade["profile_id.id"],
                promotion=grade["profile_id.promotion"],
                is_public=grade["profile_id.is_public"],
            )
            if grade["profile_id.id"]
            else None
        )


@strawberry.type
class Test:
    id: int
    promotion: str
    semester: int
    title: str
    content: str

    @strawberry.field
    async def matter(self) -> "Matter":
        test = (
            await models.Test.select(models.Test.matter_id.all_columns())
            .where(models.Test.id == self.id)
            .first()
        )
        return (
            Matter(
                id=test["matter_id.id"],
                abbr=test["matter_id.abbr"],
                name=test["matter_id.name"],
                short_name=test["matter_id.short_name"],
            )
            if test["matter_id.id"]
            else None
        )


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
