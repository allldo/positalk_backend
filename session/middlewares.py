import logging
from urllib.parse import parse_qs

from asgiref.sync import sync_to_async
from channels.auth import AuthMiddleware
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections


logger = logging.getLogger(__name__)
logging.basicConfig(filename='positalk.log', level=logging.INFO)

class TokenAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        close_old_connections()
        scope["user"] = AnonymousUser()
        headers = dict(scope.get("headers", []))
        auth_header = headers.get(b"authorization", b"").decode("utf-8")
        if auth_header.startswith("Token "):
            token_key = auth_header.split("Token ")[1]
            user = await self.get_user_by_token(token_key)
            if user:
                scope["user"] = user
                scope['nickname'] = await database_sync_to_async(user.get_name)()

        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user_by_token(self, token_key):
        try:
            token = Token.objects.get(key=token_key)
            return token.user
        except Token.DoesNotExist:
            return None