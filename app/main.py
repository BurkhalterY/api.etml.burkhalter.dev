import uvicorn
from strawberry.asgi import GraphQL

from app.schemas import schema

app = GraphQL(schema)


def start():
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
