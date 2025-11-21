from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import PDFfigure
from .serializers import PDFfigureSerializer

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class GetFiguresByOriginPDFAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="getFiguresByOriginPDF",
        operation_description="주어진 PDF 문서 ID에 연결된 모든 PDF figure를 조회합니다.",
        tags=["PDF Figures"],
        responses={200: PDFfigureSerializer(many=True), 401: openapi.Response("Unauthorized")},
    )
    def get(self, request, pdf_id):
        qs = PDFfigure.objects.filter(page_id__pdf_id=pdf_id)
        return Response(PDFfigureSerializer(qs, many=True).data, status=status.HTTP_200_OK)