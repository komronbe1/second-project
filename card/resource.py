import re
from decimal import Decimal, ROUND_DOWN, InvalidOperation
from import_export import resources
from .models import Card
from .utils import send_admin_notification


class CardResource(resources.ModelResource):
    class Meta:
        model = Card
        import_id_fields = ('card_number',)
        fields = ('card_number', 'expire', 'phone', 'status', 'balance')

    def before_import_row(self, row, row_number=None, **kwargs):

        # 1. ЧИСТИМ НОМЕР КАРТЫ
        if row.get('card_number'):
            row['card_number'] = "".join(re.findall(r'\d+', str(row['card_number'])))

        # 2. ЧИСТИМ ТЕЛЕФОН
        raw_phone = str(row.get('phone', '') or '').strip().lower()
        if not raw_phone or raw_phone == 'none':
            row['phone'] = ""
        else:
            clean = "".join(re.findall(r'\d+', raw_phone))
            if len(clean) == 9:
                clean = '998' + clean
            row['phone'] = clean if len(clean) == 12 else ""

        # 3. ЧИСТИМ БАЛАНС
        raw_balance = row.get('balance', 0) or 0
        try:
            clean = Decimal(str(raw_balance).replace(',', '').replace(' ', ''))
            row['balance'] = str(clean.quantize(Decimal('0.01'), rounding=ROUND_DOWN))
        except (InvalidOperation, ValueError, TypeError):
            row['balance'] = '0.00'

        # 4. ЧИСТИМ СТАТУС
        raw_status = str(row.get('status', '') or '').lower().strip()
        row['status'] = raw_status if raw_status in ['active', 'inactive', 'expired'] else 'inactive'

    def before_save_instance(self, instance, row, **kwargs):
        if instance.card_number:
            instance.card_number = "".join(re.findall(r'\d+', str(instance.card_number)))
        try:
            instance.balance = Decimal(str(instance.balance)).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        except (InvalidOperation, ValueError, TypeError):
            instance.balance = Decimal('0.00')

    def after_import(self, dataset, result, **kwargs):
        # dry_run=True значит это просто превью — не отправляем
        if kwargs.get('dry_run', True):
            return
        created = result.totals.get('new', 0)
        updated = result.totals.get('update', 0)
        total = created + updated
        if total > 0:
            send_admin_notification(
                total,
                method=f"📁 Стандартный импорт (новых: {created}, обновлено: {updated})"
            )