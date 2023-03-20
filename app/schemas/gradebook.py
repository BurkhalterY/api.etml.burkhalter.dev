import strawberry

from app.models import Grade, Matter
from app.schemas import types


@strawberry.type
class Query:
    @strawberry.field(permission_classes=[types.IsAuthenticated])
    async def gradebook(self) -> types.Gradebook:
        # mother_grade = (
        #     await Grade.select()
        #     .where((Grade.parent_id.is_null()) & (Grade.profile_id == ME))
        #     .first()
        # )

        matters = await Matter.select()
        averages_data = [{matter["abbr"]: (0, 0)} for matter in matters]

        grades = await Grade.select().where(Grade.profile_id == ME)
        for grade in grades:
            averages_data[grade["matter"]][0] += float(grade["value"])
            averages_data[grade["matter"]][1] += 1

        averages = []
        for matter in matters:
            average_data = averages_data[matter["abbr"]]
            average = average_data[0] / average_data[1]  # TODO: round
            averages.append(types.Grade(value=average, subgrades=""))

        semester_average = types.Grade(value=5.2, subgrades=[])
        sub_4_matters = types.Grade(value=1, subgrades=[])
        negative_points = types.Grade(value=0.5, subgrades=[])

        success = (
            (float(semester_average.value) >= 4)
            and (float(sub_4_matters.value) <= 2)
            and (float(negative_points.value) <= 2)
        )

        return types.Gradebook(
            success=success,
            semester_average=semester_average,
            sub_4_matters=sub_4_matters,
            negative_points=negative_points,
            averages=averages,
        )
