from django.urls import path
from pdf_documents.views import *

app_name = "pdf_documents"

urlpatterns = [
    path('upload/', PDFUploadView.as_view(), name='pdf-upload'),
    path('delete/<int:id>/', PDFDeleteView.as_view(), name='pdf-delete'),
    path("pdfs/<int:pdf_id>/ocr/", PDFwithOCRView.as_view(), name="pdf-ocr"),
    path("pdfs/<int:pdf_id>/matched-texts/", MatchedTextListView.as_view(), name="pdf-matched-texts"),
    path("pdfs/<int:pdf_id>", OriginPDFGetView.as_view(), name="pdf-origin-get"),
    path("pdfs/<int:pdf_id>/pages/", PDFpageGetView.as_view(), name="pdf-pages-get"),
]