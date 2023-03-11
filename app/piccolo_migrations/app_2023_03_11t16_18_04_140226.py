from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Varchar
from piccolo.columns.indexes import IndexMethod


ID = "2023-03-11T16:18:04:140226"
VERSION = "0.106.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="app", description=DESCRIPTION
    )

    manager.drop_table(class_name="Promotion", tablename="promotion")

    manager.drop_column(
        table_class_name="Profile",
        tablename="profile",
        column_name="promotion_id",
        db_column_name="promotion_id",
    )

    manager.drop_column(
        table_class_name="Task",
        tablename="task",
        column_name="promotion_id",
        db_column_name="promotion_id",
    )

    manager.add_column(
        table_class_name="Profile",
        tablename="profile",
        column_name="promotion",
        db_column_name="promotion",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 8,
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    manager.add_column(
        table_class_name="Task",
        tablename="task",
        column_name="promotion",
        db_column_name="promotion",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 8,
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    return manager
