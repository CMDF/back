# highlights/views.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Tag, Highlight
from .serializers import TagSerializer, HighlightSerializer

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# # 공통 헤더 파라미터 (JWT)
# auth_header = openapi.Parameter(
#     name="Authorization",
#     in_=openapi.IN_HEADER,
#     description='JWT 토큰. 예) "Bearer <access_token>"',
#     type=openapi.TYPE_STRING,
#     required=True,
# )
# # pk path 파라미터 (디테일 전용)
# pk_param = openapi.Parameter(
#     name="pk",
#     in_=openapi.IN_PATH,
#     description="Tag 기본키(ID)",
#     type=openapi.TYPE_INTEGER,
#     required=True,
# )

class TagListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="getTags",
        operation_description="PDF에 연결된 Tag 목록을 조회합니다. ?pdf_id= 로 필터링 가능",
        tags=["Tag"],
        responses={200: TagSerializer(many=True), 401: openapi.Response("Unauthorized")},
    )
    def get(self, request):
        pdf_id = request.query_params.get("pdf_id")
        qs = Tag.objects.all()
        if pdf_id is not None:
            qs = qs.filter(pdf_id=pdf_id)
        return Response(TagSerializer(qs, many=True).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="createTag",
        operation_description="새로운 Tag를 생성합니다.",
        tags=["Tag"],
        request_body=TagSerializer,
        responses={201: TagSerializer, 400: openapi.Response("Invalid data"), 401: openapi.Response("Unauthorized")},
    )
    def post(self, request):
        s = TagSerializer(data=request.data)
        if s.is_valid():
            s.save()
            return Response(s.data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class TagDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="updateTag",
        operation_description="특정 Tag를 부분 업데이트합니다(Partial Update, Tag의 pk를 파라미터로 삽입).",
        tags=["Tag"],
        request_body=TagSerializer,
        responses={
            200: TagSerializer,
            400: openapi.Response("Invalid data"),
            401: openapi.Response("Unauthorized"),
            404: openapi.Response("Tag not found."),
        },
    )
    def put(self, request, pk):
        try:
            tag = Tag.objects.get(pk=pk)
        except Tag.DoesNotExist:
            return Response({"detail": "Tag not found."}, status=status.HTTP_404_NOT_FOUND)

        s = TagSerializer(tag, data=request.data, partial=True)
        if s.is_valid():
            s.save()
            return Response(s.data, status=status.HTTP_200_OK)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_id="deleteTag",
        operation_description="특정 Tag를 삭제합니다(Tag의 pk를 파라미터로 삽입).",
        tags=["Tag"],
        responses={204: openapi.Response("No Content"), 401: openapi.Response("Unauthorized"), 404: openapi.Response("Tag not found.")},
    )
    def delete(self, request, pk):
        try:
            Tag.objects.get(pk=pk).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Tag.DoesNotExist:
            return Response({"detail": "Tag not found."}, status=status.HTTP_404_NOT_FOUND)
        
class HighlightCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="createHighlight",
        operation_description="새로운 Highlight를 생성합니다.",
        tags=["Highlight"],
        request_body=HighlightSerializer,
        responses={201: HighlightSerializer, 400: openapi.Response("Invalid data"), 401: openapi.Response("Unauthorized")},
    )
    def post(self, request):
        s = HighlightSerializer(data=request.data)
        if s.is_valid():
            s.save()
            return Response(s.data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

class HighlightGetAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="getHighlights",
        operation_description="PDF 페이지에 연결된 Highlight 목록을 조회합니다. ?page_id= 로 필터링 가능",
        tags=["Highlight"],
        responses={200: HighlightSerializer(many=True), 401: openapi.Response("Unauthorized")},
    )
    def get(self, request):
        page_id = request.query_params.get("page_id")
        qs = Highlight.objects.all()
        if page_id is not None:
            qs = qs.filter(page_id=page_id)
        return Response(HighlightSerializer(qs, many=True).data, status=status.HTTP_200_OK)
    
class HighlightDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="deleteHighlight",
        operation_description="특정 Highlight를 삭제합니다(Highlight의 pk를 파라미터로 삽입).",
        tags=["Highlight"],
        responses={204: openapi.Response("No Content"), 401: openapi.Response("Unauthorized"), 404: openapi.Response("Highlight not found.")},
    )
    def delete(self, request, pk):
        try:
            Highlight.objects.get(pk=pk).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Highlight.DoesNotExist:
            return Response({"detail": "Highlight not found."}, status=status.HTTP_404_NOT_FOUND)
        
    @swagger_auto_schema(
        operation_id="updateHighlight",
        operation_description="특정 Highlight를 부분 업데이트합니다(Partial Update, Highlight의 pk를 파라미터로 삽입).",
        tags=["Highlight"],
        responses={
            200: HighlightSerializer,
            400: openapi.Response("Invalid data"),
            401: openapi.Response("Unauthorized"),
            404: openapi.Response("Highlight not found."),
        },
    )
    def put(self, request, pk):
        try:
            highlight = Highlight.objects.get(pk=pk)
        except Highlight.DoesNotExist:
            return Response({"detail": "Highlight not found."}, status=status.HTTP_404_NOT_FOUND)

        s = HighlightSerializer(highlight, data=request.data, partial=True)
        if s.is_valid():
            s.save()
            return Response(s.data, status=status.HTTP_200_OK)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)