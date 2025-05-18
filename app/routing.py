from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path("ws/face_recognition/", consumers.FaceRecognitionConsumer.as_asgi()),
]
