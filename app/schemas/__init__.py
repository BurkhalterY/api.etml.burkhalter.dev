from typing import Any, Optional, Union

import jwt
import strawberry
from starlette import requests, responses, websockets
from strawberry.asgi import GraphQL as _GraphQL

from app.models import User
from app.schemas import agenda, auth, types, user


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
    ) -> Optional[types.User]:
        if not request:
            return None

        authorization = request.headers.get("Authorization", None)
        if authorization is None:
            return None

        payload = jwt.decode(authorization, auth.SECRET, ["HS256"])
        user = await User.select().where(User.id == int(payload["sub"])).first()
        return (
            types.User(
                id=user["id"],
                first_name=user["first_name"],
                last_name=user["last_name"],
                email=user["email"],
                admin=user["admin"],
            )
            if user
            else None
        )


@strawberry.type
class Query(agenda.Query, auth.Query, user.Query):
    pass


@strawberry.type
class Mutation(agenda.Mutation, auth.Mutation):
    pass


schema = strawberry.Schema(Query, Mutation)
