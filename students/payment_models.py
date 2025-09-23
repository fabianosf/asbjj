from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import uuid
import qrcode
import io
from django.core.files.base import ContentFile


class PIXPayment(models.Model):
    """Pagamentos PIX com QR Code"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('paid', 'Pago'),
        ('expired', 'Expirado'),
        ('cancelled', 'Cancelado'),
    ]
    
    # Identificação
    pix_payment_id = models.UUIDField('ID do Pagamento PIX', default=uuid.uuid4, unique=True)
    external_id = models.CharField('ID Externo', max_length=100, unique=True)
    
    # Relacionamentos
    payment = models.OneToOneField(
        'students.Payment',
        on_delete=models.CASCADE,
        related_name='pix_payment',
        verbose_name='Pagamento'
    )
    
    # Valores
    amount = models.DecimalField('Valor', max_digits=10, decimal_places=2)
    
    # PIX
    pix_key = models.CharField('Chave PIX', max_length=100, blank=True)
    pix_qr_code = models.ImageField('QR Code PIX', upload_to='pix/qr_codes/', blank=True, null=True)
    pix_copy_paste = models.TextField('Código PIX Copia e Cola', blank=True)
    
    # Status e datas
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='pending')
    expires_at = models.DateTimeField('Expira em')
    paid_at = models.DateTimeField('Pago em', null=True, blank=True)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Pagamento PIX'
        verbose_name_plural = 'Pagamentos PIX'
        ordering = ['-created_at']

    def __str__(self):
        return f"PIX - {self.payment.student.full_name} - R$ {self.amount}"

    def generate_qr_code(self):
        """Gera QR Code para o pagamento PIX"""
        if not self.pix_copy_paste:
            return None
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.pix_copy_paste)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Salvar imagem
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        filename = f"pix_qr_{self.pix_payment_id}.png"
        self.pix_qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)
        
        return self.pix_qr_code

    def save(self, *args, **kwargs):
        if not self.external_id:
            self.external_id = f"ASBJJ_{self.pix_payment_id}"
        
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)
        
        super().save(*args, **kwargs)
        
        # Gerar QR Code se não existir
        if not self.pix_qr_code and self.pix_copy_paste:
            self.generate_qr_code()
            super().save(*args, **kwargs)


class PaymentNotification(models.Model):
    """Notificações de pagamento"""
    
    NOTIFICATION_TYPES = [
        ('payment_received', 'Pagamento Recebido'),
        ('payment_overdue', 'Pagamento Vencido'),
        ('payment_reminder', 'Lembrete de Pagamento'),
        ('subscription_expiring', 'Assinatura Expirando'),
    ]
    
    payment = models.ForeignKey(
        'students.Payment',
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Pagamento'
    )
    
    notification_type = models.CharField('Tipo de Notificação', max_length=30, choices=NOTIFICATION_TYPES)
    message = models.TextField('Mensagem')
    sent_at = models.DateTimeField('Enviado em', null=True, blank=True)
    sent_via = models.CharField(
        'Enviado via',
        max_length=20,
        choices=[
            ('email', 'E-mail'),
            ('whatsapp', 'WhatsApp'),
            ('sms', 'SMS'),
        ]
    )
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Notificação de Pagamento'
        verbose_name_plural = 'Notificações de Pagamento'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.payment.student.full_name}"


class PaymentReport(models.Model):
    """Relatórios de pagamento"""
    
    REPORT_TYPES = [
        ('monthly', 'Relatório Mensal'),
        ('quarterly', 'Relatório Trimestral'),
        ('annual', 'Relatório Anual'),
        ('custom', 'Relatório Personalizado'),
    ]
    
    report_type = models.CharField('Tipo de Relatório', max_length=20, choices=REPORT_TYPES)
    title = models.CharField('Título', max_length=200)
    description = models.TextField('Descrição', blank=True)
    
    # Período
    start_date = models.DateField('Data de Início')
    end_date = models.DateField('Data de Fim')
    
    # Dados do relatório
    total_revenue = models.DecimalField('Receita Total', max_digits=12, decimal_places=2, default=0)
    total_payments = models.PositiveIntegerField('Total de Pagamentos', default=0)
    paid_payments = models.PositiveIntegerField('Pagamentos Realizados', default=0)
    pending_payments = models.PositiveIntegerField('Pagamentos Pendentes', default=0)
    overdue_payments = models.PositiveIntegerField('Pagamentos Vencidos', default=0)
    
    # Arquivo do relatório
    report_file = models.FileField('Arquivo do Relatório', upload_to='reports/', blank=True, null=True)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_reports',
        verbose_name='Criado por'
    )

    class Meta:
        verbose_name = 'Relatório de Pagamento'
        verbose_name_plural = 'Relatórios de Pagamento'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.start_date} a {self.end_date}"

    @property
    def payment_rate(self):
        """Taxa de pagamento em percentual"""
        if self.total_payments > 0:
            return (self.paid_payments / self.total_payments) * 100
        return 0
