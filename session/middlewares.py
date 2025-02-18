from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from django.db import close_old_connections
from channels.db import database_sync_to_async

class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        close_old_connections()
        scope["user"] = AnonymousUser()

        query_string = scope.get("query_string", b"").decode()
        token_key = self.get_token_from_query(query_string)

        if token_key:
            user = await self.get_user_by_token(token_key)
            if user:
                scope["user"] = user

        return await super().__call__(scope, receive, send)

    def get_token_from_query(self, query_string):
        params = dict(param.split("=") for param in query_string.split("&") if "=" in param)
        return params.get("token")

    @database_sync_to_async
    def get_user_by_token(self, token_key):
        try:
            return Token.objects.get(key=token_key).user
        except Token.DoesNotExist:
            return None
