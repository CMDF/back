from django.contrib import admin
from .models import ChatSession, ChatMessage

# 1. 메시지 인라인 (ChatSession 안에 메시지를 끼워넣어 보여주기 위함)
class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0  # 빈 입력 칸을 기본적으로 보여주지 않음 (깔끔하게 보기 위해)
    readonly_fields = ('created_at',)  # 생성일은 수정 불가능하게 설정
    fields = ('role', 'content', 'created_at') # 보여줄 필드 순서
    ordering = ('created_at',) # 시간순 정렬

# 2. 채팅 세션 관리자 (ChatSession)
@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    # 목록 화면에 보여줄 컬럼들
    list_display = ('id', 'get_pdf_title', 'user', 'title', 'created_at', 'message_count')
    
    # 우측 필터 옵션
    list_filter = ('created_at', 'user')
    
    # 검색 기능 (PDF 제목, 사용자명, 채팅방 제목으로 검색 가능)
    search_fields = ('title', 'user__username', 'origin_pdf__title')
    
    # 세부 페이지에 메시지 인라인 추가 (핵심!)
    inlines = [ChatMessageInline]
    
    # 읽기 전용 필드
    readonly_fields = ('created_at', 'updated_at')

    # 리스트에서 PDF 제목을 편하게 보기 위한 메서드
    def get_pdf_title(self, obj):
        return obj.origin_pdf.title
    get_pdf_title.short_description = 'PDF 문서명' # 컬럼 헤더 이름

    # 리스트에서 메시지 개수 보기
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = '메시지 수'

# 3. 개별 메시지 관리자 (ChatMessage)
# 보통은 Session 안에서 보지만, 전체 메시지 검색이 필요할 때 유용함
@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'role', 'short_content', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('content', 'session__title', 'session__user__username')
    readonly_fields = ('created_at',)

    # 내용이 너무 길면 잘라서 보여주기
    def short_content(self, obj):
        if len(obj.content) > 50:
            return obj.content[:50] + "..."
        return obj.content
    short_content.short_description = '내용 요약'