import os

from dotenv import load_dotenv
from piccolo.conf.apps import AppRegistry
from piccolo.engine.sqlite import SQLiteEngine

load_dotenv()

SQLITE_PATH = os.environ.get("SQLITE_PATH")
APP_REGISTRY = AppRegistry(apps=["app.piccolo_app", "piccolo.apps.user.piccolo_app"])
DB = SQLiteEngine(path=SQLITE_PATH)
