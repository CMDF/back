import os
from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404
from openai import OpenAI
from django.conf import settings

from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, ChatMessageSerializer, ChatSessionCreateSerializer
from pdf_documents.models import originPDF

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


# Upstage API 키 설정
UPSTAGE_API_KEY = settings.UPSTAGE_API_KEY

# 1. 채팅방(Session) 관리 ViewSet
# 용도: 채팅방 목록 조회, 채팅방 생성, 삭제
class ChatSessionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSessionSerializer

    def get_queryset(self):
        # 내 채팅방만 보여주기
        return ChatSession.objects.filter(user=self.request.user)


    # 1. 목록 조회 (LIST) 문서화
    @swagger_auto_schema(
        operation_summary="내 채팅방 목록 조회",
        operation_description="현재 로그인한 사용자가 생성한 모든 채팅방 목록을 반환합니다.",
        responses={200: ChatSessionSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # 2. 생성 (CREATE) 문서화 - 여기가 가장 중요합니다!
    @swagger_auto_schema(
        operation_summary="새 채팅방 생성",
        operation_description="PDF ID를 입력받아 새로운 채팅 세션을 생성합니다.",
        # Request Body는 'ChatSessionCreateSerializer' (pdf_id만 입력)
        request_body=ChatSessionCreateSerializer,
        # Response는 'ChatSessionSerializer' (방 정보 전체 반환)
        responses={
            201: ChatSessionSerializer,
            400: "잘못된 요청 (PDF ID 누락 등)",
            404: "해당 PDF를 찾을 수 없음"
        }
    )
    def create(self, request, *args, **kwargs):
        # PDF ID를 받아 채팅방 생성
        serializer = ChatSessionCreateSerializer(data=request.data)
        if serializer.is_valid():
            pdf_id = serializer.validated_data['pdf_id']
            pdf = get_object_or_404(originPDF, id=pdf_id) # 권한 체크 로직 추가 권장 (내 PDF인지)
            
            # 이미 존재하는 방이 있다면 리턴하거나 새로 생성 (여기서는 새로 생성)
            session = ChatSession.objects.create(
                user=request.user,
                origin_pdf=pdf,
                title=f"{pdf.title} - 대화"
            )
            return Response(ChatSessionSerializer(session).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # 3. 삭제 (DESTROY) 문서화
    @swagger_auto_schema(
        operation_summary="채팅방 삭제",
        operation_description="특정 채팅방을 삭제합니다. (대화 내용도 함께 삭제됩니다)",
        responses={204: "삭제 성공"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


# 2. 메시지 전송 View
class ChatMessageView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, description='사용자 메시지 내용'),
            },
            required=['message']
        ),
        tags=['Chat'],
        responses={ 200: 'chat message 전송 성공', 400: 'error": "메시지를 입력해주세요.', 500: '서버 오류'}
    )
    def post(self, request, session_id):
        # 1. 데이터 수신 및 검증
        user_message = request.data.get('message')
        if not user_message:
            return Response({"error": "메시지를 입력해주세요."}, status=400)

        # 2. 세션 확인 (내 세션인지)
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)

        try:
            # 3. Upstage API 클라이언트 준비
            client = OpenAI(
                api_key=UPSTAGE_API_KEY,
                base_url="https://api.upstage.ai/v1/solar"
            )

            # 4. 문맥(Context) 구성
            # (RAG 로직이 들어갈 자리: 여기서 검색된 텍스트를 system_prompt에 추가)
            rag_context = "" 

            system_prompt = f"""
            문서 '{session.origin_pdf.title}'에 대한 질문에 답변해 주세요.
            [참고 텍스트]: {rag_context}
            """

            # 이전 대화 기록 (History) 가져오기
            history_msgs = ChatMessage.objects.filter(session=session).order_by('created_at')[:10]
            
            messages = [{"role": "system", "content": system_prompt}]
            for msg in history_msgs:
                role = 'assistant' if msg.role == 'model' or msg.role == 'assistant' else 'user'
                messages.append({"role": role, "content": msg.content})
            
            # 현재 질문 추가
            messages.append({"role": "user", "content": user_message})

            # 5. API 호출 (Blocking)
            # stream=True 옵션을 뺍니다 (기본값이 False)
            response = client.chat.completions.create(
                model="solar-1-mini-chat",
                messages=messages
            )

            # 6. 응답 추출 (기다렸다가 한 번에 받음)
            bot_reply = response.choices[0].message.content

            # 7. DB 저장
            # (순서대로 저장)
            user_msg_obj = ChatMessage.objects.create(session=session, role='user', content=user_message)
            bot_msg_obj = ChatMessage.objects.create(session=session, role='assistant', content=bot_reply)

            # 8. 결과 반환 (JSON)
            # iOS 개발자는 이 JSON을 받아서 화면에 뿌리기만 하면 됩니다.
            return Response({
                "user_message": ChatMessageSerializer(user_msg_obj).data,
                "bot_reply": ChatMessageSerializer(bot_msg_obj).data,
                "status": "success"
            }, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)

# 3. 특정 채팅방의 메시지 내역 조회 View
class ChatHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=None,
        tags=['Chat'],
        responses={200: ChatMessageSerializer(many=True)}
    )
    def get(self, request, session_id):
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        messages = ChatMessage.objects.filter(session=session).order_by('created_at')
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)