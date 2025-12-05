import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from openai import OpenAI
from pdf_documents.models import originPDF # PDF 검색을 위해 필요
from django.conf import settings
from .serializers import ChatRequestSerializer, SelectedTextSerializer
from pdf_documents.models import originPDF, MatchedText
from highlights.models import Highlight

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

UPSTAGE_API_KEY = settings.UPSTAGE_API_KEY

class ChatBotView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="챗봇에게 질문하기 (RAG + Stateless)",
        operation_description="""
        사용자의 질문과 참고 자료(이미지 ID, 하이라이트 ID, 선택 텍스트)를 받아 AI 답변을 생성합니다.
        서버에 대화 내용을 저장하지 않으므로, 이전 대화 목록(history)을 매번 함께 보내야 합니다.
        """,
        tags=["ChatBot"],
        # 1. 요청 Body: 우리가 만든 ChatRequestSerializer 연결
        request_body=ChatRequestSerializer,
        
        # 2. 응답 Schema: 성공 시 반환되는 JSON 구조 정의
        responses={
            200: openapi.Response(
                description="AI 응답 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'reply': openapi.Schema(type=openapi.TYPE_STRING, description="AI의 답변 텍스트"),
                        'status': openapi.Schema(type=openapi.TYPE_STRING, description="성공 여부 (success)")
                    }
                )
            ),
            400: "잘못된 요청 (필수 필드 누락 등)",
            404: "PDF 문서가 존재하지 않음",
            500: "AI 서비스 호출 실패 또는 서버 에러"
        }
    )
    def post(self, request):
        # 1. 클라이언트로부터 데이터 수신
        # request 요청 형식
        # { question: "문자열로 질문자의 query가 들어옴", figure_ids[int]: "사용자가 질문 또는 지식으로 사용하려는 피규어 아이디 목록",
        # highlight_ids[int]: "사용자가 질문 또는 지식으로 사용하려는 하이라이트 아이디 목록",
        # selected_texts[dict]: { "text": "사용자가 질문 또는 지식으로 사용하기 위한 텍스트들", "page_id": int 해당 텍스트가 속한 페이지 아이디} }

        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = serializer.validated_data
        
        pdf_id = data['pdf_id']
        question = data['question']
        
        # iOS에서 보낸 ID 리스트
        figure_ids = data['figure_ids']       # 예: [10, 12] (PDFFigure의 ID들)
        highlight_ids = data['highlight_ids']
        selected_texts = data['selected_texts']

        # PDF 존재 확인
        pdf = get_object_or_404(originPDF, id=pdf_id)

        context_parts = []

        # (A) Figure IDs 처리 (MatchedText 조회)
        # 사용자가 선택한 Figure ID를 외래키로 가지고 있는 MatchedText를 찾습니다.
        if figure_ids:
            # MatchedText 모델의 figure_id 필드가 figure_ids 리스트 안에 있는 경우를 필터링
            matched_records = MatchedText.objects.filter(figure_id__in=figure_ids)
            
            for record in matched_records:
                # 사용자의 의도대로 'raw_text'를 가져옴
                text_content = record.raw_text 
                page_num = record.page_num
                
                # figure_type은 MatchedText -> PDFfigure 관계를 통해 가져옴
                fig_type = record.figure_id.figure_type 
                
                context_parts.append(f"[참고 할만한 figure의 타입 및 지정 페이지와 관련 텍스트 내용 ({fig_type}, Page {page_num})]: {text_content}")

        # (B) Highlight IDs 처리
        if highlight_ids:
            highlights = Highlight.objects.filter(id__in=highlight_ids)
            for hl in highlights:
                tag_info = hl.Tag_id.tag_detail if hl.Tag_id else "No Tag"
                context_parts.append(f"[하이라이트한 내용 (Tag: {tag_info}, Page {hl.page_id.page_num})]: {hl.highlight_text}")

        # (C) Selected Texts 처리
        if selected_texts:
            for item in selected_texts:
                context_parts.append(f"[사용자 선택 텍스트 (Page {item['page_id']})]: {item['text']}")

        # 문맥 합치기
        prompt_context = "\n\n".join(context_parts)

        # =========================================================
        # [AI Prompting]
        # =========================================================
        
        base_prompt = f"당신은 문서 '{pdf.title}'에 대해 질문에 답변하는 AI 비서입니다. 한국어로 답변해야 합니다. 유저가 질문한 내용을 바탕으로 답변해야하며, 참고자료가 있다면 해당 내용을 토대로 설명해야 합니다."
        
        if prompt_context:
            system_prompt = f"""
            {base_prompt}
            사용자가 질문과 함께 아래의 [참고 자료]를 제공했습니다.
            해당 자료 내용을 최우선으로 참고하여 답변하세요.
            
            [참고 자료]
            {prompt_context}
            """
        else:
            system_prompt = f"{base_prompt} 문서의 내용을 바탕으로 답변하세요."

        try:
            client = OpenAI(
                api_key=UPSTAGE_API_KEY,
                base_url="https://api.upstage.ai/v1/solar"
            )

            # 메시지 구성
            messages_payload = [{"role": "system", "content": system_prompt}]
            messages_payload.append({"role": "user", "content": question})

            # AI 호출
            response = client.chat.completions.create(
                model="solar-pro",
                messages=messages_payload
            )

            bot_reply = response.choices[0].message.content

            return Response({
                "reply": bot_reply,
                "status": "success"
            }, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)