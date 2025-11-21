from django.urls import path
from .views import GetFiguresByOriginPDFAPIView

app_name = "pdf_figures"

urlpatterns = [
    path("figures/<int:pdf_id>/", GetFiguresByOriginPDFAPIView.as_view(), name="get_figures_by_origin_pdf"),
]
