from django.urls import path
from highlights.views import *

app_name = "highlights"

urlpatterns = [
    path("tags/", TagAPIView.as_view(), name="tag_api"),
    path("tags/<int:pk>/", TagAPIView.as_view(), name="tag_detail_api"),
]

