import os.path

from piccolo.conf.apps import AppConfig

from app.models import TABLES

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
APP_CONFIG = AppConfig(
    app_name="app",
    migrations_folder_path=os.path.join(CURRENT_DIRECTORY, "piccolo_migrations"),
    table_classes=TABLES,
    migration_dependencies=[],
    commands=[],
)
