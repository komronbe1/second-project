from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from datetime import date
from card.utility import is_luhn_valid, validate_phone, is_expired, normalize_card

# Holatlar uchun konstantalar
ACTIVE = 'active'
EXPIRE = 'expired'
INACTIVE = 'inactive'

class User(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.username


class Card(models.Model):
    STATUS_CHOICES = (
        (ACTIVE, 'active'),
        (EXPIRE, 'expired'),
        (INACTIVE, 'inactive')
    )

    card_number = models.CharField(max_length=20, unique=True)
    expire = models.DateField(default=False)
    phone = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ACTIVE)
    balance = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        default=0
    )

    def clean(self):
        errors = {}
        self.card_number = normalize_card(self.card_number)
        if not self.card_number.isdigit():
            errors['card_number'] = "Faqat raqam bo‘lishi kerak"

        if len(self.card_number) != 16:
            errors['card_number'] = "16 xonali bo‘lishi kerak"
        if self.card_number:
            if not is_luhn_valid(self.card_number):
                errors['card_number'] = f"Karta raqami xato: {self.card_number}"

        if self.phone:
            try:
                self.phone = validate_phone(self.phone)
            except ValidationError:
                errors['phone'] = "Telefon noto'g'ri"
        
        if self.expire:
            try:
                self.expire = normalize_expire(self.expire)
            except Exception:
                errors['expire'] = "Expire noto‘g‘ri"

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()

        if self.status == ACTIVE and is_expired(self.expire):
            self.status = EXPIRE
            super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Karta"
        verbose_name_plural = "Kartalar"
