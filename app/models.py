from enum import Enum

from piccolo.apps.user.tables import BaseUser as User
from piccolo.columns import Boolean, Date, ForeignKey, Serial, Text, Varchar
from piccolo.table import Table

MATTERS = [
    "fran",
    "alle",
    "angl",
    "mathfon",
    "scinat",
    "chimi",
    "phys",
    "mathspe",
    "hispol",
    "ecdr",
    "tib",
    "tip",
    "etml",
]


class Profile(Table):
    id = Serial(primary_key=True)
    user_id = ForeignKey(User)
    promotion = Varchar(length=8)
    is_public = Boolean()


class Matter(Table):
    id = Serial(primary_key=True)
    abbr = Varchar(length=8)
    name = Varchar()


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
    matter_id = ForeignKey(Matter)
    title = Varchar()
    content = Text()


TABLES = [Matter, Profile, Task]
