# project/accounts/views.py
from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

from .serializers import (
    UserReadSerializer,
    ProfileUpdateSerializer,
)

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.utils.decorators import method_decorator

from .swagger import (
    GoogleIdTokenSerializer,
    TokenPairSerializer,
    RefreshTokenInputSerializer,
    ErrorDetailSchema,
    ValidationErrorSchema,
)

User = get_user_model()


@method_decorator(name="get", decorator=swagger_auto_schema(
    operation_summary="내 프로필 조회",
    tags=["Accounts"],
    responses={
        200: UserReadSerializer,
        401: openapi.Response("인증 필요", ErrorDetailSchema),
    }
))
@method_decorator(name="put", decorator=swagger_auto_schema(
    operation_summary="내 프로필 전체 수정",
    tags=["Accounts"],
    request_body=ProfileUpdateSerializer,
    responses={
        200: UserReadSerializer,
        400: openapi.Response("유효성 오류", ValidationErrorSchema,
                              examples={"application/json": {
                                  "username": ["이미 사용 중인 username입니다."]
                              }}),
        401: openapi.Response("인증 필요", ErrorDetailSchema),
    }
))
@method_decorator(name="patch", decorator=swagger_auto_schema(
    operation_summary="내 프로필 부분 수정",
    tags=["Accounts"],
    request_body=ProfileUpdateSerializer,
    responses={
        200: UserReadSerializer,
        400: openapi.Response("유효성 오류", ValidationErrorSchema),
        401: openapi.Response("인증 필요", ErrorDetailSchema),
    }
))
class MeView(RetrieveUpdateAPIView):
    """
    (유지)
    GET     /accounts/me/  -> 내 프로필 조회
    PATCH/PUT /accounts/me/  -> username/field 수정
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return ProfileUpdateSerializer
        return UserReadSerializer

    def get_object(self):
        return self.request.user


class LogoutView(APIView):
    """
    (유지) dj-rest-auth가 발급한 refresh 토큰을 받아 블랙리스트 처리
    """
    permission_classes = [permissions.IsAuthenticated]

    
    @swagger_auto_schema(
    operation_summary="로그아웃(Refresh 블랙리스트)",
    tags=["Accounts"],
    request_body=RefreshTokenInputSerializer,
    responses={
        205: openapi.Response("성공적으로 블랙리스트 처리됨"),
        400: openapi.Response("잘못된 토큰 또는 처리 실패", ErrorDetailSchema,
                              examples={"application/json": {
                                  "detail": "토큰 블랙리스트 처리 실패: Token is blacklisted"
                              }}),
        401: openapi.Response("인증 필요", ErrorDetailSchema),
    }
    )
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "refresh 토큰이 필요합니다."},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"detail": f"토큰 블랙리스트 처리 실패: {e}"},
                            status=status.HTTP_400_BAD_REQUEST)


@method_decorator(name="post", decorator=swagger_auto_schema(
    operation_summary="Google ID Token 로그인/회원가입",
    tags=["Accounts"],
    request_body=GoogleIdTokenSerializer,
    responses={
        200: openapi.Response(
            "로그인 성공 (JWT 페어)",
            schema=TokenPairSerializer,
            examples={"application/json": {
                "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...",
                "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
            }}
        ),
        400: openapi.Response("토큰 검증 실패 또는 요청 오류", ErrorDetailSchema),
        500: openapi.Response("서버 오류", ErrorDetailSchema),
    }
))
class GoogleLogin(SocialLoginView):
    """
    iOS 앱에서 받은 Google ID Token을 처리하여 Django 유저로 로그인/회원가입
    
    POST /api/accounts/google/login/
    {
        "id_token": "..."
    }
    
    위와 같이 요청 시, dj-rest-auth가 토큰을 검증하고 
    User 모델을 생성/조회한 뒤,
    Access/Refresh JWT 토큰을 응답으로 반환합니다.
    """
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client