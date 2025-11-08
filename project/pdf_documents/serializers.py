from rest_framework import serializers
from .models import originPDF

class OriginPDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = originPDF
        fields = ['id', 'user_id', 'title', 'S3_url', 'created_at']
        read_only_fields = ['id', 'created_at']


class PDFUploadSerializer(serializers.Serializer):
    title = serializers.CharField(required=False, allow_blank=True)
    file = serializers.FileField()  # multipart/form-data 의 file