import os

from piccolo.conf.apps import AppRegistry
from piccolo.engine.postgres import PostgresEngine

DATABASE = os.environ.get("POSTGRES_DB")
USER = os.environ.get("POSTGRES_USER")
PASSWORD = os.environ.get("POSTGRES_PASSWORD")
HOST = os.environ.get("POSTGRES_HOST", "localhost")
PORT = int(os.environ.get("POSTGRES_PORT", 5432))

APP_REGISTRY = AppRegistry(apps=["app.piccolo_app", "piccolo.apps.user.piccolo_app"])
DB = PostgresEngine(
    {
        "host": HOST,
        "port": PORT,
        "database": DATABASE,
        "user": USER,
        "password": PASSWORD,
    }
)
