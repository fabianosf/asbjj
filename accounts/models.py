from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import date


class UserProfile(models.Model):
    """Perfil estendido do usuário"""
    GENDER_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
        ('N', 'Prefiro não informar'),
    ]

    EMERGENCY_CONTACT_CHOICES = [
        ('parent', 'Pai/Mãe'),
        ('spouse', 'Cônjuge'),
        ('sibling', 'Irmão/Irmã'),
        ('friend', 'Amigo/Amiga'),
        ('other', 'Outro'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Usuário'
    )
    
    # Informações pessoais
    phone = models.CharField(
        'Telefone',
        max_length=20,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Formato de telefone inválido."
        )],
        blank=True
    )
    birth_date = models.DateField('Data de Nascimento', null=True, blank=True)
    gender = models.CharField('Gênero', max_length=1, choices=GENDER_CHOICES, blank=True)
    cpf = models.CharField(
        'CPF',
        max_length=14,
        unique=True,
        null=True,
        blank=True,
        validators=[RegexValidator(
            regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
            message="Formato de CPF inválido."
        )]
    )
    
    # Endereço
    address = models.TextField('Endereço', blank=True)
    city = models.CharField('Cidade', max_length=100, blank=True)
    state = models.CharField('Estado', max_length=2, blank=True)
    zip_code = models.CharField('CEP', max_length=10, blank=True)
    
    # Informações médicas
    medical_conditions = models.TextField('Condições Médicas', blank=True)
    medications = models.TextField('Medicamentos', blank=True)
    allergies = models.TextField('Alergias', blank=True)
    emergency_contact_name = models.CharField('Nome do Contato de Emergência', max_length=200, blank=True)
    emergency_contact_phone = models.CharField('Telefone do Contato de Emergência', max_length=20, blank=True)
    emergency_contact_relationship = models.CharField(
        'Relacionamento',
        max_length=20,
        choices=EMERGENCY_CONTACT_CHOICES,
        blank=True
    )
    
    # Informações da academia
    student_id = models.CharField('ID do Aluno', max_length=20, unique=True, null=True, blank=True)
    belt_color = models.CharField('Cor da Faixa', max_length=50, blank=True)
    join_date = models.DateField('Data de Ingresso', default=timezone.now)
    is_active_student = models.BooleanField('Aluno Ativo', default=True)
    
    # Foto e preferências
    photo = models.ImageField('Foto', upload_to='profiles/photos/', blank=True, null=True)
    bio = models.TextField('Biografia', blank=True)
    preferences = models.JSONField('Preferências', default=dict, blank=True)
    
    # Configurações de notificação
    email_notifications = models.BooleanField('Notificações por E-mail', default=True)
    sms_notifications = models.BooleanField('Notificações por SMS', default=False)
    whatsapp_notifications = models.BooleanField('Notificações por WhatsApp', default=True)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    last_login_ip = models.GenericIPAddressField('Último IP de Login', null=True, blank=True)

    class Meta:
        verbose_name = 'Perfil do Usuário'
        verbose_name_plural = 'Perfis dos Usuários'
        ordering = ['user__first_name', 'user__last_name']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def age(self):
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None

    @property
    def is_minor(self):
        return self.age is not None and self.age < 18

    def generate_student_id(self):
        """Gera um ID único para o aluno"""
        if not self.student_id:
            from datetime import datetime
            year = datetime.now().year
            last_student = UserProfile.objects.filter(
                student_id__startswith=str(year)
            ).order_by('-student_id').first()
            
            if last_student and last_student.student_id:
                try:
                    last_number = int(last_student.student_id.split('-')[-1])
                    new_number = last_number + 1
                except (ValueError, IndexError):
                    new_number = 1
            else:
                new_number = 1
            
            self.student_id = f"{year}-{new_number:04d}"
            self.save()

    def save(self, *args, **kwargs):
        if not self.student_id and self.is_active_student:
            self.generate_student_id()
        super().save(*args, **kwargs)


class UserActivity(models.Model):
    """Log de atividades do usuário"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name='Usuário'
    )
    action = models.CharField('Ação', max_length=100)
    description = models.TextField('Descrição', blank=True)
    ip_address = models.GenericIPAddressField('Endereço IP', null=True, blank=True)
    user_agent = models.TextField('User Agent', blank=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Atividade do Usuário'
        verbose_name_plural = 'Atividades dos Usuários'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.action}"


class UserSession(models.Model):
    """Sessões de usuário para controle de login"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sessions',
        verbose_name='Usuário'
    )
    session_key = models.CharField('Chave da Sessão', max_length=40, unique=True)
    ip_address = models.GenericIPAddressField('Endereço IP')
    user_agent = models.TextField('User Agent')
    is_active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    last_activity = models.DateTimeField('Última Atividade', auto_now=True)

    class Meta:
        verbose_name = 'Sessão do Usuário'
        verbose_name_plural = 'Sessões dos Usuários'
        ordering = ['-last_activity']

    def __str__(self):
        return f"{self.user.username} - {self.ip_address}"
