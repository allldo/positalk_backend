from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from django.db import close_old_connections
from channels.db import database_sync_to_async
import logging

logger = logging.getLogger(__name__)

class TokenAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        close_old_connections()
        scope["user"] = AnonymousUser()
        headers = dict(scope.get("headers", []))

        # Проверяем заголовок `Sec-WebSocket-Protocol`
        subprotocol = headers.get(b"sec-websocket-protocol", b"").decode("utf-8")

        if subprotocol.startswith("Token "):
            token_key = subprotocol.split("Token ")[1]
            user = await self.get_user_by_token(token_key)

            if user:
                scope["user"] = user
                scope['nickname'] = await database_sync_to_async(user.get_name)()
                logger.info(f"nickname: {scope['nickname']}")
            else:
                logger.warning(f"Invalid token: {token_key}")
                await send({"type": "websocket.close"})
                return

        async def send_with_protocol(message):
            if message["type"] == "websocket.accept":
                message["subprotocol"] = subprotocol
            await send(message)

        return await super().__call__(scope, receive, send_with_protocol)

    @database_sync_to_async
    def get_user_by_token(self, token_key):
        try:
            token = Token.objects.get(key=token_key)
            return token.user
        except Token.DoesNotExist:
            return None
