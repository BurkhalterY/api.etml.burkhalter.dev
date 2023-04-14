from enum import Enum

from piccolo.apps.user.tables import BaseUser as User
from piccolo.columns import (
    Boolean,
    Date,
    Float,
    ForeignKey,
    Integer,
    OnDelete,
    Serial,
    Text,
    Varchar,
)
from piccolo.table import Table

# After changes in this file, you have to create a migration:
#
# poetry shell
# piccolo migrations new app --auto
# piccolo migrations forwards app


class Formation(Table):
    id = Serial(primary_key=True)
    name = Varchar()
    duration = Integer()


class Matter(Table):
    id = Serial(primary_key=True)
    abbr = Varchar(unique=True, length=8)
    name = Varchar()
    short_name = Varchar()
    parent_id = ForeignKey("self", on_delete=OnDelete.restrict)


class School(Table):
    id = Serial(primary_key=True)
    abbr = Varchar(length=32)
    full_name = Varchar()
    street = Varchar()
    city = Varchar()
    plz = Varchar()
    phone = Varchar(length=24)
    email = Varchar()
    website = Varchar()


class Promotion(Table):
    id = Serial(primary_key=True)
    formation_id = ForeignKey(Formation, on_delete=OnDelete.restrict)
    code = Varchar(length=8)
    school_id = ForeignKey(School, on_delete=OnDelete.restrict)
    year_start = Integer()
    year_end = Integer()


class Profile(Table):
    id = Serial(primary_key=True)
    user_id = ForeignKey(User, on_delete=OnDelete.restrict)
    promotion_id = ForeignKey(Promotion, on_delete=OnDelete.restrict)
    year_start = Integer()
    year_end = Integer()
    is_public = Boolean()


class Semester(Table):
    id = Serial(primary_key=True)
    profile_id = ForeignKey(Profile)
    number = Integer()


class Test(Table):
    id = Serial(primary_key=True)
    promotion_id = ForeignKey(Promotion, on_delete=OnDelete.restrict)
    matter_id = ForeignKey(Matter, on_delete=OnDelete.restrict)
    title = Varchar()
    content = Text()


class Grade(Table):
    id = Serial(primary_key=True)
    semester_id = ForeignKey(Semester)
    test_id = ForeignKey(Test, on_delete=OnDelete.restrict)
    value = Float()
    date = Date()


class Task(Table):
    class Type(str, Enum):
        homework = "homework"
        test = "test"
        info = "info"
        summary = "summary"

    id = Serial(primary_key=True)
    date = Date()
    promotion_id = ForeignKey(Promotion, on_delete=OnDelete.restrict)
    type = Varchar(length=16, choices=Type)
    matter_id = ForeignKey(Matter, on_delete=OnDelete.restrict)
    title = Varchar()
    content = Text()
    test_id = ForeignKey(Test, on_delete=OnDelete.restrict)


TABLES = [Formation, Matter, Promotion, Profile, Semester, Test, Grade, Task]
