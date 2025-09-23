from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import FormView
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Class, ClassCategory, ClassSchedule
from core.forms import TrialClassBookingForm
from schedule.models import TrialClassBooking


class ClassListView(ListView):
    """Lista todas as aulas disponíveis"""
    model = Class
    template_name = 'classes/list.html'
    context_object_name = 'classes'
    paginate_by = 12

    def get_queryset(self):
        queryset = Class.objects.filter(is_active=True).select_related('category')
        
        # Filtro por categoria
        category_slug = self.request.GET.get('categoria')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Filtro por busca
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(short_description__icontains=search)
            )
        
        return queryset.order_by('category', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ClassCategory.objects.filter(is_active=True)
        context['selected_category'] = self.request.GET.get('categoria')
        context['search_query'] = self.request.GET.get('search', '')
        return context


class ClassDetailView(DetailView):
    """Detalhes de uma aula específica"""
    model = Class
    template_name = 'classes/detail.html'
    context_object_name = 'class_obj'
    slug_field = 'slug'

    def get_queryset(self):
        return Class.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Horários disponíveis
        context['schedules'] = ClassSchedule.objects.filter(
            class_obj=self.object,
            is_active=True
        ).select_related('instructor').order_by('day_of_week', 'start_time')
        
        # Aulas relacionadas
        context['related_classes'] = Class.objects.filter(
            category=self.object.category,
            is_active=True
        ).exclude(id=self.object.id)[:4]
        
        # Depoimentos relacionados
        context['testimonials'] = self.object.testimonials.filter(
            status='approved'
        )[:3]
        
        # Equipamentos necessários
        context['equipment'] = self.object.required_equipment.all()
        
        return context


class ClassCategoryView(ListView):
    """Aulas por categoria"""
    model = Class
    template_name = 'classes/category.html'
    context_object_name = 'classes'
    paginate_by = 12

    def get_queryset(self):
        self.category = get_object_or_404(ClassCategory, slug=self.kwargs['slug'])
        return Class.objects.filter(
            category=self.category,
            is_active=True
        ).order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = ClassCategory.objects.filter(is_active=True)
        return context


class TrialClassBookingView(FormView):
    """Agendamento de aula experimental"""
    template_name = 'classes/trial_booking.html'
    form_class = TrialClassBookingForm
    success_url = reverse_lazy('classes:trial_booking_success')

    def get_initial(self):
        initial = super().get_initial()
        class_id = self.kwargs.get('class_id')
        if class_id:
            initial['class_id'] = class_id
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        class_id = self.kwargs.get('class_id')
        
        if class_id:
            context['class_obj'] = get_object_or_404(Class, id=class_id, is_active=True)
            context['schedules'] = ClassSchedule.objects.filter(
                class_obj=context['class_obj'],
                is_active=True
            ).select_related('instructor').order_by('day_of_week', 'start_time')
        
        return context

    def form_valid(self, form):
        # Criar agendamento
        booking = TrialClassBooking.objects.create(
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            email=form.cleaned_data['email'],
            phone=form.cleaned_data['phone'],
            birth_date=form.cleaned_data.get('birth_date'),
            class_obj_id=form.cleaned_data['class_id'],
            preferred_date=form.cleaned_data['preferred_date'],
            preferred_time=form.cleaned_data.get('preferred_time'),
            notes=form.cleaned_data.get('notes', ''),
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )

        # Enviar notificações
        try:
            self.send_booking_notifications(booking)
        except Exception as e:
            # Log do erro, mas não falha o processo
            pass

        messages.success(
            self.request,
            'Agendamento realizado com sucesso! Entraremos em contato para confirmar.'
        )
        return super().form_valid(form)

    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

    def send_booking_notifications(self, booking):
        """Enviar notificações sobre o agendamento"""
        from django.core.mail import send_mail
        from django.conf import settings

        # E-mail para o administrador
        subject = f'[ASBJJ] Novo agendamento de aula experimental - {booking.full_name}'
        message = f"""
Novo agendamento de aula experimental:

Nome: {booking.full_name}
E-mail: {booking.email}
Telefone: {booking.phone}
Data de Nascimento: {booking.birth_date or 'Não informado'}
Idade: {booking.age or 'Não informado'}

Aula: {booking.class_obj.name}
Data Preferida: {booking.preferred_date}
Horário Preferido: {booking.preferred_time or 'Não especificado'}

Observações:
{booking.notes or 'Nenhuma observação'}

---
Agendado em: {booking.created_at}
IP: {booking.ip_address}
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=False,
        )

        # E-mail de confirmação para o cliente
        confirmation_message = f"""Olá {booking.full_name},

Obrigado pelo seu interesse em fazer uma aula experimental conosco!

Detalhes do seu agendamento:
- Aula: {booking.class_obj.name}
- Data Preferida: {booking.preferred_date}
- Horário Preferido: {booking.preferred_time or 'A definir'}

Nossa equipe entrará em contato em até 24 horas para confirmar o horário e fornecer mais detalhes sobre a aula.

O que esperar:
- Aula experimental gratuita
- Conhecer nossos instrutores
- Experimentar a modalidade
- Receber orientações sobre equipamentos

Se tiver alguma dúvida, entre em contato conosco:
- Telefone: {settings.WHATSAPP_NUMBER}
- E-mail: {settings.ADMIN_EMAIL}

Atenciosamente,
Equipe ASBJJ - Alexandre Salgado Brazilian Jiu-Jitsu
        """
        
        send_mail(
            f'Confirmação de Agendamento - {booking.class_obj.name}',
            confirmation_message,
            settings.DEFAULT_FROM_EMAIL,
            [booking.email],
            fail_silently=False,
        )


class TrialBookingSuccessView(TemplateView):
    """Página de sucesso do agendamento"""
    template_name = 'classes/trial_booking_success.html'


def get_available_schedules(request, class_id):
    """API para obter horários disponíveis de uma aula"""
    if request.method == 'GET':
        try:
            class_obj = get_object_or_404(Class, id=class_id, is_active=True)
            schedules = ClassSchedule.objects.filter(
                class_obj=class_obj,
                is_active=True
            ).select_related('instructor').order_by('day_of_week', 'start_time')
            
            data = []
            for schedule in schedules:
                data.append({
                    'id': schedule.id,
                    'day': schedule.get_day_of_week_display(),
                    'day_number': schedule.day_of_week,
                    'start_time': schedule.start_time.strftime('%H:%M'),
                    'end_time': schedule.end_time.strftime('%H:%M'),
                    'instructor': schedule.instructor.get_full_name() if schedule.instructor else 'A definir',
                    'location': schedule.location,
                    'available': schedule.is_available,
                    'current_enrolled': schedule.current_enrolled,
                    'max_capacity': schedule.max_capacity
                })
            
            return JsonResponse({'schedules': data})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)
