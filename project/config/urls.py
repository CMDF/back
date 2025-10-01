from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from accounts.views import LoginView, SignupView, PasswordChangeView, LogoutView

schema_view = get_schema_view(
    openapi.Info(
        title="캡스톤디자인 프로젝트: CMD_F API",
        default_version='v1',
        description="캡스톤디자인 프로젝트 API 문서입니다.",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # 앱 라우팅
    path('api/accounts/', include('accounts.urls')),
    path('api/highlights/', include('highlights.urls')),
    path('api/pdf_figures/', include('pdf_figures.urls')),
    
    # JWT 관련
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('password/change/', PasswordChangeView.as_view(), name='password_change'),

    # 토큰 갱신 및 검증
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # Swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
