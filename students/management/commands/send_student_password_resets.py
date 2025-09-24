from django.core.management.base import BaseCommand
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.conf import settings

from students.user_models import UserProfile


class Command(BaseCommand):
    help = 'Envia e-mails de redefinição de senha para todos os alunos com e-mail válido'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Apenas mostra os emails que seriam enviados, sem enviar')

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        self.stdout.write('Coletando alunos com e-mail...')

        student_profiles = UserProfile.objects.select_related('user').filter(role='student', user__isnull=False, user__email__isnull=False).exclude(user__email='').order_by('user__email')
        emails = []
        for profile in student_profiles:
            email = profile.user.email
            if email and email not in emails:
                emails.append(email)

        if not emails:
            self.stdout.write(self.style.WARNING('Nenhum e-mail de aluno encontrado.'))
            return

        self.stdout.write(f'Encontrados {len(emails)} e-mails de alunos.')

        if dry_run:
            for e in emails:
                self.stdout.write(f'Would send reset to: {e}')
            self.stdout.write(self.style.SUCCESS('Dry-run concluído.'))
            return

        form = PasswordResetForm()
        sent_count = 0
        for chunk_start in range(0, len(emails), 50):
            # Enviar em pequenos lotes
            batch = emails[chunk_start:chunk_start + 50]
            form = PasswordResetForm({ 'email': ','.join(batch) })
            # PasswordResetForm espera um único email; enviar individualmente
            for email in batch:
                form = PasswordResetForm({ 'email': email })
                if form.is_valid():
                    form.save(
                        use_https=False,
                        request=None,
                        email_template_name='registration/password_reset_email.html',
                        subject_template_name='registration/password_reset_subject.txt',
                        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                    )
                    sent_count += 1
                    self.stdout.write(f'Email de redefinição enviado para: {email}')

        self.stdout.write(self.style.SUCCESS(f'Concluído. {sent_count} e-mails de redefinição enviados.'))


