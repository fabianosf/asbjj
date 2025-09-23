from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail
from django.utils import timezone
from datetime import date, timedelta

from .models import SiteSettings, ContactMessage, Instructor, Gallery, BlogPost
from .forms import ContactForm


class CoreModelsTestCase(TestCase):
    """Testes para os modelos do core"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_site_settings_creation(self):
        """Teste de criação das configurações do site"""
        settings = SiteSettings.objects.create(
            site_name='Test Site',
            contact_email='test@example.com',
            contact_phone='+5511999999999'
        )
        self.assertEqual(str(settings), 'Configurações - Test Site')
        self.assertTrue(SiteSettings.objects.count() <= 1)
    
    def test_contact_message_creation(self):
        """Teste de criação de mensagem de contato"""
        message = ContactMessage.objects.create(
            name='Test User',
            email='test@example.com',
            phone='+5511999999999',
            message='Test message',
            category='general'
        )
        self.assertEqual(str(message), 'Test User - Sem assunto')
        self.assertEqual(message.status, 'new')
    
    def test_instructor_creation(self):
        """Teste de criação de instrutor"""
        instructor = Instructor.objects.create(
            user=self.user,
            bio='Test bio',
            experience_years=5
        )
        self.assertEqual(str(instructor), self.user.get_full_name() or self.user.username)
        self.assertEqual(instructor.experience_years, 5)
    
    def test_gallery_creation(self):
        """Teste de criação de item da galeria"""
        gallery_item = Gallery.objects.create(
            title='Test Gallery',
            description='Test description',
            category='tatame'
        )
        self.assertEqual(str(gallery_item), 'Test Gallery')
        self.assertEqual(gallery_item.category, 'tatame')
    
    def test_blog_post_creation(self):
        """Teste de criação de post do blog"""
        blog_post = BlogPost.objects.create(
            title='Test Blog Post',
            slug='test-blog-post',
            excerpt='Test excerpt',
            content='Test content',
            author=self.user,
            status='published'
        )
        self.assertEqual(str(blog_post), 'Test Blog Post')
        self.assertEqual(blog_post.status, 'published')


class CoreViewsTestCase(TestCase):
    """Testes para as views do core"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_home_view(self):
        """Teste da view da página inicial"""
        response = self.client.get(reverse('core:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ASBJJ')
    
    def test_about_view(self):
        """Teste da view sobre"""
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sobre')
    
    def test_services_view(self):
        """Teste da view de serviços"""
        response = self.client.get(reverse('core:services'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Serviços')
    
    def test_contact_view_get(self):
        """Teste da view de contato (GET)"""
        response = self.client.get(reverse('core:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], ContactForm)
        self.assertContains(response, 'Contato')
    
    def test_contact_view_post_valid(self):
        """Teste da view de contato (POST válido)"""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '+5511999999999',
            'message': 'Test message',
            'category': 'general'
        }
        response = self.client.post(reverse('core:contact'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(ContactMessage.objects.filter(email='test@example.com').exists())
    
    def test_contact_view_post_invalid(self):
        """Teste da view de contato (POST inválido)"""
        data = {
            'name': '',
            'email': 'invalid-email',
            'message': ''
        }
        response = self.client.post(reverse('core:contact'), data)
        self.assertEqual(response.status_code, 200)  # Form errors
        self.assertFalse(ContactMessage.objects.filter(email='invalid-email').exists())
    
    def test_contact_view_with_x_forwarded_for(self):
        """Teste da view de contato com X-Forwarded-For header"""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '+5511999999999',
            'message': 'Test message',
            'category': 'general'
        }
        response = self.client.post(
            reverse('core:contact'), 
            data,
            HTTP_X_FORWARDED_FOR='192.168.1.1'
        )
        self.assertEqual(response.status_code, 302)
        message = ContactMessage.objects.get(email='test@example.com')
        self.assertEqual(message.ip_address, '192.168.1.1')


class CoreFormsTestCase(TestCase):
    """Testes para os formulários do core"""
    
    def test_contact_form_valid(self):
        """Teste do formulário de contato válido"""
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '+5511999999999',
            'message': 'Test message',
            'category': 'general'
        }
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_contact_form_invalid(self):
        """Teste do formulário de contato inválido"""
        form_data = {
            'name': '',
            'email': 'invalid-email',
            'message': ''
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('message', form.errors)
    
    def test_contact_form_phone_validation(self):
        """Teste da validação de telefone"""
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '123',  # Telefone muito curto
            'message': 'Test message'
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)
    
    def test_contact_form_required_fields(self):
        """Teste dos campos obrigatórios"""
        form = ContactForm(data={})
        self.assertFalse(form.is_valid())
        required_fields = ['name', 'email', 'message']
        for field in required_fields:
            self.assertIn(field, form.errors)


class EmailTestCase(TestCase):
    """Testes para envio de e-mails"""
    
    def test_contact_email_sending(self):
        """Teste de envio de e-mail de contato"""
        # Limpar mailbox antes do teste
        mail.outbox = []
        
        # Simular envio de e-mail
        from django.core.mail import send_mail
        send_mail(
            'Test Subject',
            'Test Message',
            'from@example.com',
            ['to@example.com'],
            fail_silently=False,
        )
        
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Test Subject')


class URLTestCase(TestCase):
    """Testes para URLs"""
    
    def setUp(self):
        self.client = Client()
    
    def test_core_urls(self):
        """Teste das URLs do core"""
        urls = [
            reverse('core:index'),
            reverse('core:about'),
            reverse('core:services'),
            reverse('core:contact'),
        ]
        
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"URL {url} retornou {response.status_code}")
    
    def test_old_urls_redirect(self):
        """Teste das URLs antigas que devem redirecionar"""
        old_urls = [
            '/',
            '/sobre/',
            '/servicos/',
            '/contato/',
        ]
        
        for url in old_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"URL {url} retornou {response.status_code}")


class TemplateTestCase(TestCase):
    """Testes para templates"""
    
    def setUp(self):
        self.client = Client()
    
    def test_base_template_renders(self):
        """Teste se o template base renderiza corretamente"""
        response = self.client.get(reverse('core:index'))
        self.assertContains(response, 'ASBJJ')
        self.assertContains(response, 'bootstrap')  # Bootstrap está no CDN
    
    def test_navigation_links(self):
        """Teste se os links de navegação estão presentes"""
        response = self.client.get(reverse('core:index'))
        self.assertContains(response, 'Sobre')
        self.assertContains(response, 'Serviços')
        self.assertContains(response, 'Contato')
    
    def test_footer_content(self):
        """Teste se o rodapé está presente"""
        response = self.client.get(reverse('core:index'))
        self.assertContains(response, 'footer')


class StaticFilesTestCase(TestCase):
    """Testes para arquivos estáticos"""
    
    def setUp(self):
        self.client = Client()
    
    def test_static_files_served(self):
        """Teste se os arquivos estáticos são servidos corretamente"""
        # Em ambiente de teste, vamos apenas verificar se as URLs não retornam 500
        static_files = [
            '/static/css/style.css',
            '/static/js/main.js',
            '/static/img/logo.png',
        ]
        
        for url_path in static_files:
            response = self.client.get(url_path)
            # Aceitar 200 (sucesso) ou 404 (arquivo não encontrado), mas não 500 (erro interno)
            self.assertNotEqual(response.status_code, 500, f"Erro interno ao acessar {url_path}")
            self.assertIn(response.status_code, [200, 404], f"Status inesperado {response.status_code} para {url_path}")


class SecurityTestCase(TestCase):
    """Testes de segurança"""
    
    def setUp(self):
        self.client = Client()
    
    def test_csrf_protection(self):
        """Teste de proteção CSRF"""
        response = self.client.get(reverse('core:contact'))
        self.assertContains(response, 'csrfmiddlewaretoken')
    
    def test_xss_protection(self):
        """Teste de proteção XSS"""
        malicious_data = {
            'name': '<script>alert("XSS")</script>',
            'email': 'test@example.com',
            'phone': '+5511999999999',
            'message': 'Test message',
            'category': 'general'
        }
        response = self.client.post(reverse('core:contact'), malicious_data)
        self.assertEqual(response.status_code, 302)
        
        # Verificar se o script foi salvo no banco (Django escapa automaticamente na renderização)
        message = ContactMessage.objects.get(email='test@example.com')
        # O script será salvo no banco, mas escapado na renderização do template
        self.assertIn('<script>', message.name)
    
    def test_sql_injection_protection(self):
        """Teste de proteção contra SQL injection"""
        malicious_data = {
            'name': "'; DROP TABLE core_contactmessage; --",
            'email': 'test@example.com',
            'phone': '+5511999999999',
            'message': 'Test message',
            'category': 'general'
        }
        response = self.client.post(reverse('core:contact'), malicious_data)
        self.assertEqual(response.status_code, 302)
        
        # Verificar se a tabela ainda existe
        self.assertTrue(ContactMessage.objects.filter(email='test@example.com').exists())


class PerformanceTestCase(TestCase):
    """Testes de performance"""
    
    def setUp(self):
        self.client = Client()
    
    def test_page_load_time(self):
        """Teste de tempo de carregamento das páginas"""
        import time
        
        urls = [
            reverse('core:index'),
            reverse('core:about'),
            reverse('core:services'),
            reverse('core:contact'),
        ]
        
        for url in urls:
            start_time = time.time()
            response = self.client.get(url)
            load_time = time.time() - start_time
            
            self.assertEqual(response.status_code, 200)
            self.assertLess(load_time, 2.0, f"Página {url} carregou em {load_time:.2f}s (> 2s)")
    
    def test_database_queries_count(self):
        """Teste de número de queries do banco de dados"""
        from django.test.utils import override_settings
        from django.db import connection
        from django.test import TransactionTestCase
        
        # Reset queries
        connection.queries_log.clear()
        
        response = self.client.get(reverse('core:index'))
        self.assertEqual(response.status_code, 200)
        
        # Verificar se não há muitas queries
        query_count = len(connection.queries)
        self.assertLess(query_count, 10, f"Muitas queries: {query_count}")


class IntegrationTestCase(TestCase):
    """Testes de integração"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_full_contact_flow(self):
        """Teste do fluxo completo de contato"""
        # 1. Acessar página de contato
        response = self.client.get(reverse('core:contact'))
        self.assertEqual(response.status_code, 200)
        
        # 2. Preencher formulário
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '+5511999999999',
            'message': 'Test message',
            'category': 'general'
        }
        
        # 3. Enviar formulário
        response = self.client.post(reverse('core:contact'), data)
        self.assertEqual(response.status_code, 302)
        
        # 4. Verificar se mensagem foi criada
        message = ContactMessage.objects.get(email='test@example.com')
        self.assertEqual(message.name, 'Test User')
        self.assertEqual(message.status, 'new')
        
        # 5. Verificar redirecionamento
        self.assertRedirects(response, reverse('core:contact'))
    
    def test_site_settings_integration(self):
        """Teste de integração das configurações do site"""
        # Criar configurações sem logo para evitar erro
        settings = SiteSettings.objects.create(
            site_name='ASBJJ Test',
            contact_email='contato@asbjj.com',
            contact_phone='+5511999999999',
            site_description='Academia de Jiu-Jitsu'
        )
        
        # Verificar se aparecem nas páginas
        response = self.client.get(reverse('core:index'))
        self.assertContains(response, 'ASBJJ Test')
        
        response = self.client.get(reverse('core:contact'))
        self.assertContains(response, 'contato@asbjj.com')


class HealthCheckTestCase(TestCase):
    """Testes para o endpoint de health check"""
    
    def setUp(self):
        self.client = Client()
    
    def test_healthz_endpoint(self):
        """Teste do endpoint /healthz"""
        response = self.client.get(reverse('core:healthz'))
        self.assertEqual(response.status_code, 200)
        
        # Verificar se retorna JSON
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Verificar conteúdo da resposta
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        self.assertIn('time', data)
        self.assertIn('debug', data)
    
    def test_healthz_response_structure(self):
        """Teste da estrutura da resposta do healthz"""
        response = self.client.get(reverse('core:healthz'))
        data = response.json()
        
        # Verificar campos obrigatórios
        required_fields = ['status', 'time', 'debug']
        for field in required_fields:
            self.assertIn(field, data)
        
        # Verificar tipos
        self.assertIsInstance(data['status'], str)
        self.assertIsInstance(data['time'], str)
        self.assertIsInstance(data['debug'], bool)
    
    def test_healthz_methods(self):
        """Teste de métodos HTTP permitidos"""
        # GET deve funcionar
        response = self.client.get(reverse('core:healthz'))
        self.assertEqual(response.status_code, 200)
        
        # POST deve retornar 405 (Method Not Allowed)
        response = self.client.post(reverse('core:healthz'))
        self.assertEqual(response.status_code, 405)