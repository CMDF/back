from django.db import models
from accounts.models import User
from pdf_figures.models import PDFfigure
class originPDF(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    S3_url = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    

class PDFpage(models.Model):
    pdf_id = models.ForeignKey(originPDF, on_delete=models.CASCADE)
    page_num = models.IntegerField()
    text = models.TextField()
    
    def __str__(self):
        return f"PDF: {self.pdf_id.title} - Page: {self.page_num}"
    
class MatchedText(models.Model):
    page_id = models.ForeignKey(PDFpage, on_delete=models.CASCADE)
    figure_id = models.ForeignKey(PDFfigure, on_delete=models.CASCADE)
    page_num = models.IntegerField()
    raw_text = models.TextField()
    matched_text = models.TextField()

    def __str__(self):
        return f"Matched Text on Page: {self.page_id.page_num} for Figure ID: {self.figure_id.id}"