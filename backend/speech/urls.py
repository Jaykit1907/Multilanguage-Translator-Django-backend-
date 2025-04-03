from django.urls import path
from .views import generate_speech

urlpatterns = [
    path("speech/", generate_speech, name="generate_speech"),
]
