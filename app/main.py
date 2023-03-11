import sys

import uvicorn
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware

from app.models import User
from app.schemas import GraphQL, schema

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
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


def grant():
    emails = sys.argv[1:]
    User.update({User.admin: True}).where(User.email.is_in(emails)).run_sync()
    print("Done: " + ", ".join(emails))


def ungrant():
    emails = sys.argv[1:]
    User.update({User.admin: False}).where(User.email.is_in(emails)).run_sync()
    print("Done: " + ", ".join(emails))
