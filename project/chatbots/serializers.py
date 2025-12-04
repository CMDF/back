from rest_framework import serializers

class ChatBotStatelessSerializer(serializers.Serializer):
    pdf_id = serializers.IntegerField(help_text="질문할 PDF 문서의 ID")
    message = serializers.CharField(help_text="사용자의 질문")
    history = serializers.ListField(
        child=serializers.DictField(), 
        required=False, 
        help_text="이전 대화 목록 (예: [{'role': 'user', 'content': '...'}])"
    )