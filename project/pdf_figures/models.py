from django.db import models
from pdf_documents.models import PDFpage

class PDFfigure(models.Model):
    page_id = models.ForeignKey(PDFpage, on_delete=models.CASCADE)
    figure_type = models.CharField(max_length=50)
    figure_box = models.JSONField()  # { "min_x": ~, "min_y": ~, "max_x": ~, "max_y": ~  }

    def __str__(self):
        return f"Figure on Page: {self.page_id.page_num} - Type: {self.figure_type}"