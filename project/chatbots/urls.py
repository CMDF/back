from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

app_name = "chatbots"

urlpatterns = [
    path('ask/', ChatBotView.as_view(), name='chat-ask'),
]