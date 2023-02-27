from piccolo.conf.apps import AppRegistry
from piccolo.engine.postgres import PostgresEngine

APP_REGISTRY = AppRegistry(apps=["app.piccolo_app", "piccolo.apps.user.piccolo_app"])

DB = PostgresEngine(
    config={
        "database": "etml_burkhalter_dev",
        "user": "postgres",
        "password": "toor",
        "host": "localhost",
        "port": 5432,
    }
)
