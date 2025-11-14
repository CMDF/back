# config/urls.py
from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static

schema_view = get_schema_view(
    openapi.Info(
        title="캡스톤디자인 프로젝트: CMD_F API",
        default_version="v1",
        description="캡스톤디자인 프로젝트 API 문서입니다.",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # 앱 라우팅 (accounts 내부에서 로그인/회원가입/JWT 모두 처리)
    path("accounts/", include("accounts.urls")),
    path("highlights/", include("highlights.urls")),
    path("pdf_documents/", include("pdf_documents.urls")),
    path("pdf_figures/", include("pdf_figures.urls")),

    # Swagger / OpenAPI
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    #re_path(r"^swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

# 개발 환경에서 정적/미디어 파일 서빙
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=getattr(settings, "STATIC_ROOT", None))
    urlpatterns += static(settings.MEDIA_URL, document_root=getattr(settings, "MEDIA_ROOT", None))