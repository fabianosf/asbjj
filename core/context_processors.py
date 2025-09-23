from django.conf import settings
from .models import SiteSettings


def site_settings(request):
    """Context processor para configurações do site"""
    try:
        site_config = SiteSettings.objects.first()
    except SiteSettings.DoesNotExist:
        site_config = None
    
    return {
        'site_config': site_config,
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'ASBJJ'),
        'SITE_URL': getattr(settings, 'SITE_URL', 'https://asbjj.com.br'),
        'ADMIN_EMAIL': getattr(settings, 'ADMIN_EMAIL', 'admin@asbjj.com.br'),
        'GOOGLE_ANALYTICS_ID': getattr(settings, 'GOOGLE_ANALYTICS_ID', ''),
        'WHATSAPP_NUMBER': getattr(settings, 'WHATSAPP_NUMBER', '+5511999999999'),
    }
