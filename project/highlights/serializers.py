from rest_framework import serializers
from .models import Tag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'pdf_id', 'color', 'tag_detail']
        read_only_fields = ['id']