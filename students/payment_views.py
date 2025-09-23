from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
import json
import uuid
from decimal import Decimal

from .models import Student, Payment, PaymentPlan, StudentSubscription, Attendance
from .payment_models import PIXPayment, PaymentNotification, PaymentReport
from .decorators import admin_required


@login_required
@admin_required
def dashboard_view(request):
    """Dashboard principal com estatísticas"""
    
    # Estatísticas gerais
    total_students = Student.objects.count()
    active_students = Student.objects.filter(is_active=True).count()
    
    # Pagamentos
    total_payments = Payment.objects.count()
    paid_payments = Payment.objects.filter(payment_status='paid').count()
    pending_payments = Payment.objects.filter(
        payment_status='pending',
        due_date__lt=timezone.now().date()
    ).count()
    
    # Receita do mês atual
    current_month = timezone.now().date().replace(day=1)
    monthly_revenue = Payment.objects.filter(
        paid_date__gte=current_month,
        payment_status='paid'
    ).aggregate(total=Sum('final_amount'))['total'] or 0
    
    # Assinaturas ativas
    active_subscriptions = StudentSubscription.objects.filter(
        status='active',
        start_date__lte=timezone.now().date(),
        end_date__gte=timezone.now().date()
    ).count()
    
    # Pagamentos recentes
    recent_payments = Payment.objects.select_related('student').order_by('-created_at')[:10]
    
    # Alunos com pagamentos pendentes
    overdue_students = Student.objects.filter(
        payments__payment_status='pending',
        payments__due_date__lt=timezone.now().date()
    ).distinct()[:5]
    
    # Calcular valores pendentes para cada aluno
    for student in overdue_students:
        student.pending_amount = student.payments.filter(
            payment_status='pending'
        ).aggregate(total=Sum('final_amount'))['total'] or 0
    
    context = {
        'total_students': total_students,
        'active_students': active_students,
        'total_payments': total_payments,
        'paid_payments': paid_payments,
        'pending_payments': pending_payments,
        'monthly_revenue': monthly_revenue,
        'active_subscriptions': active_subscriptions,
        'recent_payments': recent_payments,
        'overdue_students': overdue_students,
    }
    
    return render(request, 'students/dashboard.html', context)


@login_required
@admin_required
def student_list_view(request):
    """Lista de alunos"""
    students = Student.objects.all().order_by('first_name', 'last_name')
    
    # Filtros
    search = request.GET.get('search', '')
    belt_filter = request.GET.get('belt', '')
    status_filter = request.GET.get('status', '')
    
    if search:
        students = students.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )
    
    if belt_filter:
        students = students.filter(belt_color=belt_filter)
    
    if status_filter == 'active':
        students = students.filter(is_active=True)
    elif status_filter == 'inactive':
        students = students.filter(is_active=False)
    
    context = {
        'students': students,
        'search': search,
        'belt_filter': belt_filter,
        'status_filter': status_filter,
    }
    
    return render(request, 'students/student_list.html', context)


@login_required
@admin_required
def student_detail_view(request, student_id):
    """Detalhes do aluno"""
    student = get_object_or_404(Student, id=student_id)
    
    # Assinaturas do aluno
    subscriptions = student.subscriptions.all().order_by('-created_at')
    
    # Pagamentos do aluno
    payments = student.payments.all().order_by('-created_at')
    
    # Presenças recentes
    recent_attendances = student.attendances.all().order_by('-class_date')[:10]
    
    # Estatísticas do aluno
    total_paid = payments.filter(payment_status='paid').aggregate(
        total=Sum('final_amount')
    )['total'] or 0
    
    pending_amount = payments.filter(payment_status='pending').aggregate(
        total=Sum('final_amount')
    )['total'] or 0
    
    context = {
        'student': student,
        'subscriptions': subscriptions,
        'payments': payments,
        'recent_attendances': recent_attendances,
        'total_paid': total_paid,
        'pending_amount': pending_amount,
    }
    
    return render(request, 'students/student_detail.html', context)


