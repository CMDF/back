# highlights/urls.py
from django.urls import path
from .views import TagListCreateAPIView, TagDetailAPIView

app_name = "highlights"

urlpatterns = [
    path("tags/", TagListCreateAPIView.as_view(), name="tag_list"),
    path("tags/<int:pk>/", TagDetailAPIView.as_view(), name="tag_detail"),
]