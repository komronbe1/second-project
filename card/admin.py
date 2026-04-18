from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .resource import CardResource  # Resource deb to'g'rilandi
from .models import Card

@admin.register(Card)
class CardAdmin(ImportExportModelAdmin):
    resource_classes = [CardResource]
    list_display = ['card_number', 'phone', 'balance', 'status', 'expire']
    list_filter = ['status']
    search_fields = ['card_number', 'phone'] # Karta raqami bo'yicha qidirish uchun
    list_per_page = 50 # Admin panelda tezroq yuklanishi uchun