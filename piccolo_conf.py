import tomllib
from piccolo.conf.apps import AppRegistry
from piccolo.engine.postgres import PostgresEngine

with open("database.toml", "rb") as f:
    config = tomllib.load(f)

APP_REGISTRY = AppRegistry(apps=["app.piccolo_app", "piccolo.apps.user.piccolo_app"])

DB = PostgresEngine(config=config["db"])
