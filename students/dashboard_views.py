from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.contrib.auth.models import User
from django.contrib.auth import logout
from datetime import datetime, timedelta

from .models import Student, Payment, PaymentPlan, StudentSubscription, Attendance
from .user_models import UserProfile
from .decorators import admin_required, student_required, instructor_required


@login_required
@student_required
def student_dashboard_view(request):
    """Dashboard do aluno"""
    try:
        profile = request.user.student_profile
        student = profile.student_profile
        
        # Pagamentos do aluno
        payments = student.payments.all().order_by('-created_at')
        pending_payments = payments.filter(payment_status='pending')
        paid_payments = payments.filter(payment_status='paid')
        
        # Assinatura atual
        current_subscription = student.subscriptions.filter(
            status='active',
            start_date__lte=timezone.now().date(),
            end_date__gte=timezone.now().date()
        ).first()
        
        # Presenças recentes
        recent_attendances = student.attendances.all().order_by('-class_date')[:10]
        
        # Próximas aulas (simulado - você pode criar um modelo de aulas)
        today = timezone.now().date()
        next_classes = [
            {'date': today + timedelta(days=1), 'time': '19:00', 'instructor': 'Prof. Alexandre'},
            {'date': today + timedelta(days=3), 'time': '19:00', 'instructor': 'Prof. Alexandre'},
            {'date': today + timedelta(days=5), 'time': '19:00', 'instructor': 'Prof. Alexandre'},
        ]
        
        context = {
            'student': student,
            'payments': payments,
            'pending_payments': pending_payments,
            'paid_payments': paid_payments,
            'current_subscription': current_subscription,
            'recent_attendances': recent_attendances,
            'next_classes': next_classes,
        }
        
        return render(request, 'students/student_dashboard.html', context)
        
    except UserProfile.DoesNotExist:
        messages.error(request, 'Perfil não encontrado.')
        return redirect('students:login')


@login_required
@instructor_required
def instructor_dashboard_view(request):
    """Dashboard do professor"""
    try:
        profile = request.user.student_profile
        
        # Todos os alunos
        all_students = Student.objects.filter(is_active=True)
        
        # Alunos com pagamentos pendentes
        students_with_pending_payments = Student.objects.filter(
            payments__payment_status='pending',
            payments__due_date__lt=timezone.now().date()
        ).distinct()
        
        # Alunos com pagamentos em dia
        students_with_paid_payments = Student.objects.filter(
            payments__payment_status='paid',
            payments__paid_date__gte=timezone.now().date() - timedelta(days=30)
        ).distinct()
        
        # Presenças recentes
        recent_attendances = Attendance.objects.select_related('student').order_by('-class_date')[:20]
        
        # Estatísticas
        total_students = all_students.count()
        students_pending = students_with_pending_payments.count()
        students_paid = students_with_paid_payments.count()
        
        context = {
            'all_students': all_students,
            'students_with_pending_payments': students_with_pending_payments,
            'students_with_paid_payments': students_with_paid_payments,
            'recent_attendances': recent_attendances,
            'total_students': total_students,
            'students_pending': students_pending,
            'students_paid': students_paid,
        }
        
        return render(request, 'students/instructor_dashboard.html', context)
        
    except UserProfile.DoesNotExist:
        messages.error(request, 'Perfil não encontrado.')
        return redirect('students:login')


@login_required
@student_required
def mark_attendance_view(request):
    """Marcar presença - para alunos"""
    try:
        profile = request.user.student_profile
        student = profile.student_profile
        
        if request.method == 'POST':
            class_date = request.POST.get('class_date')
            class_time = request.POST.get('class_time')
            instructor_id = request.POST.get('instructor')
            
            if class_date and class_time:
                # Verificar se já existe presença para esta data/hora
                existing_attendance = Attendance.objects.filter(
                    student=student,
                    class_date=class_date,
                    class_time=class_time
                ).first()
                
                if existing_attendance:
                    messages.warning(request, 'Presença já registrada para esta aula.')
                else:
                    instructor = None
                    if instructor_id:
                        instructor = User.objects.get(id=instructor_id)
                    
                    Attendance.objects.create(
                        student=student,
                        class_date=class_date,
                        class_time=class_time,
                        instructor=instructor,
                        status='present'
                    )
                    messages.success(request, 'Presença registrada com sucesso!')
                
                return redirect('students:student_dashboard')
        
        # Buscar instrutores disponíveis
        instructors = User.objects.filter(profile__role='instructor')
        
        context = {
            'student': student,
            'instructors': instructors,
        }
        
        return render(request, 'students/mark_attendance.html', context)
        
    except UserProfile.DoesNotExist:
        messages.error(request, 'Perfil não encontrado.')
        return redirect('students:login')


@login_required
@student_required
def student_payment_view(request):
    """Visualizar pagamentos do aluno"""
    try:
        profile = request.user.student_profile
        student = profile.student_profile
        payments = student.payments.all().order_by('-created_at')
        
        context = {
            'student': student,
            'payments': payments,
        }
        
        return render(request, 'students/student_payments.html', context)
        
    except UserProfile.DoesNotExist:
        messages.error(request, 'Perfil não encontrado.')
        return redirect('students:login')


def login_view(request):
    """Página de login personalizada"""
    if request.user.is_authenticated:
        try:
            profile = request.user.student_profile
            if profile.is_admin:
                return redirect('dashboard')
            elif profile.is_instructor:
                return redirect('instructor_dashboard')
            elif profile.is_student:
                return redirect('student_dashboard')
        except UserProfile.DoesNotExist:
            pass
    
    if request.method == 'POST':
        from django.contrib.auth import authenticate, login
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            try:
                profile = user.student_profile
                if profile.is_admin:
                    messages.success(request, f'Bem-vindo, {user.get_full_name()}! Acesso administrativo.')
                    return redirect('dashboard')
                elif profile.is_instructor:
                    messages.success(request, f'Bem-vindo, Professor {user.get_full_name()}!')
                    return redirect('instructor_dashboard')
                elif profile.is_student:
                    messages.success(request, f'Bem-vindo, {user.get_full_name()}!')
                    return redirect('student_dashboard')
            except UserProfile.DoesNotExist:
                messages.error(request, 'Perfil de usuário não encontrado.')
        else:
            messages.error(request, 'Usuário ou senha incorretos.')
    
    return render(request, 'students/login.html')


def logout_view(request):
    """Logout personalizado que redireciona para a página principal"""
    from django.contrib.auth import logout
    from django.contrib import messages
    
    logout(request)
    messages.success(request, 'Logout realizado com sucesso!')
    return redirect('/')
