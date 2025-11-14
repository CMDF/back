# highlights/urls.py
from django.urls import path
from .views import TagListCreateAPIView, TagDetailAPIView, HighlightCreateAPIView, HighlightDetailAPIView

app_name = "highlights"

urlpatterns = [
    path("tags/", TagListCreateAPIView.as_view(), name="tag_list"),
    path("tags/<int:pk>/", TagDetailAPIView.as_view(), name="tag_detail"),
    path("highlight/", HighlightCreateAPIView.as_view(), name="highlight_create"),
    path("highlight/<int:pk>/", HighlightDetailAPIView.as_view(), name="highlight_detail"),
]