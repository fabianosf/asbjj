from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView, FormView
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods

from .models import SiteSettings, ContactMessage, Instructor, Gallery, BlogPost
from .forms import ContactForm


class HomeView(TemplateView):
    """Página inicial"""
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Configurações do site
        try:
            context['site_settings'] = SiteSettings.objects.first()
        except:
            context['site_settings'] = None
        
        # Instrutores
        context['instructors'] = Instructor.objects.filter(is_active=True)[:4]
        
        # Galeria
        context['gallery_images'] = Gallery.objects.filter(is_featured=True)[:6]
        
        # Blog posts recentes
        context['recent_posts'] = BlogPost.objects.filter(
            status='published'
        ).order_by('-published_at')[:3]
        
        return context


class AboutView(TemplateView):
    """Página sobre"""
    template_name = 'core/sobre.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Instrutores
        context['instructors'] = Instructor.objects.filter(is_active=True)
        
        # Configurações do site
        try:
            context['site_settings'] = SiteSettings.objects.first()
        except:
            context['site_settings'] = None
        
        return context


class ServicesView(TemplateView):
    """Página de serviços"""
    template_name = 'core/servicos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Configurações do site
        try:
            context['site_settings'] = SiteSettings.objects.first()
        except:
            context['site_settings'] = None
        
        return context


class ContactView(FormView):
    """Página de contato"""
    template_name = 'core/contato.html'
    form_class = ContactForm
    success_url = reverse_lazy('core:contact')

    def form_valid(self, form):
        # Salvar a mensagem
        contact_message = form.save(commit=False)
        contact_message.ip_address = self.get_client_ip()
        contact_message.user_agent = self.request.META.get('HTTP_USER_AGENT', '')
        contact_message.save()

        # Enviar notificação por e-mail
        try:
            self.send_notification_email(contact_message)
        except Exception as e:
            # Log do erro, mas não falha o processo
            pass

        messages.success(
            self.request, 
            'Sua mensagem foi enviada com sucesso! Entraremos em contato em breve.'
        )
        return super().form_valid(form)

    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

    def send_notification_email(self, contact_message):
        """Envia e-mail de notificação para o administrador"""
        subject = f'[ASBJJ] Nova mensagem de contato de {contact_message.name}'
        message = f"""
Nova mensagem de contato recebida:

Nome: {contact_message.name}
E-mail: {contact_message.email}
Telefone: {contact_message.phone or 'Não informado'}
Categoria: {contact_message.get_category_display()}

Mensagem:
{contact_message.message}

---
Enviado em: {contact_message.created_at}
IP: {contact_message.ip_address}
        """
        
        from django.core.mail import send_mail
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=False,
        )


# Views antigas para compatibilidade
def index(request):
    """View antiga da página inicial"""
    return HomeView.as_view()(request)


def sobre(request):
    """View antiga da página sobre"""
    return AboutView.as_view()(request)


def servicos(request):
    """View antiga da página de serviços"""
    return ServicesView.as_view()(request)


def contato(request):
    """View antiga da página de contato"""
    if request.method == 'POST':
        return ContactView.as_view()(request)
    else:
        return ContactView.as_view()(request)


@require_http_methods(["GET"])
def healthz(request):
    """Endpoint de health-check simples"""
    return JsonResponse({
        'status': 'ok',
        'time': timezone.now().isoformat(),
        'debug': settings.DEBUG,
    })