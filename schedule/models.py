from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from classes.models import Class, ClassSchedule


class TrialClassBooking(models.Model):
    """Agendamento de aulas experimentais"""
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('confirmed', 'Confirmado'),
        ('completed', 'Concluída'),
        ('cancelled', 'Cancelada'),
        ('no_show', 'Não Compareceu'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='trial_bookings',
        verbose_name='Usuário',
        null=True,
        blank=True
    )
    
    # Informações do interessado
    first_name = models.CharField('Nome', max_length=100)
    last_name = models.CharField('Sobrenome', max_length=100)
    email = models.EmailField('E-mail')
    phone = models.CharField('Telefone', max_length=20)
    birth_date = models.DateField('Data de Nascimento', null=True, blank=True)
    
    # Informações da aula
    class_obj = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='trial_bookings',
        verbose_name='Aula'
    )
    preferred_schedule = models.ForeignKey(
        ClassSchedule,
        on_delete=models.CASCADE,
        related_name='trial_bookings',
        verbose_name='Horário Preferido',
        null=True,
        blank=True
    )
    preferred_date = models.DateField('Data Preferida')
    preferred_time = models.TimeField('Horário Preferido', null=True, blank=True)
    
    # Status e observações
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField('Observações', blank=True)
    admin_notes = models.TextField('Observações Administrativas', blank=True)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    confirmed_at = models.DateTimeField('Confirmado em', null=True, blank=True)
    completed_at = models.DateTimeField('Concluído em', null=True, blank=True)

    class Meta:
        verbose_name = 'Agendamento de Aula Experimental'
        verbose_name_plural = 'Agendamentos de Aulas Experimentais'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.class_obj.name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        if self.birth_date:
            from datetime import date
            today = date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None


class RegularBooking(models.Model):
    """Agendamento de aulas regulares"""
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('paused', 'Pausado'),
        ('cancelled', 'Cancelado'),
        ('completed', 'Concluído'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('paid', 'Pago'),
        ('overdue', 'Vencido'),
        ('refunded', 'Reembolsado'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='regular_bookings',
        verbose_name='Usuário'
    )
    class_obj = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='regular_bookings',
        verbose_name='Aula'
    )
    
    # Período
    start_date = models.DateField('Data de Início')
    end_date = models.DateField('Data de Término', null=True, blank=True)
    
    # Status
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='active')
    payment_status = models.CharField('Status do Pagamento', max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Pagamento
    monthly_fee = models.DecimalField('Taxa Mensal', max_digits=8, decimal_places=2)
    payment_due_day = models.IntegerField(
        'Dia de Vencimento',
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        default=5
    )
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Agendamento Regular'
        verbose_name_plural = 'Agendamentos Regulares'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.class_obj.name}"


class Attendance(models.Model):
    """Controle de presença nas aulas"""
    booking = models.ForeignKey(
        RegularBooking,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name='Agendamento'
    )
    schedule = models.ForeignKey(
        ClassSchedule,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name='Horário da Aula'
    )
    date = models.DateField('Data da Aula')
    attended = models.BooleanField('Compareceu', default=True)
    notes = models.TextField('Observações', blank=True)
    created_at = models.DateTimeField('Registrado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Presença'
        verbose_name_plural = 'Presenças'
        ordering = ['-date']
        unique_together = ['booking', 'date']

    def __str__(self):
        status = "Presente" if self.attended else "Faltou"
        return f"{self.booking.user.get_full_name()} - {self.date} ({status})"


class Payment(models.Model):
    """Controle de pagamentos"""
    PAYMENT_METHOD_CHOICES = [
        ('pix', 'PIX'),
        ('credit_card', 'Cartão de Crédito'),
        ('debit_card', 'Cartão de Débito'),
        ('cash', 'Dinheiro'),
        ('bank_transfer', 'Transferência Bancária'),
    ]

    booking = models.ForeignKey(
        RegularBooking,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Agendamento'
    )
    amount = models.DecimalField('Valor', max_digits=8, decimal_places=2)
    payment_date = models.DateField('Data do Pagamento')
    due_date = models.DateField('Data de Vencimento')
    payment_method = models.CharField('Método de Pagamento', max_length=20, choices=PAYMENT_METHOD_CHOICES)
    reference_month = models.DateField('Mês de Referência')
    notes = models.TextField('Observações', blank=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'
        ordering = ['-payment_date']

    def __str__(self):
        return f"{self.booking.user.get_full_name()} - R$ {self.amount} - {self.reference_month.strftime('%m/%Y')}"
