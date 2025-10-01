from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    SignupSerializer,
    LoginSerializer,
    UserReadSerializer,
    ProfileUpdateSerializer,
    PasswordChangeSerializer,
)

User = get_user_model()


def _issue_tokens_for_user(user):
    """
    SimpleJWT 토큰 생성 유틸
    """
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


class SignupView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = _issue_tokens_for_user(user)
        return Response(
            {
                "user": UserReadSerializer(user).data,
                "tokens": tokens,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        tokens = _issue_tokens_for_user(user)
        return Response(
            {
                "user": UserReadSerializer(user).data,
                "tokens": tokens,
            },
            status=status.HTTP_200_OK,
        )


class MeView(RetrieveUpdateAPIView):
    """
    GET  /accounts/me/   -> 내 프로필 조회
    PATCH/PUT /accounts/me/ -> username/email/field 수정
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return ProfileUpdateSerializer
        return UserReadSerializer

    def get_object(self):
        return self.request.user


class PasswordChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LogoutView(APIView):
    """
    클라이언트가 refresh 토큰을 서버에 보내면 블랙리스트 처리.
    settings에 'rest_framework_simplejwt.token_blacklist'가 설치되어 있어야 작동합니다.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "refresh 토큰이 필요합니다."},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            # token_blacklist 앱이 없으면 NotImplementedError 발생
            token.blacklist()
        except Exception as e:
            # 운영 선호에 따라 204로 응답하고 클라이언트에서 토큰 폐기만 시키는 전략도 가능
            return Response({"detail": f"토큰 블랙리스트 처리 실패: {e}"},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_205_RESET_CONTENT)
