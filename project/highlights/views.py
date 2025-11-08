from django.shortcuts import render

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Tag
from .serializers import TagSerializer

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


# 공통 헤더(Authorization) 파라미터
auth_header = openapi.Parameter(
    name="Authorization",
    in_=openapi.IN_HEADER,
    description='JWT 토큰. 예) "Bearer <access_token>"',
    type=openapi.TYPE_STRING,
    required=True,
)

# path 파라미터 (detail 엔드포인트용)
pk_param = openapi.Parameter(
    name="pk",
    in_=openapi.IN_PATH,
    description="Tag 기본키(ID)",
    type=openapi.TYPE_INTEGER,
    required=True,
)

class TagAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="createTag",
        operation_description="새로운 Tag를 생성합니다.",
        tags=["Tag"],
        manual_parameters=[auth_header],
        request_body=TagSerializer,
        responses={
            201: TagSerializer,
            400: openapi.Response("Invalid data"),
            401: openapi.Response("Unauthorized"),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_id="listTags",
        operation_description="모든 Tag 목록을 조회합니다.",
        tags=["Tag"],
        manual_parameters=[auth_header],
        responses={
            200: TagSerializer(many=True),
            401: openapi.Response("Unauthorized"),
        },
    )
    def get(self, request, *args, **kwargs):
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_id="updateTag",
        operation_description="특정 Tag를 부분 업데이트합니다(Partial Update).",
        tags=["Tag"],
        manual_parameters=[auth_header, pk_param],
        request_body=TagSerializer,  # partial=True 이지만 스키마는 동일
        responses={
            200: TagSerializer,
            400: openapi.Response("Invalid data"),
            401: openapi.Response("Unauthorized"),
            404: openapi.Response("Tag not found."),
        },
    )
    def put(self, request, pk, *args, **kwargs):
        try:
            tag = Tag.objects.get(pk=pk)
        except Tag.DoesNotExist:
            return Response({"detail": "Tag not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = TagSerializer(tag, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_id="deleteTag",
        operation_description="특정 Tag를 삭제합니다.",
        tags=["Tag"],
        manual_parameters=[auth_header, pk_param],
        responses={
            204: openapi.Response("No Content"),
            401: openapi.Response("Unauthorized"),
            404: openapi.Response("Tag not found."),
        },
    )
    def delete(self, request, pk, *args, **kwargs):
        try:
            tag = Tag.objects.get(pk=pk)
            tag.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Tag.DoesNotExist:
            return Response({"detail": "Tag not found."}, status=status.HTTP_404_NOT_FOUND)