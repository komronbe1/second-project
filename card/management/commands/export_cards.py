import csv
from django.core.management.base import BaseCommand
from card.models import Card

class Command(BaseCommand):
    help = 'Export cards to CSV with filters'

    def add_arguments(self, parser):
        parser.add_argument('--status', type=str, help='Filter by status (active, inactive, expired)')
        parser.add_argument('--phone', type=str, help='Filter by phone')
        parser.add_argument('--card_number', type=str, help='Filter by card number') # Добавили фильтр по карте
        parser.add_argument('--file', type=str, default='exported_cards.csv', help='Output file name')

    def handle(self, *args, **options):
        queryset = Card.objects.all()

        # Фильтрация
        if options['status']:
            queryset = queryset.filter(status=options['status'])
        if options['phone']:
            queryset = queryset.filter(phone__contains=options['phone'])
        if options['card_number']:
            queryset = queryset.filter(card_number__contains=options['card_number']) # Логика фильтрации карты

        # Используем стандартный utf-8
        with open(options['file'], mode='w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            # Выводим все актуальные поля нашей модели
            writer.writerow(['Card Number', 'Expire', 'Phone', 'Status', 'Balance'])

            for card in queryset:
                # Записываем правильные поля из нашей модели
                writer.writerow([
                    card.card_number,
                    card.expire,
                    card.phone,
                    card.status,
                    card.balance
                ])

        self.stdout.write(self.style.SUCCESS(f'✅ Successfully exported {queryset.count()} records to {options["file"]}'))