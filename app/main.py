import toml
import uvicorn
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware

from app.schemas import GraphQL, schema

with open("app/config/settings.toml", "rb") as f:
    config = toml.load(f)
dev_mode = config["general"]["environment"] == "dev"

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


def start():
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=dev_mode)
