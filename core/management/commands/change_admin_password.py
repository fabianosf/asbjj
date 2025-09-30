"""
Comando para trocar a senha do administrador
Uso: python manage.py change_admin_password
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from getpass import getpass
import sys

User = get_user_model()


class Command(BaseCommand):
    help = 'Troca a senha do usuário administrador'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Nome de usuário do admin (padrão: admin)',
            default='admin'
        )

    def handle(self, *args, **options):
        username = options['username']
        
        self.stdout.write(self.style.WARNING(f'\n🔐 Alteração de Senha - Usuário: {username}\n'))
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ Usuário "{username}" não encontrado!'))
            self.stdout.write(self.style.WARNING('\n📋 Usuários disponíveis:'))
            
            admins = User.objects.filter(is_superuser=True)
            if admins.exists():
                for admin in admins:
                    self.stdout.write(f'   - {admin.username} (Email: {admin.email})')
            else:
                self.stdout.write(self.style.WARNING('   Nenhum superusuário encontrado.'))
            
            return
        
        if not user.is_superuser:
            self.stdout.write(self.style.WARNING(f'⚠️  Atenção: {username} não é um superusuário!'))
            confirm = input('Deseja continuar mesmo assim? (s/N): ').lower()
            if confirm != 's':
                self.stdout.write(self.style.WARNING('Operação cancelada.'))
                return
        
        # Informações do usuário
        self.stdout.write(f'\n📌 Informações do usuário:')
        self.stdout.write(f'   Username: {user.username}')
        self.stdout.write(f'   Email: {user.email or "Não definido"}')
        self.stdout.write(f'   Superusuário: {"Sim" if user.is_superuser else "Não"}')
        self.stdout.write(f'   Staff: {"Sim" if user.is_staff else "Não"}')
        self.stdout.write(f'   Ativo: {"Sim" if user.is_active else "Não"}')
        
        self.stdout.write(f'\n🔑 Digite a nova senha para {username}:')
        
        # Solicitar senha
        password1 = getpass('Nova senha: ')
        if not password1:
            self.stdout.write(self.style.ERROR('❌ Senha não pode ser vazia!'))
            return
        
        password2 = getpass('Confirme a senha: ')
        
        if password1 != password2:
            self.stdout.write(self.style.ERROR('❌ As senhas não coincidem!'))
            return
        
        # Validar tamanho mínimo
        if len(password1) < 8:
            self.stdout.write(self.style.WARNING('⚠️  Aviso: Senha muito curta! Recomenda-se no mínimo 8 caracteres.'))
            confirm = input('Deseja continuar mesmo assim? (s/N): ').lower()
            if confirm != 's':
                self.stdout.write(self.style.WARNING('Operação cancelada.'))
                return
        
        # Alterar senha
        try:
            user.set_password(password1)
            user.save()
            
            self.stdout.write(self.style.SUCCESS(f'\n✅ Senha alterada com sucesso para o usuário "{username}"!'))
            self.stdout.write(self.style.SUCCESS(f'   Você já pode fazer login com a nova senha.\n'))
            
            # Dica de segurança
            self.stdout.write(self.style.WARNING('💡 Dicas de segurança:'))
            self.stdout.write('   • Use senhas fortes com letras, números e símbolos')
            self.stdout.write('   • Não compartilhe sua senha com ninguém')
            self.stdout.write('   • Troque sua senha regularmente')
            self.stdout.write('   • Use senhas diferentes para cada serviço\n')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao alterar senha: {str(e)}'))
            return

