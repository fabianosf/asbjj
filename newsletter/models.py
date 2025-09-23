from django.db import models
from django.core.validators import RegexValidator
import uuid


class NewsletterSubscriber(models.Model):
    """Assinantes da newsletter"""
    email = models.EmailField('E-mail', unique=True)
    first_name = models.CharField('Nome', max_length=100, blank=True)
    last_name = models.CharField('Sobrenome', max_length=100, blank=True)
    phone = models.CharField(
        'Telefone',
        max_length=20,
        blank=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Formato de telefone inválido."
        )]
    )
    
    # Preferências
    interests = models.JSONField('Interesses', default=list, blank=True)
    frequency = models.CharField(
        'Frequência de Recebimento',
        max_length=20,
        choices=[
            ('weekly', 'Semanal'),
            ('monthly', 'Mensal'),
            ('promotions', 'Apenas Promoções'),
        ],
        default='monthly'
    )
    
    # Status
    is_active = models.BooleanField('Ativo', default=True)
    is_verified = models.BooleanField('Verificado', default=False)
    
    # Metadados
    subscription_date = models.DateTimeField('Data de Inscrição', auto_now_add=True)
    last_activity = models.DateTimeField('Última Atividade', auto_now=True)
    verification_token = models.UUIDField('Token de Verificação', default=uuid.uuid4, unique=True)
    unsubscribe_token = models.UUIDField('Token de Descadastro', default=uuid.uuid4, unique=True)
    
    # Dados adicionais
    source = models.CharField('Origem', max_length=100, default='website')
    ip_address = models.GenericIPAddressField('Endereço IP', null=True, blank=True)

    class Meta:
        verbose_name = 'Assinante da Newsletter'
        verbose_name_plural = 'Assinantes da Newsletter'
        ordering = ['-subscription_date']

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name} ({self.email})"
        return self.email

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return ""


class NewsletterCampaign(models.Model):
    """Campanhas de newsletter"""
    STATUS_CHOICES = [
        ('draft', 'Rascunho'),
        ('scheduled', 'Agendada'),
        ('sending', 'Enviando'),
        ('sent', 'Enviada'),
        ('cancelled', 'Cancelada'),
    ]

    title = models.CharField('Título', max_length=200)
    subject = models.CharField('Assunto do E-mail', max_length=300)
    preview_text = models.CharField('Texto de Prévia', max_length=300, blank=True)
    
    # Conteúdo
    content = models.TextField('Conteúdo HTML')
    plain_content = models.TextField('Conteúdo Texto Simples', blank=True)
    
    # Configurações
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_date = models.DateTimeField('Data Agendada', null=True, blank=True)
    
    # Segmentação
    target_segments = models.JSONField('Segmentos Alvo', default=list, blank=True)
    exclude_segments = models.JSONField('Segmentos Excluídos', default=list, blank=True)
    
    # Estatísticas
    total_sent = models.PositiveIntegerField('Total Enviado', default=0)
    total_delivered = models.PositiveIntegerField('Total Entregue', default=0)
    total_opened = models.PositiveIntegerField('Total Aberto', default=0)
    total_clicked = models.PositiveIntegerField('Total Cliques', default=0)
    total_unsubscribed = models.PositiveIntegerField('Total Descadastros', default=0)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    sent_at = models.DateTimeField('Enviado em', null=True, blank=True)
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_campaigns',
        verbose_name='Criado por'
    )

    class Meta:
        verbose_name = 'Campanha de Newsletter'
        verbose_name_plural = 'Campanhas de Newsletter'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class NewsletterTemplate(models.Model):
    """Templates para newsletters"""
    name = models.CharField('Nome', max_length=100)
    description = models.TextField('Descrição', blank=True)
    html_template = models.TextField('Template HTML')
    css_styles = models.TextField('Estilos CSS', blank=True)
    is_active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Template de Newsletter'
        verbose_name_plural = 'Templates de Newsletter'
        ordering = ['name']

    def __str__(self):
        return self.name


class EmailLog(models.Model):
    """Log de e-mails enviados"""
    subscriber = models.ForeignKey(
        NewsletterSubscriber,
        on_delete=models.CASCADE,
        related_name='email_logs',
        verbose_name='Assinante'
    )
    campaign = models.ForeignKey(
        NewsletterCampaign,
        on_delete=models.CASCADE,
        related_name='email_logs',
        verbose_name='Campanha',
        null=True,
        blank=True
    )
    
    # Status do envio
    status = models.CharField(
        'Status',
        max_length=20,
        choices=[
            ('sent', 'Enviado'),
            ('delivered', 'Entregue'),
            ('opened', 'Aberto'),
            ('clicked', 'Clicado'),
            ('bounced', 'Retornou'),
            ('unsubscribed', 'Descadastrado'),
        ]
    )
    
    # Dados do e-mail
    subject = models.CharField('Assunto', max_length=300)
    recipient_email = models.EmailField('E-mail Destinatário')
    
    # Metadados
    sent_at = models.DateTimeField('Enviado em', auto_now_add=True)
    opened_at = models.DateTimeField('Aberto em', null=True, blank=True)
    clicked_at = models.DateTimeField('Clicado em', null=True, blank=True)
    
    # Dados técnicos
    message_id = models.CharField('ID da Mensagem', max_length=255, blank=True)
    bounce_reason = models.TextField('Motivo do Retorno', blank=True)
    user_agent = models.TextField('User Agent', blank=True)
    ip_address = models.GenericIPAddressField('Endereço IP', null=True, blank=True)

    class Meta:
        verbose_name = 'Log de E-mail'
        verbose_name_plural = 'Logs de E-mails'
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.recipient_email} - {self.subject} ({self.status})"
