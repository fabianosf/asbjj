from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Testimonial(models.Model):
    """Depoimentos de alunos"""
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
    ]

    # Informações do autor
    author_name = models.CharField('Nome do Autor', max_length=100)
    author_email = models.EmailField('E-mail do Autor', blank=True)
    author_age = models.PositiveIntegerField('Idade', null=True, blank=True)
    author_photo = models.ImageField(
        'Foto do Autor',
        upload_to='testimonials/photos/',
        blank=True,
        null=True
    )
    
    # Conteúdo do depoimento
    title = models.CharField('Título', max_length=200)
    content = models.TextField('Conteúdo')
    
    # Avaliação
    rating = models.IntegerField(
        'Avaliação (1-5)',
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5
    )
    
    # Relacionamento com aulas
    class_related = models.ForeignKey(
        'classes.Class',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='testimonials',
        verbose_name='Aula Relacionada'
    )
    
    # Status e moderação
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='pending')
    is_featured = models.BooleanField('Destaque', default=False)
    admin_notes = models.TextField('Observações Administrativas', blank=True)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    approved_at = models.DateTimeField('Aprovado em', null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_testimonials',
        verbose_name='Aprovado por'
    )

    class Meta:
        verbose_name = 'Depoimento'
        verbose_name_plural = 'Depoimentos'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author_name} - {self.title}"

    def approve(self, user=None):
        """Aprova o depoimento"""
        self.status = 'approved'
        self.approved_at = models.DateTimeField(auto_now=True)
        if user:
            self.approved_by = user
        self.save()

    def reject(self):
        """Rejeita o depoimento"""
        self.status = 'rejected'
        self.save()


class Review(models.Model):
    """Avaliações detalhadas de aulas específicas"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Usuário'
    )
    class_obj = models.ForeignKey(
        'classes.Class',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Aula'
    )
    
    # Avaliações específicas
    instructor_rating = models.IntegerField(
        'Avaliação do Instrutor',
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    content_rating = models.IntegerField(
        'Avaliação do Conteúdo',
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    facility_rating = models.IntegerField(
        'Avaliação da Instalação',
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    overall_rating = models.IntegerField(
        'Avaliação Geral',
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Conteúdo
    title = models.CharField('Título', max_length=200)
    content = models.TextField('Conteúdo')
    
    # Status
    is_verified = models.BooleanField('Verificado', default=False)
    is_featured = models.BooleanField('Destaque', default=False)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'
        ordering = ['-created_at']
        unique_together = ['user', 'class_obj']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.class_obj.name} ({self.overall_rating}⭐)"


class FAQ(models.Model):
    """Perguntas Frequentes"""
    CATEGORY_CHOICES = [
        ('general', 'Geral'),
        ('classes', 'Aulas'),
        ('schedule', 'Horários'),
        ('pricing', 'Preços'),
        ('equipment', 'Equipamentos'),
        ('safety', 'Segurança'),
    ]

    question = models.CharField('Pergunta', max_length=300)
    answer = models.TextField('Resposta')
    category = models.CharField('Categoria', max_length=20, choices=CATEGORY_CHOICES, default='general')
    order = models.PositiveIntegerField('Ordem', default=0)
    is_active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Pergunta Frequente'
        verbose_name_plural = 'Perguntas Frequentes'
        ordering = ['category', 'order', 'question']

    def __str__(self):
        return self.question
