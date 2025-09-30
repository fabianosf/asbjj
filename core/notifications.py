"""
Sistema de notificações push e email
"""
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Serviço de notificações"""
    
    @staticmethod
    def send_order_confirmation(order):
        """Envia confirmação de pedido por email"""
        try:
            subject = f'[ASBJJ] Confirmação do Pedido {order.order_number}'
            
            # Renderizar template HTML
            html_message = render_to_string('emails/order_confirmation.html', {
                'order': order,
                'site_url': settings.SITE_URL,
            })
            
            # Versão texto simples
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [order.customer_email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"Email de confirmação enviado para {order.customer_email}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email de confirmação: {str(e)}")
            return False
    
    @staticmethod
    def send_payment_confirmation(order):
        """Envia confirmação de pagamento por email"""
        try:
            subject = f'[ASBJJ] Pagamento Confirmado - Pedido {order.order_number}'
            
            html_message = render_to_string('emails/payment_confirmation.html', {
                'order': order,
                'site_url': settings.SITE_URL,
            })
            
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [order.customer_email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"Email de confirmação de pagamento enviado para {order.customer_email}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email de confirmação de pagamento: {str(e)}")
            return False
    
    @staticmethod
    def send_shipping_notification(order):
        """Envia notificação de envio por email"""
        try:
            subject = f'[ASBJJ] Seu pedido foi enviado - {order.order_number}'
            
            html_message = render_to_string('emails/shipping_notification.html', {
                'order': order,
                'site_url': settings.SITE_URL,
            })
            
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [order.customer_email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"Email de envio enviado para {order.customer_email}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email de envio: {str(e)}")
            return False
    
    @staticmethod
    def send_delivery_confirmation(order):
        """Envia confirmação de entrega por email"""
        try:
            subject = f'[ASBJJ] Pedido entregue - {order.order_number}'
            
            html_message = render_to_string('emails/delivery_confirmation.html', {
                'order': order,
                'site_url': settings.SITE_URL,
            })
            
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [order.customer_email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"Email de entrega enviado para {order.customer_email}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email de entrega: {str(e)}")
            return False
    
    @staticmethod
    def send_admin_notification(order, notification_type):
        """Envia notificação para administradores"""
        try:
            admin_emails = [settings.ADMIN_EMAIL] if hasattr(settings, 'ADMIN_EMAIL') else []
            
            if not admin_emails:
                return False
            
            subject = f'[ASBJJ Admin] {notification_type} - Pedido {order.order_number}'
            
            html_message = render_to_string('emails/admin_notification.html', {
                'order': order,
                'notification_type': notification_type,
                'site_url': settings.SITE_URL,
            })
            
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                admin_emails,
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"Notificação admin enviada: {notification_type}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação admin: {str(e)}")
            return False


# Instância global do serviço
notification_service = NotificationService()
