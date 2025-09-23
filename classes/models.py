from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class ClassCategory(models.Model):
    """Categoria de aulas (ex: Jiu-Jitsu, Defesa Pessoal, Yoga)"""
    name = models.CharField('Nome', max_length=100)
    slug = models.SlugField('Slug', unique=True)
    description = models.TextField('Descrição', blank=True)
    icon = models.CharField('Ícone (FontAwesome)', max_length=50, blank=True)
    color = models.CharField('Cor (hex)', max_length=7, default='#007bff')
    is_active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Categoria de Aula'
        verbose_name_plural = 'Categorias de Aulas'
        ordering = ['name']

    def __str__(self):
        return self.name


class ClassType(models.Model):
    """Tipo de aula (ex: Iniciante, Intermediário, Avançado)"""
    name = models.CharField('Nome', max_length=100)
    description = models.TextField('Descrição', blank=True)
    difficulty_level = models.IntegerField(
        'Nível de Dificuldade',
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        default=1
    )
    is_active = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Tipo de Aula'
        verbose_name_plural = 'Tipos de Aulas'
        ordering = ['difficulty_level', 'name']

    def __str__(self):
        return self.name


class Class(models.Model):
    """Modelo principal para as aulas"""
    category = models.ForeignKey(
        ClassCategory,
        on_delete=models.CASCADE,
        related_name='classes',
        verbose_name='Categoria'
    )
    name = models.CharField('Nome da Aula', max_length=200)
    slug = models.SlugField('Slug', unique=True)
    description = models.TextField('Descrição')
    short_description = models.CharField('Descrição Curta', max_length=300)
    
    # Informações da aula
    duration_minutes = models.PositiveIntegerField('Duração (minutos)', default=60)
    max_students = models.PositiveIntegerField('Máximo de Alunos', default=20)
    min_age = models.PositiveIntegerField('Idade Mínima', default=5)
    max_age = models.PositiveIntegerField('Idade Máxima', null=True, blank=True)
    
    # Preços
    price_monthly = models.DecimalField(
        'Preço Mensal',
        max_digits=8,
        decimal_places=2,
        default=0
    )
    price_single = models.DecimalField(
        'Preço por Aula',
        max_digits=8,
        decimal_places=2,
        default=0
    )
    
    # Imagens e mídia
    image = models.ImageField(
        'Imagem Principal',
        upload_to='classes/images/',
        blank=True,
        null=True
    )
    gallery = models.JSONField('Galeria de Imagens', default=list, blank=True)
    
    # Status e configurações
    is_active = models.BooleanField('Ativo', default=True)
    is_featured = models.BooleanField('Destaque', default=False)
    requires_registration = models.BooleanField('Requer Inscrição', default=True)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    # SEO
    meta_title = models.CharField('Meta Title', max_length=200, blank=True)
    meta_description = models.TextField('Meta Description', blank=True)

    class Meta:
        verbose_name = 'Aula'
        verbose_name_plural = 'Aulas'
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.category.name} - {self.name}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('classes:detail', kwargs={'slug': self.slug})


class ClassSchedule(models.Model):
    """Horários das aulas"""
    DAYS_OF_WEEK = [
        (0, 'Segunda-feira'),
        (1, 'Terça-feira'),
        (2, 'Quarta-feira'),
        (3, 'Quinta-feira'),
        (4, 'Sexta-feira'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]

    class_obj = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name='Aula'
    )
    day_of_week = models.IntegerField('Dia da Semana', choices=DAYS_OF_WEEK)
    start_time = models.TimeField('Horário de Início')
    end_time = models.TimeField('Horário de Término')
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='taught_classes',
        verbose_name='Instrutor'
    )
    location = models.CharField('Local', max_length=200, default='Tatame Principal')
    is_active = models.BooleanField('Ativo', default=True)
    max_capacity = models.PositiveIntegerField('Capacidade Máxima', default=20)
    current_enrolled = models.PositiveIntegerField('Inscritos Atuais', default=0)

    class Meta:
        verbose_name = 'Horário de Aula'
        verbose_name_plural = 'Horários de Aulas'
        ordering = ['day_of_week', 'start_time']
        unique_together = ['class_obj', 'day_of_week', 'start_time']

    def __str__(self):
        return f"{self.class_obj.name} - {self.get_day_of_week_display()} {self.start_time}"

    @property
    def is_available(self):
        return self.current_enrolled < self.max_capacity


class ClassEquipment(models.Model):
    """Equipamentos necessários para as aulas"""
    name = models.CharField('Nome', max_length=100)
    description = models.TextField('Descrição', blank=True)
    is_provided = models.BooleanField('Fornecido pela Academia', default=True)
    classes = models.ManyToManyField(
        Class,
        related_name='required_equipment',
        blank=True,
        verbose_name='Aulas que Requerem'
    )

    class Meta:
        verbose_name = 'Equipamento'
        verbose_name_plural = 'Equipamentos'
        ordering = ['name']

    def __str__(self):
        return self.name
