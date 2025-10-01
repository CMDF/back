# models.py
from django.db import models
from django.db.models import Q, UniqueConstraint
from django.db.models.functions import Lower
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

username_validator = RegexValidator(
    regex=r"^[a-zA-Z0-9_]{3,30}$",
    message="username은 3~30자의 영문/숫자/언더스코어만 허용됩니다.",
)

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, password=None, email=None, **extra_fields):
        if not username:
            raise ValueError("username is required")
        username = username.strip().lower()  # 필요시 .lower()로 소문자 강제
        email = self.normalize_email(email) if email else None

        user = self.model(username=username, email=email, **extra_fields)

        # [A] 비번 필수 운영이면:
        if not password:
            raise ValueError("password is required")
        user.set_password(password)

        # [B] 소셜/패스워드리스 허용이면 위 [A] 대신 다음 한 줄 사용
        # if password: user.set_password(password)
        # else: user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, email=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not password:
            raise ValueError("Superuser must have a password")
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, password=password, email=email, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.BigAutoField(primary_key=True, db_column="user_id")

    # 로그인 아이디(닉네임처럼 사용)
    username = models.CharField(
        max_length=150,
        unique=True,
        db_index=True,
        validators=[username_validator],
    )

    # 선택 입력: 입력된 경우에는 유일해야 함
    email = models.EmailField(unique=True, null=True, blank=True)

    field = models.CharField(max_length=255, null=True, blank=True, db_column="Field")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    # createsuperuser 시 추가 필드(이메일까지 강제하려면 ["email"]로 변경)
    REQUIRED_FIELDS = ["email"]

    objects = UserManager()

    class Meta:
        db_table = "users"  # 기존 "User" 사용 중이면 유지, 새 프로젝트면 소문자 테이블 권장
        constraints = [
            # username 대소문자 무시 유니크
            UniqueConstraint(Lower("username"), name="uniq_username_ci"),
            # email이 입력된 경우에만(=NULL 아님) 대소문자 무시 유니크
            UniqueConstraint(
                Lower("email"),
                condition=Q(email__isnull=False),
                name="uniq_email_ci_notnull",
            ),
        ]
        indexes = [
            models.Index(Lower("username"), name="idx_username_ci"),
            models.Index(Lower("email"), name="idx_email_ci"),
        ]

    def __str__(self):
        return self.username
