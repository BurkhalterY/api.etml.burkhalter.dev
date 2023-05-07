import os

import uvicorn
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware

from app.schemas import GraphQL, schema

ENVIRONMENT = os.environ.get("ENVIRONMENT", "dev")
WEB_PORT = int(os.environ.get("WEB_PORT", 8000))


is_prod = ENVIRONMENT == "prod"
is_dev = ENVIRONMENT == "dev"

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
    ssl_keyfile = ssl_certfile = None


def start():
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=WEB_PORT,
        reload=is_dev,
        ssl_keyfile=ssl_keyfile,
        ssl_certfile=ssl_certfile,
    )
