from django.urls import path, include
from .admin import custom_admin_site
from . import payment_views, dashboard_views

app_name = 'students'

urlpatterns = [
    # Admin customizado sob /dashboard/admin/ com namespace do próprio site (custom_admin)
    path('admin/', custom_admin_site.urls),
    
    # Views personalizadas
    path('', payment_views.dashboard_view, name='dashboard'),
    path('students/', payment_views.student_list_view, name='student_list'),
    path('students/<int:student_id>/', payment_views.student_detail_view, name='student_detail'),
    path('payments/', payment_views.payment_list_view, name='payment_list'),
    path('payments/<int:payment_id>/pix/', payment_views.create_pix_payment, name='create_pix_payment'),
    path('pix/<int:pix_payment_id>/', payment_views.pix_payment_detail, name='pix_payment_detail'),
    path('reports/', payment_views.payment_reports_view, name='payment_reports'),
    path('reports/generate/', payment_views.generate_payment_report, name='generate_report'),
    path('webhook/payment/', payment_views.payment_webhook, name='payment_webhook'),
    
    # Dashboards por tipo de usuário
    path('login/', dashboard_views.login_view, name='login'),
    path('student-dashboard/', dashboard_views.student_dashboard_view, name='student_dashboard'),
    path('instructor-dashboard/', dashboard_views.instructor_dashboard_view, name='instructor_dashboard'),
    path('mark-attendance/', dashboard_views.mark_attendance_view, name='mark_attendance'),
    path('student-payments/', dashboard_views.student_payment_view, name='student_payments'),
]
