from django.contrib import admin
from .models import PDFfigure

@admin.register(PDFfigure)
class PDFfigureAdmin(admin.ModelAdmin):
    list_display = ('id', 'page_id', 'figure_type')
    search_fields = ('figure_type',)