from rest_framework import serializers
from .models import originPDF, PDFpage, MatchedText

class OriginPDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = originPDF
        fields = ['id', 'user_id', 'title', 'S3_url', 'created_at']
        read_only_fields = ['id', 'created_at']


class PDFUploadSerializer(serializers.Serializer):
    title = serializers.CharField(required=False, allow_blank=True)
    file = serializers.FileField()  # multipart/form-data 의 file


class PDFpageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDFpage
        fields = ['id', 'pdf_id', 'page_num', 'text']
        read_only_fields = ['id']


class MatchedTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchedText
        fields = ['id', 'page_id', 'figure_id', 'page_num', 'raw_text', 'matched_text', 'text_box']
        read_only_fields = ['id']

class MatchedTextDataGetSerializer(serializers.ModelSerializer):
    pdf_id = serializers.IntegerField(source='page_id.pdf_id.id', read_only=True)

    class Meta:
        model = MatchedText
        fields = ['id', 'pdf_id', 'page_id', 'figure_id', 'page_num', 'raw_text', 'matched_text']