from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from .models import (
    Student, PaymentPlan, StudentSubscription, 
    Payment, PaymentReceipt, Attendance
)
from .payment_models import PIXPayment, PaymentNotification, PaymentReport


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone', 'belt_color', 'is_active', 'enrollment_date', 'age']
    list_filter = ['belt_color', 'is_active', 'enrollment_date', 'city', 'state']
    search_fields = ['first_name', 'last_name', 'email', 'cpf', 'phone']
    readonly_fields = ['created_at', 'updated_at', 'age']
    
    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'whatsapp', 'photo')
        }),
        ('Documentos', {
            'fields': ('cpf', 'rg')
        }),
        ('Endereço', {
            'fields': ('address', 'city', 'state', 'zip_code')
        }),
        ('Informações da Academia', {
            'fields': ('belt_color', 'enrollment_date', 'is_active')
        }),
        ('Informações Médicas', {
            'fields': ('birth_date', 'emergency_contact_name', 'emergency_contact_phone', 'medical_conditions', 'allergies')
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')


@admin.register(PaymentPlan)
class PaymentPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'duration_days', 'allows_unlimited_classes', 'max_classes_per_month', 'is_active']
    list_filter = ['is_active', 'allows_unlimited_classes']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(StudentSubscription)
class StudentSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['student', 'payment_plan', 'start_date', 'end_date', 'status', 'is_active']
    list_filter = ['status', 'start_date', 'end_date', 'payment_plan']
    search_fields = ['student__first_name', 'student__last_name', 'student__email']
    readonly_fields = ['created_at', 'updated_at', 'is_active']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student', 'payment_plan')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['student', 'amount', 'final_amount', 'payment_method', 'payment_status', 'due_date', 'paid_date']
    list_filter = ['payment_status', 'payment_method', 'due_date', 'paid_date']
    search_fields = ['student__first_name', 'student__last_name', 'student__email', 'payment_id']
    readonly_fields = ['payment_id', 'final_amount', 'created_at', 'updated_at']
    date_hierarchy = 'due_date'
    
    fieldsets = (
        ('Informações do Pagamento', {
            'fields': ('payment_id', 'student', 'subscription', 'amount', 'discount_amount', 'final_amount')
        }),
        ('Detalhes do Pagamento', {
            'fields': ('payment_method', 'payment_status', 'due_date', 'paid_date')
        }),
        ('Observações', {
            'fields': ('notes',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student', 'subscription', 'created_by')


@admin.register(PaymentReceipt)
class PaymentReceiptAdmin(admin.ModelAdmin):
    list_display = ['payment', 'receipt_type', 'uploaded_at', 'uploaded_by']
    list_filter = ['receipt_type', 'uploaded_at']
    search_fields = ['payment__student__first_name', 'payment__student__last_name']
    readonly_fields = ['uploaded_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('payment__student', 'uploaded_by')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'class_date', 'class_time', 'instructor', 'status']
    list_filter = ['status', 'class_date', 'instructor']
    search_fields = ['student__first_name', 'student__last_name']
    date_hierarchy = 'class_date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student', 'instructor')


@admin.register(PIXPayment)
class PIXPaymentAdmin(admin.ModelAdmin):
    list_display = ['payment', 'amount', 'status', 'expires_at', 'paid_at']
    list_filter = ['status', 'expires_at', 'paid_at']
    search_fields = ['payment__student__first_name', 'payment__student__last_name', 'external_id']
    readonly_fields = ['pix_payment_id', 'external_id', 'created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('payment__student')


@admin.register(PaymentNotification)
class PaymentNotificationAdmin(admin.ModelAdmin):
    list_display = ['payment', 'notification_type', 'sent_via', 'sent_at', 'created_at']
    list_filter = ['notification_type', 'sent_via', 'sent_at']
    search_fields = ['payment__student__first_name', 'payment__student__last_name']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('payment__student')


@admin.register(PaymentReport)
class PaymentReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'report_type', 'start_date', 'end_date', 'total_revenue', 'payment_rate']
    list_filter = ['report_type', 'start_date', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'payment_rate']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')


# Personalização do Admin Site
class CustomAdminSite(admin.AdminSite):
    site_header = "ASBJJ - Administração"
    site_title = "ASBJJ Admin"
    index_title = "Painel Administrativo"
    login_template = 'admin/login.html' # Usar template de login personalizado
    index_template = 'admin/index.html' # Usar template de índice personalizado
    logged_out_template = 'admin/logged_out.html' # Usar template de logout personalizado
    
    def logout(self, request, extra_context=None):
        """Override do logout para redirecionar corretamente"""
        from django.contrib.auth import logout
        from django.shortcuts import redirect
        from django.contrib import messages
        from django.http import HttpResponseRedirect
        
        logout(request)
        messages.success(request, 'Logout realizado com sucesso!')
        return HttpResponseRedirect('/')

    def index(self, request, extra_context=None):
        """
        Personalizar a página inicial do admin com estatísticas
        """
        extra_context = extra_context or {}
        
        # Estatísticas gerais
        total_students = Student.objects.count()
        active_students = Student.objects.filter(is_active=True).count()
        total_payments = Payment.objects.count()
        paid_payments = Payment.objects.filter(payment_status='paid').count()
        
        # Pagamentos do mês atual
        current_month = timezone.now().date().replace(day=1)
        monthly_payments = Payment.objects.filter(
            paid_date__gte=current_month,
            payment_status='paid'
        ).aggregate(
            total_amount=Sum('final_amount'),
            count=Count('id')
        )
        
        # Pagamentos pendentes
        pending_payments = Payment.objects.filter(
            payment_status='pending',
            due_date__lt=timezone.now().date()
        ).count()
        
        # Assinaturas ativas
        active_subscriptions = StudentSubscription.objects.filter(
            status='active',
            start_date__lte=timezone.now().date(),
            end_date__gte=timezone.now().date()
        ).count()
        
        extra_context.update({
            'total_students': total_students,
            'active_students': active_students,
            'total_payments': total_payments,
            'paid_payments': paid_payments,
            'monthly_revenue': monthly_payments['total_amount'] or 0,
            'monthly_payments_count': monthly_payments['count'] or 0,
            'pending_payments': pending_payments,
            'active_subscriptions': active_subscriptions,
        })
        
        return super().index(request, extra_context)


# Criar instância personalizada do admin site
custom_admin_site = CustomAdminSite(name='custom_admin')

# Registrar modelos no admin personalizado
custom_admin_site.register(Student, StudentAdmin)
custom_admin_site.register(PaymentPlan, PaymentPlanAdmin)
custom_admin_site.register(StudentSubscription, StudentSubscriptionAdmin)
custom_admin_site.register(Payment, PaymentAdmin)
custom_admin_site.register(PaymentReceipt, PaymentReceiptAdmin)
custom_admin_site.register(Attendance, AttendanceAdmin)
custom_admin_site.register(PIXPayment, PIXPaymentAdmin)
custom_admin_site.register(PaymentNotification, PaymentNotificationAdmin)
custom_admin_site.register(PaymentReport, PaymentReportAdmin)