from rest_framework import serializers
from .models import PDFfigure

class PDFfigureSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDFfigure
        fields = ['id', 'page_id', 'figure_type', 'figure_box']