from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from students.user_models import UserProfile


class Command(BaseCommand):
    help = 'Utilitário: desmarca must_change_password para usuários informados (uso manual se necessário)'

    def add_arguments(self, parser):
        parser.add_argument('usernames', nargs='*', help='Usernames a atualizar')

    def handle(self, *args, **options):
        usernames = options.get('usernames', [])
        if not usernames:
            self.stdout.write('Informe ao menos um username.')
            return
        count = 0
        for uname in usernames:
            try:
                user = User.objects.get(username=uname)
                profile = user.student_profile
                if profile.must_change_password:
                    profile.must_change_password = False
                    profile.save(update_fields=['must_change_password'])
                    count += 1
                    self.stdout.write(f'Atualizado: {uname}')
            except (User.DoesNotExist, UserProfile.DoesNotExist):
                pass
        self.stdout.write(self.style.SUCCESS(f'Concluído. {count} perfis atualizados.'))


