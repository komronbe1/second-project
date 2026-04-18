from import_export import resources, fields
from django.core.exceptions import ValidationError
from .models import Card
from .utility import validate_phone, parse_expire

class CardResource(resources.ModelResource):
    class Meta:
        model = Card
        fields = ('card_number', 'expire', 'phone', 'status', 'balance')
        import_id_fields = ('card_number',)
        # Muhim: Ma'lumot o'zgarmagan qatorlarni yoki bo'sh joylarni o'tkazib yuboradi
        skip_unchanged = True
        report_skipped = True

    def before_import_row(self, row, **kwargs):
        # 1. Karta raqamini tekshirish (Bo'sh qatorlarni to'xtatish)
        card_number = row.get('card_number')
        if not card_number or str(card_number).strip().lower() == 'none':
            # Bu yerda xato qaytarmasdan, shunchaki qatorni o'chirish ham mumkin
            # Lekin xato qaytarish orqali qaysi qatorda ma'lumot yo'qligini bilasiz
            return 

        # Excel ba'zan raqamlarni 4.55e+15 yoki 1234.0 qilib yuboradi
        # Ularni toza string holatiga keltiramiz
        row['card_number'] = str(card_number).replace(" ", "").split('.')[0]

        # 2. Telefon raqami
        phone = row.get('phone')
        if phone and str(phone).strip().lower() != 'none':
            try:
                row['phone'] = validate_phone(str(phone))
            except:
                pass # Noto'g'ri bo'lsa modelning clean'iga qoldiramiz

        # 3. Sana (Expire)
        expire = row.get('expire')
        if expire and str(expire).strip().lower() != 'none':
            try:
                dt_obj = parse_expire(str(expire))
                row['expire'] = dt_obj.strftime("%m/%y")
            except:
                raise ValidationError(f"Sana formati xato: {expire}")