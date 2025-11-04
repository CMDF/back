from django.urls import path
from . import views

app_name = "pdf_figures"

urlpatterns = [
    # 준비가 안 됐다면 일단 빈 리스트도 OK
    # path("", views.some_view, name="index"),
]
