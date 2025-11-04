# project/accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# User 모델을 admin 사이트에 등록
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom User Admin 정의
    UserAdmin을 상속받아 email 기반으로 수정
    """
    
    # 관리자 페이지 목록에 보여줄 필드
    # (UserAdmin의 기본 list_display에서 first_name, last_name 제외)
    list_display = (
        "email", 
        "username", 
        "field", 
        "is_active", 
        "is_staff", 
        "date_joined"
    )
    
    # 목록에서 링크로 사용할 필드 (기본값: 첫 번째 필드)
    list_display_links = ("email", "username")

    # 검색 필드
    # (UserAdmin의 기본값 'username', 'first_name', 'last_name', 'email'에서 수정)
    search_fields = ("email", "username")

    # 정렬 기준 (UserAdmin의 기본값 'username'에서 'email'로 변경)
    ordering = ("email",)

    # 필터 옵션
    list_filter = ("is_active", "is_staff", "is_superuser", "groups")

    # '사용자 수정' 페이지에서 보여줄 필드 구성
    # (UserAdmin의 fieldsets를 email 기반으로 재정의)
    fieldsets = (
        # (섹션 제목, {'fields': (필드 목록,)})
        (None, {"fields": ("email", "password")}), # 'None'은 섹션 제목 없음을 의미
        ("Personal info", {"fields": ("username", "field")}), # 우리 모델의 커스텀 필드
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    # '사용자 추가' 페이지에서 보여줄 필드 구성
    # (UserAdmin의 add_fieldsets를 email 기반으로 재정의)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                # email(ID), username(REQUIRED_FIELD), password
                "fields": ("email", "username", "password", "password2"), 
            },
        ),
    )
    
    # groups와 user_permissions 필드를 수평으로 표시
    filter_horizontal = ("groups", "user_permissions")