# project/accounts/serializers.py (수정됨)

from django.contrib.auth import get_user_model
# 🚨 [삭제] password_validation, Q
from rest_framework import serializers

User = get_user_model()

class UserReadSerializer(serializers.ModelSerializer):
    """
    (유지) 사용자 정보 조회용
    """
    class Meta:
        model = User
        fields = ("user_id", "username", "email", "field", "date_joined")
        read_only_fields = fields


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """
    (유지) 소셜 로그인 후 username, field 등을 설정하기 위해 필요
    """
    class Meta:
        model = User
        fields = ("username", "field") # 🚨 email은 USERNAME_FIELD이므로 수정 불가
        extra_kwargs = {
            "username": {"required": False},
            "field": {"required": False},
        }

    def validate_username(self, value):
        if not value:
            return value
        v = value.strip()
        qs = User.objects.filter(username__iexact=v, username__isnull=False) # 👈 쿼리 수정
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("이미 사용 중인 username입니다.")
        return v

# (만약 '비밀번호 설정' 기능을 추가하고 싶다면, 'old_password'가 없는 
# 'SetPasswordSerializer'를 만들어야 함)
# ...