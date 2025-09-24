"""
URL configuration for ASBJJ project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from students import dashboard_views
from django.views.generic.base import RedirectView
from django.contrib.auth import views as auth_views
from accounts.views import CustomPasswordResetConfirmView

# Importar sitemaps
try:
    from core.sitemaps import StaticViewSitemap
    sitemaps = {
        'static': StaticViewSitemap,
    }
except ImportError:
    sitemaps = {}

urlpatterns = [
    # Admin com logout personalizado
    path("admin/logout/", dashboard_views.logout_view, name="admin_logout"),
    path("admin/", admin.site.urls),
    
    # Dashboard personalizado
    path("dashboard/", include(("students.urls", "students"), namespace="students")),
    
    # Dashboards por tipo de usuário
    path("login/", dashboard_views.login_view, name="login"),
    path("logout/", dashboard_views.logout_view, name="logout"),
    path("student-dashboard/", dashboard_views.student_dashboard_view, name="student_dashboard"),
    path("instructor-dashboard/", dashboard_views.instructor_dashboard_view, name="instructor_dashboard"),
    path("mark-attendance/", dashboard_views.mark_attendance_view, name="mark_attendance"),
    path("student-payments/", dashboard_views.student_payment_view, name="student_payments"),
    
    # Core URLs
    path("", include("core.urls")),
    
    # App URLs
    path("accounts/", include("accounts.urls")),

    # Password reset aliases (sem namespace) para compatibilidade com templates/padrões
    path("password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", CustomPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    
    # Sitemap
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    
    # Robots.txt
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    # Favicon
    path("favicon.ico", RedirectView.as_view(url=settings.STATIC_URL + "img/logo.png", permanent=True)),
]

# Debug toolbar (apenas em desenvolvimento)
if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass

# Servir arquivos estáticos e de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)