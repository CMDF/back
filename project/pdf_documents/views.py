# pdf_documents/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
import requests
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from django.conf import settings
from botocore.exceptions import ClientError
import boto3
import os
import uuid
import json

from .serializers import OriginPDFSerializer, PDFUploadSerializer, MatchedTextDataGetSerializer
from .models import originPDF, PDFpage, MatchedText

from pdf_figures.serializers import PDFfigureSerializer
from pdf_figures.models import PDFfigure

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class PDFUploadView(APIView):
    # ★ multipart/form-data 파싱 필수
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_summary="PDF 업로드",
        operation_description=(
            "S3로 PDF를 업로드하고 메타데이터(DB)에 저장합니다.\n"
            "- Content-Type: multipart/form-data\n"
            "- 필드: `title`(text), `file`(file)\n"
            "- 인증: Authorization: Bearer <access_token>"
        ),
        tags=["PDF Documents"],
        security=[{"Bearer": []}],
        consumes=["multipart/form-data"],
        request_body=PDFUploadSerializer,
        responses={201: OriginPDFSerializer, 400: "잘못된 요청", 403: "권한/버킷", 500: "서버 오류"},
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
                S3_url=s3_url,
                s3_key=key
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
    

class PDFwithOCRView(APIView):
    """
    특정 originPDF(pdf_id)에 대해:
    1) S3 presigned URL 생성
    2) OCR 서버 호출
    3) pages / figures / matches 를 DB에 저장
    """
    @swagger_auto_schema(
        operation_summary="PDF OCR 처리 및 DB 저장",
        operation_description=(
            "지정한 PDF에 대해 S3 presigned URL을 생성하고 OCR 서버에 전달하여\n"
            "분석된 결과를 pages, figures, matches 테이블에 저장합니다.\n"
            "- 인증: Authorization: Bearer <access_token>"
        ),
        tags=["PDF Documents"],
        responses = {
            201: openapi.Response("description='OCR 처리 및 DB 저장 완료'", schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, description='상세 메시지'),
                    'pdf_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='처리된 PDF ID'),
                    'pages_created': openapi.Schema(type=openapi.TYPE_INTEGER, description='생성된 페이지 수'),
                    'figures_created': openapi.Schema(type=openapi.TYPE_INTEGER, description='생성된 그림 수'),
                }
            )),
        }
    )
    def post(self, request, pdf_id, *args, **kwargs):
        # 0) originPDF 조회
        try:
            origin_pdf = originPDF.objects.get(id=pdf_id, user_id=request.user)
        except originPDF.DoesNotExist:
            return Response(
                {"detail": "해당 PDF를 찾을 수 없거나 권한이 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )

        # s3_key 필수 체크
        if not origin_pdf.s3_key:
            return Response(
                {"detail": "해당 PDF에는 s3_key가 저장되어 있지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        bucket = settings.AWS_STORAGE_BUCKET_NAME
        key = origin_pdf.s3_key

        # 1) S3 클라이언트 및 presigned URL 생성
        try:
            s3 = boto3.client(
                "s3",
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )

            presigned_url = s3.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": bucket, "Key": key},
                ExpiresIn=300,  # 5분
            )
        except Exception as e:
            return Response(
                {"detail": f"Presigned URL 생성 중 오류: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # 2) OCR 서버 호출
        ocr_endpoint = settings.OCR_SERVER  # secrets.json → settings에 로드되어 있다고 가정

        payload = {
            "file_url": presigned_url,
            "timeout": 120,
        }

        try:
            ocr_response = requests.post(
                ocr_endpoint,
                json=payload,
                timeout=180,
            )
            ocr_response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return Response(
                {"detail": f"OCR 서버 요청 실패: {e}"},
                status=status.HTTP_502_BAD_GATEWAY
            )

        try:
            data = ocr_response.json()
        except ValueError:
            return Response(
                {"detail": "OCR 서버에서 유효한 JSON 응답을 받지 못했습니다."},
                status=status.HTTP_502_BAD_GATEWAY
            )

        # if ocr_response.status_code != 200:
        #     return Response(
        #         {
        #             "detail": "OCR 서버가 요청을 처리하지 못했습니다.",
        #             "ocr_status": ocr_response.status_code,
        #             "ocr_raw": ocr_response.text,   # 여기에 서버 에러 메시지 그대로 찍힘
        #         },
        #         status=status.HTTP_502_BAD_GATEWAY
        #     )

        # ✅ 1) 200, 201 둘 다 성공으로 취급
        if ocr_response.status_code not in (200, 201):
            return Response(
                {
                    "detail": "OCR 서버가 요청을 처리하지 못했습니다.",
                    "ocr_status": ocr_response.status_code,
                    "ocr_raw": ocr_response.text,
                },
                status=status.HTTP_502_BAD_GATEWAY
            )

        # ✅ 2) 첫 번째 파싱 (여기서 str 이 나옴)
        try:
            data = ocr_response.json()
        except ValueError:
            return Response(
                {
                    "detail": "OCR 서버에서 JSON이 아닌 응답을 받았습니다.",
                    "ocr_raw": ocr_response.text,
                },
                status=status.HTTP_502_BAD_GATEWAY
            )

        # ✅ 3) OCR 서버가 JSON 문자열을 한 번 더 감싸서 보내므로,
        #      str 이면 한 번 더 json.loads() 해서 dict 로 만든다
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except ValueError:
                return Response(
                    {
                        "detail": "OCR 서버에서 이중 인코딩된 JSON 문자열을 받았지만 파싱에 실패했습니다.",
                        "parsed_data_preview": data[:200],
                    },
                    status=status.HTTP_502_BAD_GATEWAY
                )

        # ✅ 4) 최종적으로 dict 가 아니면 에러
        if not isinstance(data, dict):
            return Response(
                {
                    "detail": "OCR 서버에서 예상치 못한 JSON 형식(객체가 아님)을 받았습니다.",
                    "parsed_type": str(type(data)),
                },
                status=status.HTTP_502_BAD_GATEWAY
            )

        # 3) DB 저장 (pages → figures → matches), 한 트랜잭션으로 처리
        with transaction.atomic():
            # 이미 기존 OCR 결과가 있다면 정리하고 다시 넣고 싶다면 아래 주석 해제
            # MatchedText → PDFfigure → PDFpage 순으로 삭제
            # MatchedText.objects.filter(page_id__pdf_id=origin_pdf).delete()
            # PDFfigure.objects.filter(page_id__pdf_id=origin_pdf).delete()
            # PDFpage.objects.filter(pdf_id=origin_pdf).delete()

            # 3-1) pages 저장
            page_objs = {}  # page_num → PDFpage 인스턴스
            for p in data.get("pages", []):
                page_num = p.get("page_num")
                text = p.get("text", "")

                if page_num is None:
                    continue

                page_obj = PDFpage.objects.create(
                    pdf_id=origin_pdf,
                    page_num=page_num,
                    text=text,
                )
                page_objs[page_num] = page_obj

            # 3-2) figures 저장 + (figure_page_num, figure_box) → PDFfigure 매핑
            figure_map = {}  # (page_num, tuple(original_box)) → PDFfigure

            for f in data.get("figures", []):
                page_num = f.get("page_num")
                figure_type = f.get("figure_type", "")
                box_list = f.get("figure_box", [])

                if page_num is None or page_num not in page_objs:
                    continue

                page_obj = page_objs[page_num]

                # 모델의 주석엔 dict 형태 예시가 있어서, list → dict 변환 (원하면 그대로 list 저장해도 됨)
                if isinstance(box_list, list) and len(box_list) == 4:
                    figure_box = {
                        "min_x": box_list[0],
                        "min_y": box_list[1],
                        "max_x": box_list[2],
                        "max_y": box_list[3],
                    }
                else:
                    figure_box = box_list

                figure_obj = PDFfigure.objects.create(
                    page_id=page_obj,
                    figure_type=figure_type,
                    figure_box=figure_box,
                )

                # matches 에서는 원래 list 형태가 오므로, key 는 원본 list 기준으로 tuple 처리
                if isinstance(box_list, list):
                    figure_map[(page_num, tuple(box_list))] = figure_obj

            # 3-3) matches → MatchedText 저장
            for m in data.get("matches", []):
                text_page_num = m.get("page_num")       # 텍스트 페이지 번호
                figure_page_num = m.get("figure_page")  # 그림이 있는 페이지 번호
                box_list = m.get("figure_box", [])

                if text_page_num not in page_objs:
                    # 해당 텍스트 페이지가 없으면 스킵
                    continue

                page_obj = page_objs[text_page_num]

                # figure_obj = None
                # if figure_page_num is not None and isinstance(box_list, list):
                #     figure_obj = figure_map.get((figure_page_num, tuple(box_list)))
                figure_obj = None
                if figure_page_num is not None and isinstance(box_list, list):
                    key = tuple(box_list)
                    figure_obj = (
                        figure_map.get((figure_page_num, key)) or        # 0-based일 가능성
                        figure_map.get((figure_page_num + 1, key)) or    # 1-based일 가능성
                        figure_map.get((figure_page_num - 1, key))       # 안전빵 백업
                    )

                # figure_id 가 null 허용이 아니므로 못 찾으면 스킵
                if figure_obj is None:
                    continue

                raw_text_list = m.get("raw_text", [])
                figure_text_list = m.get("figure_text", [])

                if isinstance(raw_text_list, list):
                    raw_text = " ".join(raw_text_list)
                else:
                    raw_text = str(raw_text_list)

                if isinstance(figure_text_list, list):
                    matched_text = " ".join(figure_text_list)
                else:
                    matched_text = str(figure_text_list)

                MatchedText.objects.create(
                    page_id=page_obj,
                    figure_id=figure_obj,
                    page_num=text_page_num,
                    raw_text=raw_text,
                    matched_text=matched_text,
                )

        # 4) 최종 응답 (필요하면 counts 나 상세 serializer 로 바꿔도 됨)
        return Response(
            {
                "detail": "OCR 처리 및 DB 저장이 완료되었습니다.",
                "pdf_id": origin_pdf.id,
                "pages_created": len(page_objs),
                "figures_created": len(figure_map),
                "matches_created": MatchedText.objects.filter(page_id__pdf_id=origin_pdf).count(),
            },
            status=status.HTTP_201_CREATED
        )
    
class MatchedTextListView(APIView):
    """
    특정 originPDF(pdf_id)에 대한 MatchedText 목록 조회
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="PDF의 MatchedText 목록 조회",
        operation_description=(
            "지정한 PDF에 대해 MatchedText 항목들의 목록을 조회합니다.\n"
            "- 인증: Authorization: Bearer <access_token>"
        ),
        tags=["PDF Documents"],
        responses={200: MatchedTextDataGetSerializer(many=True)},
    )
    def get(self, request, pdf_id, *args, **kwargs):
        # 1) originPDF 조회
        try:
            origin_pdf = originPDF.objects.get(id=pdf_id, user_id=request.user)
        except originPDF.DoesNotExist:
            return Response(
                {"detail": "해당 PDF를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2) MatchedText 조회
        matched_texts = MatchedText.objects.filter(page_id__pdf_id=origin_pdf).select_related('page_id', 'figure_id')

        # 3) 직렬화 및 응답
        serializer = MatchedTextDataGetSerializer(matched_texts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class OriginPDFGetView(APIView):
    """
    특정 originPDF(pdf_id)에 대한 메타데이터 조회
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="PDF 메타데이터 조회",
        operation_description=(
            "지정한 PDF에 대한 메타데이터를 조회합니다.\n"
            "- 인증: Authorization: Bearer <access_token>"
        ),
        tags=["PDF Documents"],
        responses={200: OriginPDFSerializer},
    )
    def get(self, request, pdf_id, *args, **kwargs):
        # 1) originPDF 조회
        try:
            origin_pdf = originPDF.objects.get(id=pdf_id, user_id=request.user)
        except originPDF.DoesNotExist:
            return Response(
                {"detail": "해당 PDF를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2) 직렬화 및 응답
        serializer = OriginPDFSerializer(origin_pdf)
        return Response(serializer.data, status=status.HTTP_200_OK)