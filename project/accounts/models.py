# project/accounts/models.py (수정됨)

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

    # 🚨 [수정됨] email을 기본 ID로 사용, username은 필수가 아님
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("email is required")
        
        email = self.normalize_email(email)
        
        # username이 전달되면 사용, 아니면 None
        username = extra_fields.pop("username", None)
        if username:
            username = username.strip().lower()

        user = self.model(email=email, username=username, **extra_fields)

        # 🚨 [수정됨] 소셜 로그인을 위해 [B] 옵션(set_unusable_password) 채택
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password() # 소셜 로그인 유저는 비밀번호가 없음

        user.save(using=self._db)
        return user

    # 🚨 [수정됨] create_superuser도 email을 기본 ID로 사용
    def create_superuser(self, email, password=None, username=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not password:
            raise ValueError("Superuser must have a password")
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        
        # createsuperuser 시 username이 필요하면 여기서 처리 (없으면 email 앞부분 등)
        if not username:
             username = email.split('@')[0] # 예시: 이메일 앞부분

        return self.create_user(
            email=email, 
            password=password, 
            username=username, 
            **extra_fields
        )


class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.BigAutoField(primary_key=True, db_column="user_id")

    # 🚨 [수정됨] email을 기본 ID로 사용. unique=True, null=False
    email = models.EmailField(unique=True, null=False, blank=False)

    # 🚨 [수정됨] username은 선택적 필드로 변경 (null=True, blank=True)
    # (단, 입력된 경우에는 유일해야 함)
    username = models.CharField(
        max_length=150,
        unique=True,
        null=True, # 👈 수정
        blank=True, # 👈 수정
        db_index=True,
        validators=[username_validator],
    )

    field = models.CharField(max_length=255, null=True, blank=True, db_column="Field")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    # 🚨 [수정됨] USERNAME_FIELD를 email로 변경
    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    # 🚨 [수정됨] createsuperuser 시 email은 ID이므로, username을 필드로 받음
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    class Meta:
        db_table = "users"
        constraints = [
            # 🚨 [수정됨] username이 입력된 경우에만(=NULL 아님) 유니크
            UniqueConstraint(
                Lower("username"),
                condition=Q(username__isnull=False), # 👈 수정
                name="uniq_username_ci_notnull",
            ),
            # email은 필드 정의에서 이미 unique=True이므로 별도 제약조건 불필요
            # (EmailField는 기본적으로 대소문자 무관하게 동작함)
        ]
        # ... indexes는 그대로 두셔도 됩니다 ...

    def __str__(self):
        return self.email # 👈 email로 변경