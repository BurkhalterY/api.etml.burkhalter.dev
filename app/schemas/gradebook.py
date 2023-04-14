from datetime import date
from typing import List, Optional

import strawberry
from strawberry.types import Info

from app.models import Grade, Matter, Profile, Test


def better_round(value, rounding):
    # mathematically useless but easier for Python floats rounding
    irounding = 1 / rounding  # ↲
    return int(round(value + rounding / 2, 10) * irounding) / irounding


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
