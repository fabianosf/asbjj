from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.utils import timezone
from decimal import Decimal
import uuid


class Student(models.Model):
    """Modelo para alunos da academia"""
    
    # Informações pessoais
    first_name = models.CharField('Nome', max_length=100)
    last_name = models.CharField('Sobrenome', max_length=100)
    email = models.EmailField('E-mail', unique=True)
    phone = models.CharField(
        'Telefone',
        max_length=20,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Formato de telefone inválido."
        )]
    )
    whatsapp = models.CharField('WhatsApp', max_length=20, blank=True)
    
    # Documentos
    cpf = models.CharField(
        'CPF',
        max_length=14,
        unique=True,
        validators=[RegexValidator(
            regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
            message="Formato de CPF inválido."
        )]
    )
    rg = models.CharField('RG', max_length=20, blank=True)
    
    # Endereço
    address = models.TextField('Endereço')
    city = models.CharField('Cidade', max_length=100)
    state = models.CharField('Estado', max_length=2)
    zip_code = models.CharField('CEP', max_length=10)
    
    # Informações da academia
    belt_color = models.CharField(
        'Faixa',
        max_length=20,
        choices=[
            ('white', 'Branca'),
            ('blue', 'Azul'),
            ('purple', 'Roxa'),
            ('brown', 'Marrom'),
            ('black', 'Preta'),
        ],
        default='white'
    )
    enrollment_date = models.DateField('Data de Matrícula', default=timezone.now)
    is_active = models.BooleanField('Ativo', default=True)
    
    # Informações médicas
    birth_date = models.DateField('Data de Nascimento')
    emergency_contact_name = models.CharField('Nome do Contato de Emergência', max_length=200)
    emergency_contact_phone = models.CharField('Telefone do Contato de Emergência', max_length=20)
    medical_conditions = models.TextField('Condições Médicas', blank=True)
    allergies = models.TextField('Alergias', blank=True)
    
    # Foto
    photo = models.ImageField('Foto', upload_to='students/photos/', blank=True, null=True)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_students',
        verbose_name='Criado por'
    )

    class Meta:
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        today = timezone.now().date()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))


class PaymentPlan(models.Model):
    """Planos de pagamento disponíveis"""
    
    name = models.CharField('Nome do Plano', max_length=100)
    description = models.TextField('Descrição', blank=True)
    price = models.DecimalField('Preço', max_digits=10, decimal_places=2)
    duration_days = models.PositiveIntegerField('Duração (dias)', default=30)
    is_active = models.BooleanField('Ativo', default=True)
    
    # Configurações
    allows_unlimited_classes = models.BooleanField('Aulas Ilimitadas', default=False)
    max_classes_per_month = models.PositiveIntegerField('Máximo de Aulas por Mês', null=True, blank=True)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Plano de Pagamento'
        verbose_name_plural = 'Planos de Pagamento'
        ordering = ['price']

    def __str__(self):
        return f"{self.name} - R$ {self.price}"


class StudentSubscription(models.Model):
    """Assinaturas dos alunos"""
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='subscriptions', verbose_name='Aluno')
    payment_plan = models.ForeignKey(PaymentPlan, on_delete=models.CASCADE, verbose_name='Plano')
    
    # Datas
    start_date = models.DateField('Data de Início')
    end_date = models.DateField('Data de Fim')
    
    # Status
    STATUS_CHOICES = [
        ('active', 'Ativa'),
        ('expired', 'Expirada'),
        ('cancelled', 'Cancelada'),
        ('suspended', 'Suspensa'),
    ]
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Assinatura'
        verbose_name_plural = 'Assinaturas'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.full_name} - {self.payment_plan.name}"

    @property
    def is_active(self):
        today = timezone.now().date()
        return self.status == 'active' and self.start_date <= today <= self.end_date


class Payment(models.Model):
    """Pagamentos realizados pelos alunos"""
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Dinheiro'),
        ('pix', 'PIX'),
        ('credit_card', 'Cartão de Crédito'),
        ('debit_card', 'Cartão de Débito'),
        ('bank_transfer', 'Transferência Bancária'),
        ('check', 'Cheque'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('paid', 'Pago'),
        ('cancelled', 'Cancelado'),
        ('refunded', 'Reembolsado'),
    ]
    
    # Identificação única
    payment_id = models.UUIDField('ID do Pagamento', default=uuid.uuid4, unique=True)
    
    # Relacionamentos
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments', verbose_name='Aluno')
    subscription = models.ForeignKey(StudentSubscription, on_delete=models.CASCADE, related_name='payments', verbose_name='Assinatura')
    
    # Valores
    amount = models.DecimalField('Valor', max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField('Valor do Desconto', max_digits=10, decimal_places=2, default=0)
    final_amount = models.DecimalField('Valor Final', max_digits=10, decimal_places=2)
    
    # Informações do pagamento
    payment_method = models.CharField('Método de Pagamento', max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField('Status do Pagamento', max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Datas
    due_date = models.DateField('Data de Vencimento')
    paid_date = models.DateTimeField('Data do Pagamento', null=True, blank=True)
    
    # Observações
    notes = models.TextField('Observações', blank=True)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_payments',
        verbose_name='Criado por'
    )

    class Meta:
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.full_name} - R$ {self.final_amount} - {self.get_payment_status_display()}"

    def save(self, *args, **kwargs):
        # Calcular valor final
        self.final_amount = self.amount - self.discount_amount
        super().save(*args, **kwargs)


class PaymentReceipt(models.Model):
    """Comprovantes de pagamento"""
    
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='receipts', verbose_name='Pagamento')
    receipt_file = models.FileField('Arquivo do Comprovante', upload_to='payments/receipts/')
    receipt_type = models.CharField(
        'Tipo de Comprovante',
        max_length=20,
        choices=[
            ('pix', 'PIX'),
            ('bank_slip', 'Boleto'),
            ('credit_card', 'Cartão de Crédito'),
            ('receipt', 'Recibo'),
            ('other', 'Outro'),
        ]
    )
    
    # Metadados
    uploaded_at = models.DateTimeField('Enviado em', auto_now_add=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_receipts',
        verbose_name='Enviado por'
    )

    class Meta:
        verbose_name = 'Comprovante de Pagamento'
        verbose_name_plural = 'Comprovantes de Pagamento'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Comprovante - {self.payment.student.full_name}"


class Attendance(models.Model):
    """Controle de presença nas aulas"""
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances', verbose_name='Aluno')
    class_date = models.DateField('Data da Aula')
    class_time = models.TimeField('Horário da Aula')
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='taught_classes',
        verbose_name='Instrutor'
    )
    
    # Status da presença
    STATUS_CHOICES = [
        ('present', 'Presente'),
        ('absent', 'Ausente'),
        ('late', 'Atrasado'),
        ('excused', 'Justificado'),
    ]
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='present')
    
    # Observações
    notes = models.TextField('Observações', blank=True)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Presença'
        verbose_name_plural = 'Presenças'
        ordering = ['-class_date', '-class_time']
        unique_together = ['student', 'class_date', 'class_time']

    def __str__(self):
        return f"{self.student.full_name} - {self.class_date} {self.class_time}"