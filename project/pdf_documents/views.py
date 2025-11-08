# pdf_documents/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from django.conf import settings
from botocore.exceptions import ClientError
import boto3
import os
import uuid

from .serializers import OriginPDFSerializer
from .models import originPDF

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class PDFUploadView(APIView):
    # ★ multipart/form-data 파싱 필수
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_summary="PDF 업로드",
        operation_description=(
            "S3로 PDF를 업로드하고 메타데이터(DB)에 저장합니다.\n\n"
            "- Content-Type: multipart/form-data\n"
            "- 필드: `title`(text), `file`(file)\n"
            "- 인증: Authorization: Bearer <access_token>"
        ),
        tags=["PDF Documents"],
        security=[{"Bearer": []}],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["file"],
            properties={
                "title": openapi.Schema(type=openapi.TYPE_STRING, description="제목", example="중간보고서"),
                # drf_yasg에서 파일은 다음과 같이 표기
                "file": openapi.Schema(type=openapi.TYPE_STRING, format="binary", description="PDF 파일"),
            },
        ),
        responses={
            201: openapi.Response("Created", schema=OriginPDFSerializer),
            400: "잘못된 요청(파일 누락 등)",
            403: "권한/버킷 정책 문제로 S3 업로드 실패",
            500: "서버 오류(DB 저장 실패 등)",
        },
    )
    def post(self, request, *args, **kwargs):
        # 1) 입력 검증
        file_obj = request.FILES.get('file', None)
        title = request.data.get('title', '')

        if not file_obj:
            return Response(
                {"detail": "파일이 첨부되지 않았습니다. form-data에서 key를 'file'로 보내세요."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2) S3 클라이언트 (settings에서 일관되게 가져오기)
        s3 = boto3.client(
            "s3",
            region_name=settings.AWS_REGION,                # ← settings.py에서 정의한 AWS_REGION 사용
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

        bucket = settings.AWS_STORAGE_BUCKET_NAME
        # 파일명 충돌 방지: 원본 확장자는 유지
        ext = os.path.splitext(file_obj.name)[1] or ".pdf"
        key = f"pdfs/{uuid.uuid4().hex}{ext}"

        # 업로드 옵션 (브라우저 열람/다운로드에 유용)
        extra_args = {"ContentType": file_obj.content_type or "application/pdf"}

        # (버킷 정책에서 SSE-KMS를 강제한다면 주석 해제하고 KMS 키 지정)
        # extra_args.update({
        #     "ServerSideEncryption": "aws:kms",
        #     "SSEKMSKeyId": "<KMS 키 ARN 또는 별칭>"
        # })

        try:
            # 3) 업로드
            s3.upload_fileobj(
                Fileobj=file_obj,
                Bucket=bucket,
                Key=key,
                ExtraArgs=extra_args,
            )
        except ClientError as e:
            # AccessDenied 등 S3에서 바로 떨어지는 에러를 사용자에게 명확히 반환
            code = e.response.get("Error", {}).get("Code")
            msg = e.response.get("Error", {}).get("Message")
            return Response(
                {
                    "detail": "S3 업로드에 실패했습니다.",
                    "error_code": code,
                    "error_message": msg,
                    "hint": "IAM 정책/버킷 정책/KMS 강제 여부를 확인하세요."
                },
                status=status.HTTP_403_FORBIDDEN if code in ("AccessDenied",) else status.HTTP_502_BAD_GATEWAY
            )
        except Exception as e:
            return Response(
                {"detail": f"S3 업로드 중 알 수 없는 오류: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # 4) 접근 URL (리전 포함 커스텀 도메인 사용)
        # settings.py: AWS_S3_CUSTOM_DOMAIN = f"{bucket}.s3.{AWS_REGION}.amazonaws.com"
        s3_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{key}"

        # 5) DB 저장
        try:
            origin_pdf = originPDF.objects.create(
                user_id=request.user,   # IsAuthenticated 전제. 비로그인 접근이면 FK 오류 가능
                title=title,
                S3_url=s3_url
            )
        except Exception as e:
            # DB 실패 시, 업로드된 객체를 정리하고 싶다면 아래 주석 해제(선택)
            # try:
            #     s3.delete_object(Bucket=bucket, Key=key)
            # except Exception:
            #     pass
            return Response(
                {"detail": f"DB 저장에 실패했습니다: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # 6) 응답
        serializer = OriginPDFSerializer(origin_pdf)
        return Response(serializer.data, status=status.HTTP_201_CREATED)