from rest_framework import serializers
from .models import Tag, Highlight

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'pdf_id', 'color', 'tag_detail']
        read_only_fields = ['id']

class HighlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Highlight
        fields = ['id', 'page_id', 'start_index', 'Tag_id', 'highlight_text', 'highlight_box']
        read_only_fields = ['id', 'created_at']