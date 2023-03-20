import os.path

import toml
import uvicorn
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware

from app.schemas import GraphQL, schema

settings_file = "config/settings.toml"
config = {}
if os.path.isfile(settings_file):
    with open(settings_file, "r") as f:
        config = toml.load(f).get("general", {})
dev_mode = config.get("environment", "dev") != "prod"

graphql_app = GraphQL(schema)
app = Starlette()
app.add_route("/graphql", graphql_app)
app.add_websocket_route("/graphql", graphql_app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


ssl_keyfile = "config/key.pem"
ssl_certfile = "config/cert.pem"
if not (os.path.isfile(ssl_keyfile) and os.path.isfile(ssl_certfile)):
    ssl_keyfile = None
    ssl_certfile = None


def start():
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=config.get("port", 8000),
        reload=dev_mode,
        ssl_keyfile=ssl_keyfile,
        ssl_certfile=ssl_certfile,
    )