@login_required
@admin_required
def payment_list_view(request):
    """Lista de pagamentos"""
    payments = Payment.objects.select_related('student', 'subscription').order_by('-created_at')
    
    # Filtros
    status_filter = request.GET.get('status', '')
    method_filter = request.GET.get('method', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if status_filter:
        payments = payments.filter(payment_status=status_filter)
    
    if method_filter:
        payments = payments.filter(payment_method=method_filter)
    
    if date_from:
        payments = payments.filter(due_date__gte=date_from)
    
    if date_to:
        payments = payments.filter(due_date__lte=date_to)
    
    context = {
        'payments': payments,
        'status_filter': status_filter,
        'method_filter': method_filter,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'students/payment_list.html', context)


@login_required
def create_pix_payment(request, payment_id):
    """Criar pagamento PIX"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        # Simular criação de PIX (em produção, integrar com gateway de pagamento)
        pix_payment = PIXPayment.objects.create(
            payment=payment,
            amount=payment.final_amount,
            pix_key=settings.PIX_KEY if hasattr(settings, 'PIX_KEY') else 'contato@asbjj.com.br',
            pix_copy_paste=f"00020126580014BR.GOV.BCB.PIX0114+5511999999999520400005303986540{payment.final_amount:.2f}5802BR5913ASBJJ ACADEMY6009SAO PAULO62070503***6304{payment.payment_id}",
            expires_at=timezone.now() + timezone.timedelta(hours=24)
        )
        
        messages.success(request, 'Pagamento PIX criado com sucesso!')
        return redirect('students:pix_payment_detail', pix_payment.id)
    
    return render(request, 'students/create_pix_payment.html', {'payment': payment})


@login_required
def pix_payment_detail(request, pix_payment_id):
    """Detalhes do pagamento PIX"""
    pix_payment = get_object_or_404(PIXPayment, id=pix_payment_id)
    
    context = {
        'pix_payment': pix_payment,
    }
    
    return render(request, 'students/pix_payment_detail.html', context)


@login_required
def payment_reports_view(request):
    """Relatórios de pagamento"""
    reports = PaymentReport.objects.all().order_by('-created_at')
    
    context = {
        'reports': reports,
    }
    
    return render(request, 'students/payment_reports.html', context)


@login_required
def generate_payment_report(request):
    """Gerar relatório de pagamento"""
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        report_type = request.POST.get('report_type', 'custom')
        
        # Buscar pagamentos no período
        payments = Payment.objects.filter(
            due_date__gte=start_date,
            due_date__lte=end_date
        )
        
        # Calcular estatísticas
        total_revenue = payments.filter(payment_status='paid').aggregate(
            total=Sum('final_amount')
        )['total'] or 0
        
        total_payments = payments.count()
        paid_payments = payments.filter(payment_status='paid').count()
        pending_payments = payments.filter(payment_status='pending').count()
        overdue_payments = payments.filter(
            payment_status='pending',
            due_date__lt=timezone.now().date()
        ).count()
        
        # Criar relatório
        report = PaymentReport.objects.create(
            report_type=report_type,
            title=f"Relatório de Pagamentos - {start_date} a {end_date}",
            start_date=start_date,
            end_date=end_date,
            total_revenue=total_revenue,
            total_payments=total_payments,
            paid_payments=paid_payments,
            pending_payments=pending_payments,
            overdue_payments=overdue_payments,
            created_by=request.user
        )
        
        messages.success(request, 'Relatório gerado com sucesso!')
        return redirect('students:payment_reports')
    
    return render(request, 'students/generate_report.html')


@csrf_exempt
def payment_webhook(request):
    """Webhook para receber notificações de pagamento"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Em produção, validar assinatura do webhook
            payment_id = data.get('payment_id')
            status = data.get('status')
            
            if payment_id and status:
                try:
                    pix_payment = PIXPayment.objects.get(external_id=payment_id)
                    
                    if status == 'paid' and pix_payment.status == 'pending':
                        pix_payment.status = 'paid'
                        pix_payment.paid_at = timezone.now()
                        pix_payment.save()
                        
                        # Atualizar pagamento relacionado
                        payment = pix_payment.payment
                        payment.payment_status = 'paid'
                        payment.paid_date = timezone.now()
                        payment.save()
                        
                        # Criar notificação
                        PaymentNotification.objects.create(
                            payment=payment,
                            notification_type='payment_received',
                            message=f'Pagamento PIX de R$ {payment.final_amount} recebido com sucesso!',
                            sent_via='email'
                        )
                        
                        return JsonResponse({'status': 'success'})
                        
                except PIXPayment.DoesNotExist:
                    pass
            
        except json.JSONDecodeError:
            pass
    
    return JsonResponse({'status': 'error'}, status=400)
