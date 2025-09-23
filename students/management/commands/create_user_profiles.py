from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from students.user_models import UserProfile
from students.models import Student


class Command(BaseCommand):
    help = 'Cria perfis de usuário para usuários existentes'

    def handle(self, *args, **options):
        self.stdout.write('Criando perfis de usuário...')
        
        # Criar perfil para o usuário admin
        admin_user = User.objects.filter(username='admin').first()
        if admin_user:
            profile, created = UserProfile.objects.get_or_create(
                user=admin_user,
                defaults={
                    'role': 'admin',
                    'phone': '+5511999999999',
                }
            )
            if created:
                self.stdout.write(f'Criado perfil admin para {admin_user.username}')
        
        # Criar perfil para o usuário fabianosf
        fabiano_user = User.objects.filter(username='fabianosf').first()
        if fabiano_user:
            profile, created = UserProfile.objects.get_or_create(
                user=fabiano_user,
                defaults={
                    'role': 'admin',
                    'phone': '+5511999999999',
                }
            )
            if created:
                self.stdout.write(f'Criado perfil admin para {fabiano_user.username}')
        
        # Criar perfis de alunos para os alunos existentes
        students = Student.objects.all()
        for student in students:
            # Criar usuário para o aluno se não existir
            username = student.email.split('@')[0]
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': student.first_name,
                    'last_name': student.last_name,
                    'email': student.email,
                }
            )
            
            if created:
                user.set_password('123456')  # Senha padrão
                user.save()
                self.stdout.write(f'Criado usuário para aluno {student.full_name}')
            
            # Criar perfil do aluno
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': 'student',
                    'phone': student.phone,
                    'whatsapp': student.whatsapp,
                    'student_profile': student,
                }
            )
            
            if created:
                self.stdout.write(f'Criado perfil de aluno para {student.full_name}')
        
        # Criar um usuário professor de exemplo
        instructor_user, created = User.objects.get_or_create(
            username='professor',
            defaults={
                'first_name': 'Alexandre',
                'last_name': 'Salgado',
                'email': 'professor@asbjj.com.br',
            }
        )
        
        if created:
            instructor_user.set_password('123456')
            instructor_user.save()
            self.stdout.write('Criado usuário professor')
        
        # Criar perfil do professor
        instructor_profile, created = UserProfile.objects.get_or_create(
            user=instructor_user,
            defaults={
                'role': 'instructor',
                'phone': '+5511999999999',
            }
        )
        
        if created:
            self.stdout.write('Criado perfil de professor')
        
        self.stdout.write(
            self.style.SUCCESS('Perfis de usuário criados com sucesso!')
        )
        
        self.stdout.write('\nUsuários criados:')
        self.stdout.write('- admin / admin (Administrador)')
        self.stdout.write('- fabianosf / fabianosf (Administrador)')
        self.stdout.write('- professor / 123456 (Professor)')
        self.stdout.write('- [email do aluno] / 123456 (Aluno)')

