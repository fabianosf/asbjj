from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta

from .models import TrialClassBooking, RegularBooking, Attendance, Payment
from classes.models import Class, ClassSchedule


class MyBookingsView(LoginRequiredMixin, ListView):
    """Lista de agendamentos do usuário"""
    model = RegularBooking
    template_name = 'schedule/my_bookings.html'
    context_object_name = 'bookings'
    paginate_by = 10

    def get_queryset(self):
        return RegularBooking.objects.filter(
            user=self.request.user
        ).select_related('class_obj').order_by('-created_at')


class BookingDetailView(LoginRequiredMixin, DetailView):
    """Detalhes de um agendamento específico"""
    model = RegularBooking
    template_name = 'schedule/booking_detail.html'
    context_object_name = 'booking'
    pk_url_kwarg = 'booking_id'

    def get_queryset(self):
        return RegularBooking.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking = self.object
        
        # Presenças recentes
        context['recent_attendances'] = Attendance.objects.filter(
            booking=booking
        ).order_by('-date')[:10]
        
        # Pagamentos recentes
        context['recent_payments'] = Payment.objects.filter(
            booking=booking
        ).order_by('-payment_date')[:5]
        
        # Estatísticas
        context['total_classes'] = Attendance.objects.filter(booking=booking).count()
        context['attended_classes'] = Attendance.objects.filter(
            booking=booking, 
            attended=True
        ).count()
        context['missed_classes'] = Attendance.objects.filter(
            booking=booking, 
            attended=False
        ).count()
        
        if context['total_classes'] > 0:
            context['attendance_rate'] = round(
                (context['attended_classes'] / context['total_classes']) * 100, 1
            )
        else:
            context['attendance_rate'] = 0
        
        return context


class CancelBookingView(LoginRequiredMixin, TemplateView):
    """Cancelar agendamento"""
    template_name = 'schedule/cancel_booking.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking_id = self.kwargs.get('booking_id')
        context['booking'] = get_object_or_404(
            RegularBooking, 
            id=booking_id, 
            user=self.request.user
        )
        return context
    
    def post(self, request, *args, **kwargs):
        booking_id = self.kwargs.get('booking_id')
        booking = get_object_or_404(
            RegularBooking, 
            id=booking_id, 
            user=self.request.user
        )
        
        reason = request.POST.get('reason', '')
        
        # Atualizar status do agendamento
        booking.status = 'cancelled'
        booking.save()
        
        # Enviar notificação
        try:
            self.send_cancellation_notification(booking, reason)
        except Exception as e:
            pass
        
        messages.success(
            request,
            'Seu agendamento foi cancelado com sucesso.'
        )
        
        return redirect('schedule:my_bookings')
    
    def send_cancellation_notification(self, booking, reason):
        """Enviar notificação de cancelamento"""
        from django.core.mail import send_mail
        from django.conf import settings
        
        subject = f'[ASBJJ] Agendamento cancelado - {booking.class_obj.name}'
        message = f"""
Agendamento cancelado:

Aluno: {booking.user.get_full_name()}
Aula: {booking.class_obj.name}
Data de início: {booking.start_date}
Data de cancelamento: {timezone.now().strftime('%d/%m/%Y %H:%M')}

Motivo do cancelamento:
{reason or 'Não informado'}

---
Cancelado por: {self.request.user.get_full_name()}
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=False,
        )


class AttendanceListView(LoginRequiredMixin, ListView):
    """Lista de presenças do usuário"""
    model = Attendance
    template_name = 'schedule/attendance_list.html'
    context_object_name = 'attendances'
    paginate_by = 20

    def get_queryset(self):
        return Attendance.objects.filter(
            booking__user=self.request.user
        ).select_related('booking', 'schedule').order_by('-date')


class PaymentListView(LoginRequiredMixin, ListView):
    """Lista de pagamentos do usuário"""
    model = Payment
    template_name = 'schedule/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 20

    def get_queryset(self):
        return Payment.objects.filter(
            booking__user=self.request.user
        ).select_related('booking').order_by('-payment_date')


def booking_stats_api(request):
    """API para estatísticas de agendamentos"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Não autorizado'}, status=401)
    
    if request.method == 'GET':
        try:
            # Agendamentos ativos
            active_bookings = RegularBooking.objects.filter(
                user=request.user,
                status='active'
            ).count()
            
            # Total de aulas assistidas
            total_attended = Attendance.objects.filter(
                booking__user=request.user,
                attended=True
            ).count()
            
            # Taxa de presença
            total_classes = Attendance.objects.filter(
                booking__user=request.user
            ).count()
            
            attendance_rate = 0
            if total_classes > 0:
                attendance_rate = round((total_attended / total_classes) * 100, 1)
            
            # Próximas aulas
            today = timezone.now().date()
            next_week = today + timedelta(days=7)
            
            upcoming_classes = Attendance.objects.filter(
                booking__user=request.user,
                date__gte=today,
                date__lte=next_week
            ).select_related('booking', 'schedule').order_by('date', 'schedule__start_time')
            
            upcoming_data = []
            for attendance in upcoming_classes:
                upcoming_data.append({
                    'date': attendance.date.strftime('%d/%m/%Y'),
                    'time': attendance.schedule.start_time.strftime('%H:%M'),
                    'class_name': attendance.booking.class_obj.name,
                    'instructor': attendance.schedule.instructor.get_full_name() if attendance.schedule.instructor else 'A definir',
                    'location': attendance.schedule.location
                })
            
            # Pagamentos pendentes
            pending_payments = Payment.objects.filter(
                booking__user=request.user,
                payment_date__isnull=True
            ).select_related('booking').order_by('due_date')
            
            pending_data = []
            for payment in pending_payments:
                pending_data.append({
                    'id': payment.id,
                    'amount': float(payment.amount),
                    'due_date': payment.due_date.strftime('%d/%m/%Y'),
                    'class_name': payment.booking.class_obj.name,
                    'reference_month': payment.reference_month.strftime('%m/%Y')
                })
            
            data = {
                'active_bookings': active_bookings,
                'total_attended': total_attended,
                'attendance_rate': attendance_rate,
                'upcoming_classes': upcoming_data,
                'pending_payments': pending_data,
                'total_pending': len(pending_data)
            }
            
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)
