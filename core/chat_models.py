"""
Modelos para sistema de chat de suporte
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ChatRoom(models.Model):
    """Sala de chat"""
    STATUS_CHOICES = [
        ('open', 'Aberta'),
        ('closed', 'Fechada'),
        ('waiting', 'Aguardando'),
    ]
    
    customer_email = models.EmailField('E-mail do Cliente')
    customer_name = models.CharField('Nome do Cliente', max_length=200)
    subject = models.CharField('Assunto', max_length=200)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='open')
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Atribuído a'
    )
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    closed_at = models.DateTimeField('Fechado em', null=True, blank=True)

    class Meta:
        verbose_name = 'Sala de Chat'
        verbose_name_plural = 'Salas de Chat'
        ordering = ['-updated_at']

    def __str__(self):
        return f"Chat - {self.customer_name} - {self.subject}"

    def close(self):
        """Fecha a sala de chat"""
        self.status = 'closed'
        self.closed_at = timezone.now()
        self.save()

    @property
    def is_open(self):
        return self.status == 'open'

    @property
    def last_message(self):
        return self.messages.last()


class ChatMessage(models.Model):
    """Mensagem do chat"""
    MESSAGE_TYPES = [
        ('customer', 'Cliente'),
        ('admin', 'Administrador'),
        ('system', 'Sistema'),
    ]
    
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Sala'
    )
    sender_type = models.CharField('Tipo do Remetente', max_length=20, choices=MESSAGE_TYPES)
    sender_name = models.CharField('Nome do Remetente', max_length=200)
    sender_email = models.EmailField('E-mail do Remetente', blank=True)
    message = models.TextField('Mensagem')
    is_read = models.BooleanField('Lida', default=False)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Mensagem do Chat'
        verbose_name_plural = 'Mensagens do Chat'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender_name}: {self.message[:50]}..."

    def mark_as_read(self):
        """Marca mensagem como lida"""
        self.is_read = True
        self.save()


class ChatAttachment(models.Model):
    """Anexo do chat"""
    message = models.ForeignKey(
        ChatMessage,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name='Mensagem'
    )
    file = models.FileField('Arquivo', upload_to='chat/attachments/')
    filename = models.CharField('Nome do Arquivo', max_length=255)
    file_size = models.PositiveIntegerField('Tamanho do Arquivo')
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Anexo do Chat'
        verbose_name_plural = 'Anexos do Chat'

    def __str__(self):
        return f"{self.filename} - {self.message}"

    @property
    def file_size_mb(self):
        """Tamanho do arquivo em MB"""
        return round(self.file_size / (1024 * 1024), 2)


class ChatTemplate(models.Model):
    """Template de resposta rápida"""
    name = models.CharField('Nome', max_length=100)
    subject = models.CharField('Assunto', max_length=200)
    content = models.TextField('Conteúdo')
    is_active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Template de Chat'
        verbose_name_plural = 'Templates de Chat'
        ordering = ['name']

    def __str__(self):
        return self.name
