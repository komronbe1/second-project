from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .resource import CardResource 
from .models import Card
from .utility import card_mask, phone_mask


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
        