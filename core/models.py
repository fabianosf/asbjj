from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
import uuid


class SiteSettings(models.Model):
    """Configurações gerais do site"""
    site_name = models.CharField('Nome do Site', max_length=200, default='ASBJJ')
    site_description = models.TextField('Descrição do Site', blank=True)
    site_logo = models.ImageField('Logo', upload_to='site/images/', blank=True, null=True)
    site_favicon = models.ImageField('Favicon', upload_to='site/images/', blank=True, null=True)
    
    # Informações de contato
    contact_email = models.EmailField('E-mail de Contato')
    contact_phone = models.CharField(
        'Telefone de Contato',
        max_length=20,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Formato de telefone inválido."
        )]
    )
    contact_address = models.TextField('Endereço', blank=True)
    contact_whatsapp = models.CharField('WhatsApp', max_length=20, blank=True)
    
    # Redes sociais
    instagram_url = models.URLField('Instagram', blank=True)
    facebook_url = models.URLField('Facebook', blank=True)
    youtube_url = models.URLField('YouTube', blank=True)
    tiktok_url = models.URLField('TikTok', blank=True)
    google_maps_url = models.URLField('Google Maps (embed/view URL)', blank=True)
    
    # SEO
    meta_title = models.CharField('Meta Title', max_length=200, blank=True)
    meta_description = models.TextField('Meta Description', blank=True)
    meta_keywords = models.TextField('Meta Keywords', blank=True)
    google_analytics_id = models.CharField('Google Analytics ID', max_length=20, blank=True)
    tawkto_property_id = models.CharField('Tawk.to Property ID', max_length=100, blank=True)
    
    # Configurações
    is_maintenance_mode = models.BooleanField('Modo Manutenção', default=False)
    maintenance_message = models.TextField('Mensagem de Manutenção', blank=True)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Configuração do Site'
        verbose_name_plural = 'Configurações do Site'

    def __str__(self):
        return f"Configurações - {self.site_name}"

    def save(self, *args, **kwargs):
        # Garantir que apenas uma instância exista
        if not self.pk and SiteSettings.objects.exists():
            raise ValueError('Apenas uma instância de SiteSettings é permitida')
        super().save(*args, **kwargs)


class ContactMessage(models.Model):
    """Mensagens de contato recebidas"""
    STATUS_CHOICES = [
        ('new', 'Nova'),
        ('read', 'Lida'),
        ('replied', 'Respondida'),
        ('archived', 'Arquivada'),
    ]

    # Informações do remetente
    name = models.CharField('Nome', max_length=200)
    email = models.EmailField('E-mail')
    phone = models.CharField('Telefone', max_length=20, blank=True)
    
    # Conteúdo da mensagem
    subject = models.CharField('Assunto', max_length=300, blank=True)
    message = models.TextField('Mensagem')
    
    # Categoria e prioridade
    category = models.CharField(
        'Categoria',
        max_length=50,
        choices=[
            ('general', 'Geral'),
            ('classes', 'Aulas'),
            ('schedule', 'Horários'),
            ('pricing', 'Preços'),
            ('complaint', 'Reclamação'),
            ('suggestion', 'Sugestão'),
        ],
        default='general'
    )
    priority = models.CharField(
        'Prioridade',
        max_length=20,
        choices=[
            ('low', 'Baixa'),
            ('normal', 'Normal'),
            ('high', 'Alta'),
            ('urgent', 'Urgente'),
        ],
        default='normal'
    )
    
    # Status e resposta
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='new')
    response = models.TextField('Resposta', blank=True)
    responded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contact_responses',
        verbose_name='Respondido por'
    )
    responded_at = models.DateTimeField('Respondido em', null=True, blank=True)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    ip_address = models.GenericIPAddressField('Endereço IP', null=True, blank=True)
    user_agent = models.TextField('User Agent', blank=True)

    class Meta:
        verbose_name = 'Mensagem de Contato'
        verbose_name_plural = 'Mensagens de Contato'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject or 'Sem assunto'}"


class Instructor(models.Model):
    """Instrutores da academia"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='instructor_profile',
        verbose_name='Usuário'
    )
    
    # Informações profissionais
    bio = models.TextField('Biografia', blank=True)
    experience_years = models.PositiveIntegerField('Anos de Experiência', default=0)
    certifications = models.JSONField('Certificações', default=list, blank=True)
    specializations = models.JSONField('Especializações', default=list, blank=True)
    
    # Foto e mídia
    photo = models.ImageField('Foto', upload_to='instructors/photos/', blank=True, null=True)
    social_links = models.JSONField('Links Sociais', default=dict, blank=True)
    
    # Status
    is_active = models.BooleanField('Ativo', default=True)
    is_featured = models.BooleanField('Destaque', default=False)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Instrutor'
        verbose_name_plural = 'Instrutores'
        ordering = ['user__first_name', 'user__last_name']

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username


class Gallery(models.Model):
    """Galeria de imagens do site"""
    title = models.CharField('Título', max_length=200)
    description = models.TextField('Descrição', blank=True)
    image = models.ImageField('Imagem', upload_to='gallery/images/')
    category = models.CharField(
        'Categoria',
        max_length=50,
        choices=[
            ('academy', 'Academia'),
            ('classes', 'Aulas'),
            ('events', 'Eventos'),
            ('graduations', 'Graduações'),
            ('competitions', 'Competições'),
            ('team', 'Equipe'),
        ],
        default='academy'
    )
    is_featured = models.BooleanField('Destaque', default=False)
    order = models.PositiveIntegerField('Ordem', default=0)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Imagem da Galeria'
        verbose_name_plural = 'Galeria de Imagens'
        ordering = ['category', 'order', '-created_at']

    def __str__(self):
        return self.title


class BlogPost(models.Model):
    """Posts do blog"""
    STATUS_CHOICES = [
        ('draft', 'Rascunho'),
        ('published', 'Publicado'),
        ('archived', 'Arquivado'),
    ]

    title = models.CharField('Título', max_length=300)
    slug = models.SlugField('Slug', unique=True)
    excerpt = models.TextField('Resumo', max_length=500)
    content = models.TextField('Conteúdo')
    
    # Imagens
    featured_image = models.ImageField('Imagem Destacada', upload_to='blog/images/', blank=True, null=True)
    
    # Autor e categoria
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blog_posts',
        verbose_name='Autor'
    )
    category = models.CharField(
        'Categoria',
        max_length=50,
        choices=[
            ('news', 'Notícias'),
            ('tips', 'Dicas'),
            ('techniques', 'Técnicas'),
            ('events', 'Eventos'),
            ('nutrition', 'Nutrição'),
            ('health', 'Saúde'),
        ],
        default='news'
    )
    
    # SEO
    meta_title = models.CharField('Meta Title', max_length=300, blank=True)
    meta_description = models.TextField('Meta Description', blank=True)
    
    # Status e visibilidade
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField('Destaque', default=False)
    allow_comments = models.BooleanField('Permitir Comentários', default=True)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    published_at = models.DateTimeField('Publicado em', null=True, blank=True)
    view_count = models.PositiveIntegerField('Visualizações', default=0)

    class Meta:
        verbose_name = 'Post do Blog'
        verbose_name_plural = 'Posts do Blog'
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('core:blog_detail', kwargs={'slug': self.slug})
