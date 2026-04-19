from import_export import resources
from django.core.exceptions import ValidationError
from .models import Card
from .utility import validate_phone, parse_expire

class CardResource(resources.ModelResource):
    class Meta:
        model = Card
        
        import_id_fields = ('card_number',)
        fields = ('card_number', 'expire', 'phone', 'status', 'balance')
        skip_unchanged = True
        report_skipped = True

    def skip_row(self, instance, original, row, import_validation_errors=None):
        """
        Bo'sh qatorlarni yoki karta raqami yo'q qatorlarni 
        import jarayonidan butunlay chetlashtiradi.
        """
        card_number = row.get('card_number')
        if not card_number or str(card_number).strip().lower() == 'none':
            return True
        return super().skip_row(instance, original, row, import_validation_errors)

    def before_import_row(self, row, **kwargs):
        
        card_number = row.get('card_number')
        if card_number:
            
            clean_card = str(card_number).replace(" ", "").split('.')[0]
            row['card_number'] = clean_card

        
        phone = row.get('phone')
        if phone and str(phone).strip().lower() != 'none':
            try:
                row['phone'] = validate_phone(str(phone))
            except Exception:
                
                pass

        
        expire = row.get('expire')
        if expire and str(expire).strip().lower() != 'none':
            try:
                dt_obj = parse_expire(str(expire))
                row['expire'] = dt_obj.strftime("%m/%y")
            except Exception:
                
                raise ValidationError(f"Sana formati xato: {expire}. Kutilayotgan format: MM/YY yoki YYYY-MM")