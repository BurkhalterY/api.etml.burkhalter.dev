from enum import Enum

from piccolo.apps.user.tables import BaseUser as User
from piccolo.columns import Date, ForeignKey, Integer, Serial, Text, Varchar
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


class Matter(Table):
    id = Serial(primary_key=True)
    abbr = Varchar(length=8)
    name = Varchar()


class Promotion(Table):
    id = Serial(primary_key=True)
    code = Varchar(length=8)
    start_year = Integer()
    end_year = Integer()


class Profile(Table):
    id = Serial(primary_key=True)
    user_id = ForeignKey(User)
    promotion_id = ForeignKey(Promotion)


class Task(Table):
    class Type(str, Enum):
        homework = "homework"
        test = "test"
        info = "info"
        summary = "summary"

    id = Serial(primary_key=True)
    promotion_id = ForeignKey(Promotion)
    date = Date()
    type = Varchar(length=16, choices=Type)
    matter_id = ForeignKey(Matter)
    title = Varchar()
    content = Text()


TABLES = [Matter, Promotion, Profile, Task]
