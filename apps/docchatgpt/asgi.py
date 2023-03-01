import os

from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing 

debug_status = os.getenv('DEBUG', 'False') == 'True'
#debugging only happens locally, so if debug is true, then use settings, otherwise use prod settings
if debug_status:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bmt_gpt.settings')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bmt_gpt.settings_production')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    ' websocket': AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    )
})