import os

import uvicorn
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import PlainTextResponse
from starlette.routing import Route, WebSocketRoute

from app.schemas import GraphQL, schema

async def status(request):
    return PlainTextResponse("OK")

load_dotenv()

ENVIRONMENT = os.environ.get("ENVIRONMENT", "dev")
WEB_PORT = int(os.environ.get("WEB_PORT", 8000))

IS_PROD = ENVIRONMENT == "prod"
IS_DEV = ENVIRONMENT == "dev"

graphql_app = GraphQL(schema) #, graphiql=IS_DEV)
app = Starlette(
    routes=[
        Route("/status", status),
        Route("/graphql", graphql_app),
        WebSocketRoute("/graphql", graphql_app),
    ],
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]
)


def start():
    uvicorn.run("app.main:app", host="0.0.0.0", port=WEB_PORT, reload=IS_DEV)
