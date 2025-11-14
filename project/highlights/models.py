from django.db import models
from pdf_documents.models import originPDF, PDFpage

class Tag(models.Model):
    pdf_id = models.ForeignKey(originPDF, on_delete=models.CASCADE)
    color = models.CharField(max_length=30)
    tag_detail = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.tag_detail}: {self.color}"
    
class Highlight(models.Model):
    pdf_id = models.ForeignKey(originPDF, on_delete=models.CASCADE)
    page_id = models.ForeignKey(PDFpage, on_delete=models.CASCADE)
    Tag_id = models.ForeignKey(Tag, on_delete=models.CASCADE)
    highlight_text = models.TextField()
    highlight_box = models.JSONField()  # { "min_x": ~, "min_y": ~, "max_x": ~, "max_y": ~  }