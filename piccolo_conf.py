import toml
from piccolo.conf.apps import AppRegistry
from piccolo.engine.postgres import PostgresEngine
from piccolo.engine.sqlite import SQLiteEngine

with open("config/settings.toml", "r") as f:
    config = toml.load(f)

APP_REGISTRY = AppRegistry(apps=["app.piccolo_app", "piccolo.apps.user.piccolo_app"])

engine = config["general"]["engine"]
if engine == "sqlite":
    DB = SQLiteEngine(path=config["sqlite"]["path"])
if engine == "postgres":
    DB = PostgresEngine(config=config["postgres"])
