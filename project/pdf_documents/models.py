from django.db import models
from accounts.models import User
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
        return f"PDF: {self.pdf_id.title} - Page: {self.page_number}"