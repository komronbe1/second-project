import re
from import_export import resources, fields
from .models import Card

class CardResource(resources.ModelResource):
    card_number = fields.Field(attribute='card_number', column_name='card_number')

    class Meta:
        model = Card
        import_id_fields = ('card_number',)
        fields = ('card_number', 'expire', 'phone', 'status', 'balance')

    def before_import(self, dataset, **kwargs):
        """
        ЖЕСТКИЙ ХАК: Принудительно перезаписываем заголовки.
        Главное, чтобы в твоем Excel колонки шли именно в таком порядке:
        1: Карта, 2: Срок, 3: Телефон, 4: Статус, 5: Баланс
        """
        dataset.headers = ['card_number', 'expire', 'phone', 'status', 'balance']

    # ИСПРАВЛЕННАЯ СИГНАТУРА: добавили 'row' и убрали 'using_transactions'
    def before_save_instance(self, instance, row, **kwargs):
        """
        Чистим данные перед сохранением
        """
        # 1. Чистим номер карты
        if instance.card_number:
            instance.card_number = "".join(re.findall(r'\d+', str(instance.card_number)))

        # 2. Чистим телефон
        if instance.phone:
            phone = "".join(re.findall(r'\d+', str(instance.phone)))
            if len(phone) == 9:
                phone = '998' + phone
            instance.phone = phone

        # 3. НОВОЕ: Спасаем баланс от краша (decimal.ConversionSyntax)
        if instance.balance:
            try:
                # Меняем запятую на точку (в Excel часто пишут 500,50 вместо 500.50)
                raw_balance = str(instance.balance).replace(',', '.')
                # Убираем все символы, кроме цифр и точки
                clean_balance = "".join(re.findall(r'[\d\.]', raw_balance))

                if clean_balance:
                    instance.balance = float(clean_balance)
                else:
                    instance.balance = 0.00 # Если там были только буквы
            except Exception:
                instance.balance = 0.00
        else:
            instance.balance = 0.00 # Если ячейка пустая

        return instance