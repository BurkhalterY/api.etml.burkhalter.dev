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


class Profile(Table):
    id = Serial(primary_key=True)
    user_id = ForeignKey(User, on_delete=OnDelete.set_null)
    promotion = Varchar(length=8)
    is_public = Boolean()


class Matter(Table):
    id = Serial(primary_key=True)
    abbr = Varchar(unique=True, length=8)
    name = Varchar()
    short_name = Varchar()
    parent_id = ForeignKey("self", on_delete=OnDelete.restrict)


class Test(Table):
    id = Serial(primary_key=True)
    promotion = Varchar(length=8)
    semester = Integer()
    matter_id = ForeignKey(Matter, on_delete=OnDelete.restrict)
    title = Varchar()
    content = Text()


class Grade(Table):
    id = Serial(primary_key=True)
    profile_id = ForeignKey(Profile, on_delete=OnDelete.set_null)
    test_id = ForeignKey(Test, on_delete=OnDelete.set_null)
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
    promotion = Varchar(length=8)
    type = Varchar(length=16, choices=Type)
    matter_id = ForeignKey(Matter, on_delete=OnDelete.restrict)
    title = Varchar()
    content = Text()
    test_id = ForeignKey(Test, on_delete=OnDelete.set_null)


TABLES = [Grade, Matter, Profile, Task, Test]
