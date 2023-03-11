from datetime import date
from typing import List, Optional

import strawberry

from app import models


@strawberry.type
class User:
    id: strawberry.ID
    first_name: str
    last_name: str
    email: Optional[str]

    @strawberry.field
    async def profiles(self) -> List["Profile"]:
        profiles = await models.Profile.select().where(
            models.Profile.user_id == self.id
        )
        return [
            Profile(id=profile["id"], is_public=profile["is_public"])
            for profile in profiles
        ]


@strawberry.type
class Profile:
    id: strawberry.ID
    is_public: bool

    @strawberry.field
    async def user(self) -> Optional["User"]:
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
                email=profile["user_id.email"],
            )
            if profile["user_id.id"]
            else None
        )

    @strawberry.field
    async def promotion(self) -> Optional["Promotion"]:
        profile = (
            await models.Profile.select(models.Profile.promotion_id.all_columns())
            .where(models.Profile.id == self.id)
            .first()
        )
        return (
            Promotion(
                id=profile["promotion_id.id"],
                code=profile["promotion_id.code"],
                start_year=profile["promotion_id.start_year"],
                end_year=profile["promotion_id.end_year"],
            )
            if profile["promotion_id.id"]
            else None
        )


@strawberry.type
class Promotion:
    id: strawberry.ID
    code: str
    start_year: int
    end_year: int

    @strawberry.field
    async def profiles(self) -> List["Profile"]:
        profiles = await models.Profile.select().where(
            (models.Profile.promotion_id == self.id)
            & (models.Profile.is_public.eq(True))
        )
        return [
            Profile(id=profile["id"], is_public=profile["is_public"])
            for profile in profiles
        ]


@strawberry.type
class Matter:
    id: strawberry.ID
    abbr: str
    name: str


@strawberry.type
class Task:
    id: strawberry.ID
    date: date
    type: str
    title: str
    content: str

    @strawberry.field
    async def promotion(self) -> Optional["Promotion"]:
        task = (
            await models.Task.select(models.Task.promotion_id.all_columns())
            .where(models.Task.id == self.id)
            .first()
        )
        return (
            Promotion(
                id=task["promotion_id.id"],
                code=task["promotion_id.code"],
                start_year=task["promotion_id.start_year"],
                end_year=task["promotion_id.end_year"],
            )
            if task["promotion_id.id"]
            else None
        )

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
            )
            if task["matter_id.id"]
            else None
        )


@strawberry.type
class Week:
    number: int
    date_from: date
    date_to: date
    days: List["Day"]


@strawberry.type
class Day:
    date: date
    tasks: List["Task"]
