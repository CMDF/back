# project/accounts/swagger.py
from rest_framework import serializers
from drf_yasg import openapi

# --- 요청/응답 전용 Serializer (뷰 로직에 영향 없음) ---

class GoogleIdTokenSerializer(serializers.Serializer):
    id_token = serializers.CharField(help_text="Google 발급 ID Token (JWT)")

class TokenPairSerializer(serializers.Serializer):
    access = serializers.CharField(help_text="액세스 JWT")
    refresh = serializers.CharField(help_text="리프레시 JWT")

class RefreshTokenInputSerializer(serializers.Serializer):
    refresh = serializers.CharField(help_text="블랙리스트 처리할 리프레시 토큰")

# --- 공용 오류 스키마 (Swagger2 형식) ---
ErrorDetailSchema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "detail": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="오류 상세 메시지(또는 객체)"
        )
    },
    example={"detail": "Invalid token"}
)

ValidationErrorSchema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    additional_properties=openapi.Items(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)),
    example={
        "username": [
            "username은 3~30자의 영문/숫자/언더스코어만 허용됩니다."
        ]
    }
)