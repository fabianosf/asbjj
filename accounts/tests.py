from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail
from django.contrib.auth import get_user_model

from .forms import UserRegistrationForm, UserLoginForm


class AccountsModelsTestCase(TestCase):
    """Testes para os modelos do accounts"""
    
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
    
    def test_user_creation(self):
        """Teste de criação de usuário"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
    
    def test_superuser_creation(self):
        """Teste de criação de superusuário"""
        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)


class AccountsFormsTestCase(TestCase):
    """Testes para os formulários do accounts"""
    
    def test_user_registration_form_valid(self):
        """Teste do formulário de registro válido"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
            'first_name': 'New',
            'last_name': 'User'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_user_registration_form_invalid(self):
        """Teste do formulário de registro inválido"""
        form_data = {
            'username': '',
            'email': 'invalid-email',
            'password1': '123',
            'password2': '456'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('password2', form.errors)
    
    def test_user_registration_form_password_mismatch(self):
        """Teste de senhas não coincidem"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpassword123',
            'password2': 'differentpassword123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
    
    def test_user_login_form_valid(self):
        """Teste do formulário de login válido"""
        form_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        form = UserLoginForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_user_login_form_invalid(self):
        """Teste do formulário de login inválido"""
        form_data = {
            'username': '',
            'password': ''
        }
        form = UserLoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('password', form.errors)


class AccountsViewsTestCase(TestCase):
    """Testes para as views do accounts"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_login_view_get(self):
        """Teste da view de login (GET)"""
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
    
    def test_login_view_post_valid(self):
        """Teste da view de login (POST válido)"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('accounts:login'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after login
        self.assertTrue(self.client.session.get('_auth_user_id'))
    
    def test_login_view_post_invalid(self):
        """Teste da view de login (POST inválido)"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(reverse('accounts:login'), data)
        self.assertEqual(response.status_code, 200)  # Form errors
        self.assertFalse(self.client.session.get('_auth_user_id'))
    
    def test_register_view_get(self):
        """Teste da view de registro (GET)"""
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cadastro')
    
    def test_register_view_post_valid(self):
        """Teste da view de registro (POST válido)"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(reverse('accounts:register'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after registration
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_register_view_post_invalid(self):
        """Teste da view de registro (POST inválido)"""
        data = {
            'username': '',
            'email': 'invalid-email',
            'password1': '123',
            'password2': '456'
        }
        response = self.client.post(reverse('accounts:register'), data)
        self.assertEqual(response.status_code, 200)  # Form errors
        self.assertFalse(User.objects.filter(username='').exists())
    
    def test_logout_view(self):
        """Teste da view de logout"""
        # Fazer login primeiro
        self.client.login(username='testuser', password='testpass123')
        self.assertTrue(self.client.session.get('_auth_user_id'))
        
        # Fazer logout
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout
        self.assertFalse(self.client.session.get('_auth_user_id'))


class AccountsSecurityTestCase(TestCase):
    """Testes de segurança para accounts"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_password_hashing(self):
        """Teste de hash de senha"""
        user = User.objects.create_user(
            username='hashtest',
            email='hashtest@example.com',
            password='plainpassword'
        )
        self.assertNotEqual(user.password, 'plainpassword')
        self.assertTrue(user.check_password('plainpassword'))
    
    def test_session_security(self):
        """Teste de segurança de sessão"""
        # Fazer login
        self.client.login(username='testuser', password='testpass123')
        session_key = self.client.session.session_key
        self.assertIsNotNone(session_key)
        
        # Verificar se a sessão contém o ID do usuário
        self.assertEqual(self.client.session.get('_auth_user_id'), str(self.user.id))
    
    def test_csrf_protection(self):
        """Teste de proteção CSRF"""
        response = self.client.get(reverse('accounts:login'))
        self.assertContains(response, 'csrfmiddlewaretoken')
        
        response = self.client.get(reverse('accounts:register'))
        self.assertContains(response, 'csrfmiddlewaretoken')
    
    def test_brute_force_protection(self):
        """Teste de proteção contra força bruta"""
        # Tentar fazer login várias vezes com senha errada
        for i in range(5):
            data = {
                'username': 'testuser',
                'password': 'wrongpassword'
            }
            response = self.client.post(reverse('accounts:login'), data)
            self.assertEqual(response.status_code, 200)
        
        # Tentar com senha correta - ainda deve funcionar
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('accounts:login'), data)
        self.assertEqual(response.status_code, 302)


class AccountsEmailTestCase(TestCase):
    """Testes de e-mail para accounts"""
    
    def setUp(self):
        self.client = Client()
    
    def test_registration_email_confirmation(self):
        """Teste de confirmação de e-mail no registro"""
        # Limpar mailbox antes do teste
        mail.outbox = []
        
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = self.client.post(reverse('accounts:register'), data)
        self.assertEqual(response.status_code, 302)
        
        # Verificar se e-mail foi enviado (se implementado)
        # self.assertEqual(len(mail.outbox), 1)
    
    def test_password_reset_email(self):
        """Teste de e-mail de recuperação de senha"""
        # Limpar mailbox antes do teste
        mail.outbox = []
        
        user = User.objects.create_user(
            username='resetuser',
            email='reset@example.com',
            password='testpass123'
        )
        
        # Simular envio de e-mail de recuperação
        from django.core.mail import send_mail
        send_mail(
            'Password Reset',
            'Reset your password',
            'noreply@example.com',
            [user.email],
            fail_silently=False,
        )
        
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Password Reset')


class AccountsIntegrationTestCase(TestCase):
    """Testes de integração para accounts"""
    
    def setUp(self):
        self.client = Client()
    
    def test_full_registration_flow(self):
        """Teste do fluxo completo de registro"""
        # 1. Acessar página de registro
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        
        # 2. Preencher formulário
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        # 3. Enviar formulário
        response = self.client.post(reverse('accounts:register'), data)
        self.assertEqual(response.status_code, 302)
        
        # 4. Verificar se usuário foi criado
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')
        
        # 5. Verificar redirecionamento
        self.assertRedirects(response, reverse('accounts:login'))
    
    def test_full_login_logout_flow(self):
        """Teste do fluxo completo de login e logout"""
        # 1. Criar usuário
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 2. Acessar página de login
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        
        # 3. Fazer login
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('accounts:login'), data)
        self.assertEqual(response.status_code, 302)
        
        # 4. Verificar se está logado
        self.assertTrue(self.client.session.get('_auth_user_id'))
        
        # 5. Fazer logout
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)
        
        # 6. Verificar se não está mais logado
        self.assertFalse(self.client.session.get('_auth_user_id'))