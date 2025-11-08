from django.contrib import admin
from .models import Tag

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    # 관리자 페이지에 보여질 컬럼
    list_display = ('id', 'pdf_id', 'tag_detail', 'color')

    # 컬럼 클릭 시 상세 페이지로 이동할 수 있는 링크
    list_display_links = ('id', 'tag_detail')

    # 검색창에서 검색할 필드
    search_fields = ('tag_detail', 'color', 'pdf_id__id', 'pdf_id__pdf_name')

    # 우측 필터 사이드바에 노출할 필드
    list_filter = ('color', 'pdf_id')

    # 정렬 기준 (id 오름차순)
    ordering = ('id',)

    # ForeignKey 선택 시 검색 기능 활성화
    autocomplete_fields = ('pdf_id',)