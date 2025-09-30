import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)


class PerformanceMiddleware(MiddlewareMixin):
    """Middleware para monitorar performance das requisições"""
    
    def process_request(self, request):
        request.start_time = time.time()
        return None
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Log requests lentas (> 1 segundo)
            if duration > 1.0:
                logger.warning(
                    f"Slow request: {request.method} {request.path} "
                    f"took {duration:.2f}s"
                )
            
            # Adicionar header de performance
            response['X-Response-Time'] = f"{duration:.3f}s"
            
            # Monitorar performance via cache
            if not settings.DEBUG:
                cache_key = f"perf_{request.path}_{request.method}"
                cache.set(cache_key, duration, timeout=3600)
        
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """Middleware para rate limiting básico"""
    
    def process_request(self, request):
        # Rate limiting apenas para APIs e formulários (não em testes)
        if (request.path.startswith('/api/') or request.method == 'POST') and not getattr(request, 'testing', False):
            client_ip = self.get_client_ip(request)
            cache_key = f"rate_limit_{client_ip}"
            
            # Verificar limite (10 requests por minuto)
            current_requests = cache.get(cache_key, 0)
            if current_requests >= 10:
                return JsonResponse({
                    'error': 'Rate limit exceeded',
                    'message': 'Too many requests. Please try again later.'
                }, status=429)
            
            # Incrementar contador
            cache.set(cache_key, current_requests + 1, timeout=60)
        
        return None
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Middleware para adicionar headers de segurança"""
    
    def process_response(self, request, response):
        # Headers de segurança
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'SAMEORIGIN'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy básico
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://www.googletagmanager.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://www.google-analytics.com; "
            "frame-src 'none';"
        )
        response['Content-Security-Policy'] = csp
        
        return response


class ErrorHandlingMiddleware(MiddlewareMixin):
    """Middleware para tratamento de erros"""
    
    def process_exception(self, request, exception):
        # Log do erro
        logger.error(
            f"Exception in {request.method} {request.path}: {str(exception)}",
            exc_info=True
        )
        
        # Resposta de erro para APIs
        if request.path.startswith('/api/'):
            return JsonResponse({
                'error': 'Internal server error',
                'message': 'An error occurred while processing your request.'
            }, status=500)
        
        return None
