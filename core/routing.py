from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/audio/$', consumers.AudioStreamConsumer.as_asgi()),
    re_path(r'ws/send/$', consumers.AudioReceive.as_asgi()),
]