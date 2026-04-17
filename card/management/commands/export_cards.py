import csv
from django.core.management.base import BaseCommand
from card.models import Card

class Command(BaseCommand):
    help = 'Export cards to CSV with filters'

    def add_arguments(self, parser):
        parser.add_argument('--status', type=str, help='Filter by status')
        parser.add_argument('--phone', type=str, help='Filter by phone')
        parser.add_argument('--file', type=str, default='exported_cards.csv', help='Output file name')

    def handle(self, *args, **options):
        queryset = Card.objects.all()

        # Фильтрация
        if options['status']:
            queryset = queryset.filter(status=options['status'])
        if options['phone']:
            queryset = queryset.filter(phone__contains=options['phone'])

        with open(options['file'], mode='w', encoding='utf-16') as f:
            writer = csv.writer(f)
            writer.writerow(['Phone', 'Card Number', 'Status', 'Created At'])

            for card in queryset:
                writer.writerow([card.phone, card.card_number, card.status, card.created_at])

        self.stdout.write(self.style.SUCCESS(f'Successfully exported {queryset.count()} records to {options["file"]}'))