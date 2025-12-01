from django.db import models
from django.conf import settings
from pdf_documents.models import originPDF  # originPDF 모델 import

class ChatSession(models.Model):
    # 1. 사용자 연결
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_sessions')
    
    # 2. PDF 연결
    # 어떤 PDF에 대한 대화인지 식별합니다. PDF가 삭제되면 대화도 함께 삭제
    origin_pdf = models.ForeignKey(originPDF, on_delete=models.CASCADE, related_name='chat_sessions')
    
    # 3. 메타 데이터 (채팅방 제목, 생성일, 업데이트 날짜)
    title = models.CharField(max_length=200, blank=True, default='New Chat') 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # 한 사용자가 같은 PDF에 대해 여러 개의 채팅방을 만들 수 있다면 유니크 제약이 필요 없지만,
        # "PDF 하나당 하나의 채팅방만 유지"하려면 unique_together를 사용할 수도 있습니다.
        # 여기서는 여러 대화방 생성을 허용하는 구조로 짰습니다.
        ordering = ['-updated_at']

    def __str__(self):
        return f"[{self.origin_pdf.title}] {self.user.username}의 대화"


class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'), # 사용 모델의 특성에 따라 model 대신 assistant로 변경
    ]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.content[:20]}..."