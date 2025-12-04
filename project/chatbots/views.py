import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from openai import OpenAI
from pdf_documents.models import originPDF # PDF 검색을 위해 필요
from django.conf import settings
from .serializers import ChatBotStatelessSerializer

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

UPSTAGE_API_KEY = settings.UPSTAGE_API_KEY

class ChatBotView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Stateless 챗봇 대화 요청",
        operation_description="DB에 저장하지 않고, 클라이언트가 보낸 history를 기반으로 답변합니다.",
        tags=["ChatBots"],
        security=[{"Bearer": []}],
        request_body=ChatBotStatelessSerializer, 
        responses={200: "성공 (reply 반환)"}
    )
    def post(self, request):
        # 1. 클라이언트로부터 데이터 수신
        # iOS가 'history'라는 리스트에 이전 대화를 담아서 보내줘야 함
        # 예: [{"role": "user", "content": "안녕"}, {"role": "assistant", "content": "반가워"}]
        history = request.data.get('history', []) 
        user_message = request.data.get('message')
        pdf_id = request.data.get('pdf_id')

        if not user_message or not pdf_id:
            return Response({"error": "메시지와 PDF ID는 필수입니다."}, status=400)

        # 2. PDF 존재 확인 (RAG 검색 대상)
        pdf = get_object_or_404(originPDF, id=pdf_id)

        try:
            client = OpenAI(
                api_key=UPSTAGE_API_KEY,
                base_url="https://api.upstage.ai/v1/solar"
            )

            # ---------------------------------------------------------
            # [RAG 로직] - 저장된 PDF 내용 검색
            # user_message와 관련된 내용을 pdf_id에 해당하는 벡터 DB/MatchedText에서 찾음
            # ---------------------------------------------------------
            rag_context = "" # (여기에 검색 로직 구현)
            
            system_prompt = f"""
            문서 '{pdf.title}'에 기반하여 답변하세요.
            [참고 문맥]: {rag_context}
            """

            # 3. 메시지 구성 (System + History + Current Message)
            messages_payload = [{"role": "system", "content": system_prompt}]
            
            # iOS가 보내준 이전 대화 기록을 그대로 AI에게 전달
            # (단, 신뢰할 수 없는 데이터일 수 있으므로 포맷 검증은 필요할 수 있음)
            messages_payload.extend(history)
            
            # 현재 질문 추가
            messages_payload.append({"role": "user", "content": user_message})

            # 4. AI 호출
            response = client.chat.completions.create(
                model="solar-1-mini-chat",
                messages=messages_payload
            )

            bot_reply = response.choices[0].message.content

            # 5. 응답 반환 (저장 없이 바로 리턴)
            return Response({
                "reply": bot_reply,
                "status": "success"
            }, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)