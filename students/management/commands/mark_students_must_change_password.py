from django.core.management.base import BaseCommand
from students.user_models import UserProfile


class Command(BaseCommand):
    help = 'Marca todos os alunos para exigirem troca de senha no próximo login'

    def handle(self, *args, **options):
        updated = UserProfile.objects.filter(role='student', must_change_password=False).update(must_change_password=True)
        self.stdout.write(self.style.SUCCESS(f'Marcados {updated} perfis de alunos para troca de senha.'))


