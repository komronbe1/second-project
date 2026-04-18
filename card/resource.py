from import_export.resources import ModelResource
from import_export import fields
from django.core.exceptions import ValidationError
from .models import Card
from .utility import validate_phone, parse_expire


class CardRecource(ModelResource):
    card_number = fields.Field(
        column_name='card_number',
        attribute='card_number'
    )
    class Meta:
        model = Card
        fields = ('card_number', 'expire', 'phone', 'status', 'balance')
        import_id_fields = ('card_number',)

    def before_import_row(self, row, **kwargs):

        # CARD NUMBER
        card_number = row.get('card_number')

        if not card_number:
            raise ValidationError("Karta raqami kiritilmagan")

        card_number = str(card_number).replace(" ", "")

        if len(card_number) != 16 or not card_number.isdigit():
            raise ValidationError("Karta 16 ta raqam bo‘lishi kerak")

        row['card_number'] = card_number

        # PHONE
        phone = row.get('phone')
        if phone:
            try:
                row['phone'] = validate_phone(str(phone))
            except Exception:
                raise ValidationError("Telefon noto‘g‘ri")

        # EXPIRE
        expire = row.get('expire')
        if expire:
            try:
                row['expire'] = parse_expire(str(expire))
            except Exception:
                raise ValidationError("Expire noto‘g‘ri format")