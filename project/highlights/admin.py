from django.contrib import admin
from .models import Tag

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    # 목록 페이지에서 보여줄 필드
    list_display = ('id', 'pdf_id', 'tag_detail', 'color')
    
    # 클릭 시 상세 페이지로 이동할 필드
    list_display_links = ('id', 'tag_detail')
    
    # 검색 기능: 태그 내용 및 연관된 PDF 제목으로 검색 가능
    search_fields = ('tag_detail', 'pdf_id__title')
    
    # 필터 기능: 색상 기준으로 필터링 가능
    list_filter = ('color',)
    
    # 정렬 순서: 최근 추가된 항목이 위로
    ordering = ('-id',)