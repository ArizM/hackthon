from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/collaboration/(?P<session_id>\d+)/$', consumers.CollaborationConsumer.as_asgi()),
]
