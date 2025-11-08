from django.db import models
from pdf_documents.models import originPDF

class Tag(models.Model):
    pdf_id = models.ForeignKey(originPDF, on_delete=models.CASCADE)
    color = models.CharField(max_length=30)
    tag_detail = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.tag_detail}: {self.color}"