from django.contrib import admin
from .models import originPDF

@admin.register(originPDF)
class OriginPDFAdmin(admin.ModelAdmin):
    # 목록에 표시할 필드들
    list_display = ('id', 'title', 'user_id', 'S3_url', 'created_at')
    
    # 클릭 시 상세 페이지로 이동할 필드
    list_display_links = ('id', 'title')
    
    # 검색 기능
    search_fields = ('title', 'user_id__username')
    
    # 필터 기능 (날짜 등으로 필터 가능)
    list_filter = ('created_at',)
    
    # 생성일 기준 내림차순 정렬
    ordering = ('-created_at',)