from django.urls import path
from pdf_documents.views import *

app_name = "pdf_documents"

urlpatterns = [
    path('upload/', PDFUploadView.as_view(), name='pdf-upload'),
    path("pdfs/<int:pdf_id>/ocr/", PDFwithOCRView.as_view(), name="pdf-ocr"),
    path("pdfs/<int:pdf_id>/matched-texts/", MatchedTextListView.as_view(), name="pdf-matched-texts"),
]