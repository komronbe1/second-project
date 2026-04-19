from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .resource import CardResource 
from .models import Card
from .utility import card_mask, phone_mask
@admin.register(Card)
class CardAdmin(ImportExportModelAdmin):
    resource_classes = [CardResource]
    list_display = ['masked_card_number', 'mask_phone', 'balance', 'status', 'expire']
    list_filter = ['status']
    search_fields = ['card_number', 'phone'] # Karta raqami bo'yicha qidirish uchun
    list_per_page = 50 

    def masked_card_number(self,obj):
        if obj.card_number:
            try:
                return card_mask(obj.card_number)
            except:
                return obj.card_number
        
    def mask_phone(self,obj):
        if obj.phone:
            try:
                return phone_mask(obj.phone)
            except:
                return obj.phone            
        