from rest_framework import serializers
from .models import ChatSession, ChatMessage
from pdf_documents.models import originPDF

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'content', 'created_at']

class ChatSessionSerializer(serializers.ModelSerializer):
    # PDF 제목 등을 함께 보여주기 위해 ReadOnlyField 사용
    pdf_title = serializers.ReadOnlyField(source='origin_pdf.title')
    
    class Meta:
        model = ChatSession
        fields = ['id', 'origin_pdf', 'pdf_title', 'title', 'created_at', 'updated_at']
        read_only_fields = ['user', 'title'] # 제목은 자동 생성하거나 나중에 수정

class ChatSessionCreateSerializer(serializers.Serializer):
    # 채팅방 생성 시 pdf_id만 받으면 됨
    pdf_id = serializers.IntegerField()