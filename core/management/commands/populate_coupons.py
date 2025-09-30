import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import Coupon


class Command(BaseCommand):
    help = 'Popula o banco de dados com cupons de exemplo.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Criando cupons de exemplo...'))

        # Data atual
        now = timezone.now()
        
        coupons_data = [
            {
                'code': 'BEMVINDO10',
                'description': 'Cupom de boas-vindas - 10% de desconto',
                'discount_type': 'percentage',
                'discount_value': 10.00,
                'minimum_amount': 50.00,
                'maximum_discount': 50.00,
                'usage_limit': 100,
                'valid_from': now,
                'valid_until': now + timedelta(days=30),
            },
            {
                'code': 'FRETE15',
                'description': 'Desconto de R$ 15 no frete',
                'discount_type': 'fixed',
                'discount_value': 15.00,
                'minimum_amount': 100.00,
                'usage_limit': 50,
                'valid_from': now,
                'valid_until': now + timedelta(days=15),
            },
            {
                'code': 'BLACKFRIDAY',
                'description': 'Black Friday - 20% de desconto',
                'discount_type': 'percentage',
                'discount_value': 20.00,
                'minimum_amount': 200.00,
                'maximum_discount': 100.00,
                'usage_limit': 200,
                'valid_from': now,
                'valid_until': now + timedelta(days=7),
            },
            {
                'code': 'PRIMEIRA10',
                'description': 'Primeira compra - 10% de desconto',
                'discount_type': 'percentage',
                'discount_value': 10.00,
                'minimum_amount': 80.00,
                'maximum_discount': 30.00,
                'usage_limit': 1,
                'valid_from': now,
                'valid_until': now + timedelta(days=60),
            },
            {
                'code': 'KIMONO20',
                'description': 'Desconto especial em kimonos',
                'discount_type': 'percentage',
                'discount_value': 20.00,
                'minimum_amount': 300.00,
                'maximum_discount': 80.00,
                'usage_limit': 30,
                'valid_from': now,
                'valid_until': now + timedelta(days=45),
            },
        ]

        for coupon_data in coupons_data:
            coupon, created = Coupon.objects.get_or_create(
                code=coupon_data['code'],
                defaults=coupon_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Cupom criado: {coupon.code}'))
            else:
                self.stdout.write(self.style.WARNING(f'Cupom já existe: {coupon.code}'))

        self.stdout.write(self.style.SUCCESS('Cupons criados com sucesso!'))
        self.stdout.write(self.style.SUCCESS('Cupons disponíveis:'))
        for coupon in Coupon.objects.filter(is_active=True):
            self.stdout.write(f'  - {coupon.code}: {coupon.description}')
