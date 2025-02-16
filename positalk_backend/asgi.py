"""
ASGI config for positalk_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'positalk_backend.settings')
django.setup()
from session.middlewares import TokenAuthMiddleware

from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application
from session.routing import websocket_urlpatterns
from channels.routing import URLRouter


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": TokenAuthMiddleware(
        URLRouter(websocket_urlpatterns)
    ),
})