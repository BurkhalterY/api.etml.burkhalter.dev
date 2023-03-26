from datetime import date, timedelta
from typing import List, Optional

import strawberry
from strawberry.types import Info

from app.models import Grade, Matter, Profile, Test
from app.schemas import types


@strawberry.type
class Query:
    @strawberry.field(permission_classes=[types.IsAuthenticated])
    async def gradebook(self, info: Info, promotion: str) -> types.Gradebook:
        grades = await Grade.select(
            Grade.all_columns(),
            Grade.test_id.matter_id,
        ).where(
            (Grade.profile_id.user_id == info.context["user"].id)
            & (Grade.profile_id.promotion == promotion)
        )

        matters_db = await Matter.select()
        matters = {
            matter["id"]: types.Matter(
                id=matter["id"],
                abbr=matter["abbr"],
                name=matter["name"],
                short_name=matter["short_name"],
            )
            for matter in matters_db
        }

        semesters = [
            types.Semester(
                number=i + 1,
                date_from=date(2022, 8, 22),
                date_to=date(2023, 1, 20),
                averages=[],
            )
            for i in range(4)
        ]
        for semester in semesters:
            for grade in grades:
                matter_id = grade["test_id.matter_id"]
                if matter_id not in semester["averages"]:
                    semester["averages"][matter_id] = types.Average(
                        matter=matters[matter_id], grades=[]
                    )
                average = semester["averages"][matter_id]

                average.grades.append(
                    types.Grade(
                        id=grade["id"],
                        value=grade["value"],
                        date=grade["date"],
                    )
                )

        return types.Gradebook(averages=averages.values())

    @strawberry.field(permission_classes=[types.IsAuthenticated])
    async def tests(self, info: Info, promotion: str) -> List[types.Test]:
        rated_tests = await Grade.select(Grade.test_id).where(
            (Grade.profile_id.user_id == info.context["user"].id)
            & (Grade.profile_id.promotion == promotion)
        )
        test_ids = [grade["test_id"] for grade in rated_tests]

        profile = (
            await Profile.select(Profile.id)
            .where(
                (Profile.id == info.context["user"].id)
                & (Profile.promotion == promotion)
            )
            .first()
        )

        tests = await Test.select().where(
            (Test.promotion == promotion) & (Test.id.not_in(test_ids))
        )
        return [
            types.Test(
                id=test["id"],
                promotion=test["promotion"],
                title=test["title"],
                content=test["content"],
            )
            for test in tests
        ]


@strawberry.type
class Mutation:
    @strawberry.mutation(permission_classes=[types.IsAdmin])
    async def test(
        self,
        promotion: str,
        matter_id: int,
        title: str,
        content: Optional[str] = "",
        id: Optional[int] = None,
    ) -> types.Test:
        promotion = promotion.lower()
        if not re.match("^[a-z0-9]{3,6}$", promotion):
            raise Exception("Unconventional promotion name provided.")

        if id:
            await Test.update(
                {
                    Test.promotion: promotion,
                    Test.matter_id: matter_id,
                    Test.title: title,
                    Test.content: content,
                }
            ).where(Test.id == id)
        else:
            id = (
                await Test.insert(
                    Test(
                        promotion=promotion,
                        matter_id=matter_id,
                        title=title,
                        content=content,
                    )
                )
            )[0]["id"]

        return types.Test(
            id=id,
            promotion=promotion,
            title=title,
            content=content,
        )

    @strawberry.mutation(permission_classes=[types.IsAuthenticated])
    async def grade(
        self,
        info: Info,
        test_id: int,
        value: float,
        date: date,
        id: Optional[int] = None,
    ) -> types.Test:
        test = await Test.select(Test.id).where(Test.id == test_id).first()
        if test is None:
            raise Exception(f"Test with id {test_id} doesn't exist")

        profile_id = (
            await Profile.select(Profile.id)
            .where(
                (Profile.id == info.context["user"].id)
                & (Profile.promotion == test["promotion"])
            )
            .first()
        )

        if id:
            await Grade.update(
                {
                    Grade.profile_id: profile_id,
                    Grade.test_id: test_id,
                    Grade.value: value,
                    Grade.date: date,
                }
            ).where(Grade.id == id)
        else:
            id = (
                await Grade.insert(
                    Grade(
                        profile_id=profile_id,
                        test_id=test_id,
                        value=value,
                        date=date,
                    )
                )
            )[0]["id"]

        return types.Grade(
            id=id,
            value=value,
            date=date,
        )
