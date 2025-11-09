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

User = get_user_model()

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