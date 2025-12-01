from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

app_name = "chatbots"
router = DefaultRouter()
router.register(r'sessions', ChatSessionViewSet, basename='session')
urlpatterns = [
    # 1. 채팅방 관리 (Router)
    # GET  /chatbots/sessions/       : 내 채팅방 목록 조회
    # POST /chatbots/sessions/       : 새 채팅방 생성 (body: {"pdf_id": 1})
    # DEL  /chatbots/sessions/{id}/  : 채팅방 삭제
    path('', include(router.urls)),

    # 2. 메시지 전송 (Blocking 방식)
    # POST /chatbots/sessions/{session_id}/message/
    # - 사용자가 메시지를 보내고, AI 응답이 올 때까지 기다렸다가 한 번에 받습니다.
    path('sessions/<int:session_id>/message/', ChatMessageView.as_view(), name='chat-message'),

    # 3. 대화 내역 조회 (History)
    # GET /chatbots/sessions/{session_id}/history/
    # - 채팅방에 들어갔을 때 과거 대화 내용을 불러옵니다.
    path('sessions/<int:session_id>/history/', ChatHistoryView.as_view(), name='chat-history'),
]