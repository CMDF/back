from django.contrib.auth import get_user_model, password_validation
from django.db.models import Q
from rest_framework import serializers

User = get_user_model()

class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("user_id", "username", "email", "field", "date_joined")
        read_only_fields = fields


class SignupSerializer(serializers.ModelSerializer):
    # 클라이언트에서 비밀번호 2회 입력을 원하면 password2 필드 추가해도 됨
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def validate_username(self, value):
        v = value.strip()
        # 필요시 소문자 강제: v = v.lower()
        # 대소문자 무시 중복 방지
        if User.objects.filter(username__iexact=v).exists():
            raise serializers.ValidationError("이미 사용 중인 username입니다.")
        return v

    def validate_email(self, value):
        if not value:
            return value
        v = value.strip().lower()
        # NULL이 아닌 경우에만 유니크 보장
        if User.objects.filter(Q(email__iexact=v) & Q(email__isnull=False)).exists():
            raise serializers.ValidationError("이미 사용 중인 이메일입니다.")
        return v

    def validate(self, attrs):
        # Django의 비밀번호 검증기 사용
        password_validation.validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        username = validated_data["username"].strip()
        email = validated_data.get("email")
        if email:
            email = email.strip().lower()
        password = validated_data["password"]

        # 매니저 시그니처가 (username, password=None, **extra_fields) 여도
        # email은 kw로 안전하게 전달됩니다.
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        username = attrs.get("username", "").strip()
        password = attrs.get("password")

        # 대소문자 무시 조회 (인증 백엔드에서 처리한다면 여기서 exact로 바꿔도 됨)
        try:
            user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            raise serializers.ValidationError("아이디 또는 비밀번호가 올바르지 않습니다.")

        if not user.is_active:
            raise serializers.ValidationError("비활성화된 계정입니다.")

        if not user.check_password(password):
            raise serializers.ValidationError("아이디 또는 비밀번호가 올바르지 않습니다.")

        attrs["user"] = user
        return attrs


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email", "field")
        extra_kwargs = {
            "username": {"required": False},
            "email": {"required": False},
            "field": {"required": False},
        }

    def validate_username(self, value):
        v = value.strip()
        qs = User.objects.filter(username__iexact=v)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("이미 사용 중인 username입니다.")
        return v

    def validate_email(self, value):
        if not value:
            return value
        v = value.strip().lower()
        qs = User.objects.filter(email__iexact=v, email__isnull=False)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("이미 사용 중인 이메일입니다.")
        return v

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, trim_whitespace=False)
    new_password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        user = self.context["request"].user
        if not user.check_password(attrs["old_password"]):
            raise serializers.ValidationError({"old_password": "현재 비밀번호가 올바르지 않습니다."})
        password_validation.validate_password(attrs["new_password"], user=user)
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        return user
