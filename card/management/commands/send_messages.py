from django.core.management.base import BaseCommand
from card.models import Card
from card.utils import prepare_message, send_message


class Command(BaseCommand):
    help = 'Send fake Telegram messages to filtered cards'

    def add_arguments(self, parser):
        parser.add_argument('--status',      type=str, help='Filter by status')
        parser.add_argument('--phone',       type=str, help='Filter by phone (partial)')
        parser.add_argument('--card_number', type=str, help='Filter by card number (partial)')
        parser.add_argument('--lang',        type=str, default='UZ', help='Message language: UZ or EN')
        parser.add_argument('--dry-run',     action='store_true', help='Print messages without sending')

    def handle(self, *args, **options):
        queryset = Card.objects.all()

        if options['status']:
            queryset = queryset.filter(status=options['status'])
        if options['phone']:
            queryset = queryset.filter(phone__contains=options['phone'])
        if options['card_number']:
            queryset = queryset.filter(card_number__contains=options['card_number'])

        if not queryset.exists():
            self.stdout.write(self.style.WARNING("Карты не найдены по фильтру."))
            return

        sent = 0
        failed = 0
        lang = options.get('lang', 'UZ')
        dry_run = options['dry_run']

        for card in queryset:
            message = prepare_message(card.card_number, card.balance, lang=lang)

            if dry_run:
                self.stdout.write(f"[DRY-RUN] → {message}")
                sent += 1
                continue

            # chat_id берём из телефона карты (или шлём в группу)
            chat_id = card.phone if card.phone else "-5243783628"
            success = send_message(message, chat_id=chat_id)

            if success:
                sent += 1
                self.stdout.write(self.style.SUCCESS(f"✅ Отправлено: {card.card_number}"))
            else:
                failed += 1
                self.stdout.write(self.style.ERROR(f"❌ Ошибка: {card.card_number}"))

        self.stdout.write(
            self.style.SUCCESS(f"\n📊 Итог: отправлено={sent}, ошибок={failed}")
        )