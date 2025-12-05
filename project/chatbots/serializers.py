from rest_framework import serializers

class SelectedTextSerializer(serializers.Serializer):
    text = serializers.CharField(help_text="선택한 텍스트 내용")
    page_id = serializers.IntegerField(help_text="해당 텍스트가 있는 페이지 아이디 (originPDF의 PDFpage ID, 진짜 페이지 번호가 아님)")

class ChatRequestSerializer(serializers.Serializer):
    # --- 필수 필드 ---
    pdf_id = serializers.IntegerField(
        required=True, 
        help_text="질문 대상 PDF 문서의 ID"
    )
    question = serializers.CharField(
        required=True, 
        help_text="사용자의 질문 내용"
    )

    # iOS에서 값을 안 보내거나 null로 보낼 수 있으므로 required=False, allow_null=True 설정
    figure_ids = serializers.ListField(
        child=serializers.IntegerField(), 
        required=False, 
        allow_null=True, 
        default=[],
        help_text="참고할 Figure(이미지/표)의 ID 목록 (MatchedText 조회용)"
    )
    
    highlight_ids = serializers.ListField(
        child=serializers.IntegerField(), 
        required=False, 
        allow_null=True, 
        default=[],
        help_text="참고할 Highlight(형광펜)의 ID 목록"
    )
    
    selected_texts = serializers.ListField(
        child=SelectedTextSerializer(), 
        required=False, 
        allow_null=True, 
        default=[],
        help_text="사용자가 드래그하여 선택한 텍스트 목록"
    )