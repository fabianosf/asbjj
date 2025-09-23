from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Perfil estendido do usuário"""
    
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('instructor', 'Professor'),
        ('student', 'Aluno'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile',
        verbose_name='Usuário'
    )
    
    role = models.CharField(
        'Tipo de Usuário',
        max_length=20,
        choices=ROLE_CHOICES,
        default='student'
    )
    
    phone = models.CharField('Telefone', max_length=20, blank=True)
    whatsapp = models.CharField('WhatsApp', max_length=20, blank=True)
    
    # Para alunos
    student_profile = models.ForeignKey(
        'students.Student',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_profile',
        verbose_name='Perfil do Aluno'
    )
    
    # Para professores
    instructor_profile = models.ForeignKey(
        'core.Instructor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_profile',
        verbose_name='Perfil do Professor'
    )
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Perfil do Usuário'
        verbose_name_plural = 'Perfis dos Usuários'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_instructor(self):
        return self.role == 'instructor'

    @property
    def is_student(self):
        return self.role == 'student'
