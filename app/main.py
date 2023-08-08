import os.path

import uvicorn
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware

from app.schemas import GraphQL, schema

load_dotenv()

ENVIRONMENT = os.environ.get("ENVIRONMENT", "dev")
WEB_PORT = int(os.environ.get("WEB_PORT", 8000))

IS_PROD = ENVIRONMENT == "prod"
IS_DEV = ENVIRONMENT == "dev"

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

ssl_keyfile = "app/config/key.pem"
ssl_certfile = "app/config/cert.pem"
if not (os.path.isfile(ssl_keyfile) and os.path.isfile(ssl_certfile)):
    ssl_keyfile = ssl_certfile = None


def start():
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=WEB_PORT,
        reload=IS_DEV,
        ssl_keyfile=ssl_keyfile,
        ssl_certfile=ssl_certfile,
    )
