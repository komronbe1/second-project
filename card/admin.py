from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .resource import CardRecource
from .models import Card
from .utility import card_mask, phone_mask

@admin.register(Card)
class CardAdmin(ImportExportModelAdmin):
    resource_classes = (CardRecource, )
    list_display = ['card_number', 'phone', 'balance','status','expire']
    list_filter = ['status', 'balance', 'expire', 'phone']
    search_fields = ['phone', 'card_number']

    def mask_card(self,obj):
        return card_mask(obj.card_number)
    mask_card.short_description =' Card number'

    def mask_phone(self,obj):
        return phone_mask(obj.phone)
    mask_phone.short_description = 'Phone '


