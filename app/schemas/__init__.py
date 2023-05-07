from typing import Any, Optional, Union

import jwt
import strawberry
from starlette import requests, responses, websockets
from strawberry.asgi import GraphQL as _GraphQL

from app import models
from app.schemas import agenda, auth
from app.schemas.schema_types import User


class GraphQL(_GraphQL):
    async def get_context(
        self,
        request: Union[requests.Request, websockets.WebSocket],
        response: Optional[responses.Response] = None,
    ) -> Any:
        return {"user": await self._get_user(request)}

    async def _get_user(
        self,
        request: Union[requests.Request, websockets.WebSocket],
        response: Optional[responses.Response] = None,
    ) -> Optional[auth.User]:
        if not request:
            return None

        authorization = request.headers.get("Authorization", None)
        if authorization is None:
            return None

        payload = jwt.decode(authorization, auth.SECRET, ["HS256"])
        user = (
            await models.User.select()
            .where(models.User.id == int(payload["sub"]))
            .first()
        )
        return User(**user) if user else None


@strawberry.type
class Query(agenda.Query, auth.Query):
    pass


@strawberry.type
class Mutation(agenda.Mutation, auth.Mutation):
    pass


schema = strawberry.Schema(Query, Mutation)
