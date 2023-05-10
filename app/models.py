from enum import Enum

from piccolo.apps.user.tables import BaseUser
from piccolo.columns import (
    M2M,
    Boolean,
    Date,
    Float,
    ForeignKey,
    Integer,
    LazyTableReference,
    OnDelete,
    Serial,
    Time,
    Varchar,
)
from piccolo.table import Table

# After changes in this file, you have to create a migration:
#
# poetry shell
# piccolo migrations new app --auto
# piccolo migrations forwards app


class User(BaseUser, tablename="piccolo_user"):
    is_public = Boolean()
    threads_ids = M2M(LazyTableReference("ThreadUser", module_path=__name__))
    tasks_ids = M2M(LazyTableReference("TaskUser", module_path=__name__))


class Formation(Table):
    id = Serial(primary_key=True)
    name = Varchar()
    title_m = Varchar()
    title_f = Varchar()
    duration = Integer()
    eqf_level = Integer()


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


class Thread(Table):
    id = Serial(primary_key=True)
    formation_id = ForeignKey(Formation, on_delete=OnDelete.restrict)
    code = Varchar(length=8)
    school_id = ForeignKey(School, on_delete=OnDelete.restrict)
    year_start = Integer()
    year_end = Integer()
    users_ids = M2M(LazyTableReference("ThreadUser", module_path=__name__))


class ThreadUser(Table):
    thread_id = ForeignKey(Thread, on_delete=OnDelete.restrict)
    user_id = ForeignKey(User, on_delete=OnDelete.restrict)


class Matter(Table):
    id = Serial(primary_key=True)
    abbr = Varchar(unique=True, length=8)
    name = Varchar()
    short_name = Varchar()
    parent_id = ForeignKey("self", on_delete=OnDelete.restrict)


class Test(Table):
    id = Serial(primary_key=True)
    thread_id = ForeignKey(Thread, on_delete=OnDelete.restrict)
    matter_id = ForeignKey(Matter, on_delete=OnDelete.restrict)
    title = Varchar()
    semester = Integer()
    tasks_ids = M2M(LazyTableReference("TaskTest", module_path=__name__))


class Grade(Table):
    id = Serial(primary_key=True)
    user_id = ForeignKey(User, on_delete=OnDelete.restrict)
    value = Float()
    test_id = ForeignKey(Test, on_delete=OnDelete.restrict)
    matter_id = ForeignKey(Matter, on_delete=OnDelete.restrict)
    title = Varchar()
    semester = Integer()
    date = Date()


class Task(Table):
    class Type(str, Enum):
        homework = "homework"
        test = "test"
        info = "info"

    id = Serial(primary_key=True)
    thread_id = ForeignKey(Thread, on_delete=OnDelete.restrict)
    date = Date()
    matter_id = ForeignKey(Matter, on_delete=OnDelete.restrict)
    type = Varchar(length=16, choices=Type)
    title = Varchar()
    users_ids = M2M(LazyTableReference("TaskUser", module_path=__name__))
    tests_ids = M2M(LazyTableReference("TaskTest", module_path=__name__))


class TaskUser(Table):
    task_id = ForeignKey(Task, on_delete=OnDelete.restrict)
    user_id = ForeignKey(User, on_delete=OnDelete.restrict)
    done = Boolean()
    at = Time()


class TaskTest(Table):
    task_id = ForeignKey(Task, on_delete=OnDelete.restrict)
    test_id_id = ForeignKey(Test, on_delete=OnDelete.restrict)


TABLES = [
    Formation,
    Grade,
    Matter,
    School,
    Task,
    TaskTest,
    TaskUser,
    Test,
    Thread,
    ThreadUser,
    User,
]
