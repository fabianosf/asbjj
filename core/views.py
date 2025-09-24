from django.shortcuts import render, get_object_or_404, redirect
from django import forms
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.views.generic import TemplateView, ListView, DetailView, FormView
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods

from .models import SiteSettings, ContactMessage, Instructor, Gallery, BlogPost
from .forms import ContactForm, TrialClassBookingForm
from students.models import Student


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
        context['featured_instructors'] = Instructor.objects.filter(is_active=True, is_featured=True)[:4]
        
        # Galeria
        context['gallery_images'] = Gallery.objects.filter(is_featured=True)[:8]
        
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


class GalleryListView(ListView):
    """Galeria de fotos"""
    model = Gallery
    template_name = 'core/galeria.html'
    context_object_name = 'images'
    paginate_by = 24

    def get_queryset(self):
        queryset = Gallery.objects.all().order_by('order', '-created_at')
        category = self.request.GET.get('categoria')
        if category:
            queryset = queryset.filter(category=category)
        return queryset


class BlogListView(ListView):
    """Lista de posts do blog"""
    model = BlogPost
    template_name = 'core/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = BlogPost.objects.filter(status='published').order_by('-published_at')
        category = self.request.GET.get('categoria')
        if category:
            queryset = queryset.filter(category=category)
        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(Q(title__icontains=search) | Q(content__icontains=search))
        return queryset


class BlogDetailView(DetailView):
    """Detalhe do post do blog"""
    model = BlogPost
    template_name = 'core/blog_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'


class EnrollmentApplicationView(FormView):
    """Formulário de inscrição de novos alunos"""
    template_name = 'core/inscricao.html'
    success_url = reverse_lazy('core:enrollment')

    class EnrollmentForm(forms.Form):
        first_name = forms.CharField(label='Nome', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
        last_name = forms.CharField(label='Sobrenome', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
        email = forms.EmailField(label='E-mail', widget=forms.EmailInput(attrs={'class': 'form-control'}))
        phone = forms.CharField(label='Telefone', max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
        birth_date = forms.DateField(label='Data de Nascimento', widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
        cpf = forms.CharField(label='CPF', max_length=14, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}))
        address = forms.CharField(label='Endereço', widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))
        city = forms.CharField(label='Cidade', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
        state = forms.CharField(label='Estado', max_length=2, widget=forms.TextInput(attrs={'class': 'form-control'}))
        zip_code = forms.CharField(label='CEP', max_length=10, widget=forms.TextInput(attrs={'class': 'form-control'}))
        whatsapp = forms.CharField(label='WhatsApp', max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
        medical_conditions = forms.CharField(label='Condições Médicas', required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
        allergies = forms.CharField(label='Alergias', required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))

        def clean_cpf(self):
            cpf = self.cleaned_data.get('cpf', '').strip()
            # Normalizar apenas dígitos
            digits = ''.join(filter(str.isdigit, cpf))
            if len(digits) != 11:
                raise ValidationError('CPF deve ter 11 dígitos.')
            # Rejeitar CPFs com todos dígitos iguais
            if digits == digits[0] * 11:
                raise ValidationError('CPF inválido.')
            # Validar dígitos verificadores
            def calc_dv(nums, factor):
                total = 0
                for n in nums:
                    total += int(n) * factor
                    factor -= 1
                resto = (total * 10) % 11
                return '0' if resto == 10 else str(resto)
            dv1 = calc_dv(digits[:9], 10)
            dv2 = calc_dv(digits[:10], 11)
            if digits[-2:] != dv1 + dv2:
                raise ValidationError('CPF inválido.')
            # Formatar
            cpf_formatted = f"{digits[0:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:11]}"
            if Student.objects.filter(cpf=cpf_formatted).exists() or Student.objects.filter(cpf=digits).exists():
                raise ValidationError('Este CPF já está cadastrado.')
            return cpf_formatted

        def clean_email(self):
            email = self.cleaned_data.get('email', '').strip().lower()
            if Student.objects.filter(email=email).exists():
                raise ValidationError('Este e-mail já está cadastrado.')
            return email

    form_class = EnrollmentForm

    def form_valid(self, form):
        # Validações de unicidade extras para evitar erro 500
        if Student.objects.filter(cpf=form.cleaned_data['cpf']).exists():
            form.add_error('cpf', 'Este CPF já está cadastrado.')
            return self.form_invalid(form)
        if Student.objects.filter(email=form.cleaned_data['email']).exists():
            form.add_error('email', 'Este e-mail já está cadastrado.')
            return self.form_invalid(form)

        try:
            # Criar registro básico de aluno (sem exigir login)
            Student.objects.create(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                whatsapp=form.cleaned_data.get('whatsapp', ''),
                cpf=form.cleaned_data['cpf'],
                rg='',
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                state=form.cleaned_data['state'],
                zip_code=form.cleaned_data['zip_code'],
                birth_date=form.cleaned_data['birth_date'],
                emergency_contact_name=form.cleaned_data['first_name'] + ' ' + form.cleaned_data['last_name'],
                emergency_contact_phone=form.cleaned_data['phone'],
                medical_conditions=form.cleaned_data.get('medical_conditions', ''),
                allergies=form.cleaned_data.get('allergies', ''),
                created_by=None,
            )
        except IntegrityError:
            # Fallback: caso outro campo único conflite
            form.add_error(None, 'Não foi possível concluir a inscrição. Verifique os dados e tente novamente.')
            return self.form_invalid(form)

        messages.success(self.request, 'Inscrição enviada! Entraremos em contato para finalizar a matrícula.')
        return super().form_valid(form)


class CalendarView(TemplateView):
    """Calendário de eventos/competições"""
    template_name = 'core/calendario.html'


class ShopView(TemplateView):
    """Página simples de merchandising/loja"""
    template_name = 'core/loja.html'