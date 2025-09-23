from celery import shared_task
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

@shared_task
def send_contact_notification(contact_message_id):
    """Enviar notificação de nova mensagem de contato"""
    from .models import ContactMessage
    
    try:
        contact_message = ContactMessage.objects.get(id=contact_message_id)
        
        subject = f'[ASBJJ] Nova mensagem de contato de {contact_message.name}'
        
        # Template HTML para o e-mail
        html_content = render_to_string('emails/contact_notification.html', {
            'contact_message': contact_message,
            'site_url': settings.SITE_URL,
        })
        
        # Versão texto simples
        text_content = f"""
Nova mensagem de contato recebida:

Nome: {contact_message.name}
E-mail: {contact_message.email}
Telefone: {contact_message.phone}
Categoria: {contact_message.get_category_display()}
Prioridade: {contact_message.get_priority_display()}

Mensagem:
{contact_message.message}

---
Enviado em: {contact_message.created_at}
IP: {contact_message.ip_address}
        """
        
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        
        return f'Notificação enviada para {settings.ADMIN_EMAIL}'
    except Exception as e:
        return f'Erro ao enviar notificação: {str(e)}'

@shared_task
def send_auto_response(contact_message_id, response_template):
    """Enviar resposta automática baseada em palavras-chave"""
    from .models import ContactMessage
    
    try:
        contact_message = ContactMessage.objects.get(id=contact_message_id)
        
        subject = 'Resposta Automática: Informações Solicitadas'
        
        html_content = render_to_string(f'emails/auto_responses/{response_template}.html', {
            'contact_message': contact_message,
            'site_url': settings.SITE_URL,
        })
        
        text_content = f"""Olá {contact_message.name},

{response_template}

Aqui está a sua mensagem original:
"{contact_message.message}"

Atenciosamente,
Equipe ASBJJ - Alexandre Salgado Brazilian Jiu-Jitsu
        """
        
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [contact_message.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        
        return f'Resposta automática enviada para {contact_message.email}'
    except Exception as e:
        return f'Erro ao enviar resposta automática: {str(e)}'

@shared_task
def send_trial_booking_notification(booking_id):
    """Enviar notificação de novo agendamento experimental"""
    from schedule.models import TrialClassBooking
    
    try:
        booking = TrialClassBooking.objects.get(id=booking_id)
        
        subject = f'[ASBJJ] Novo agendamento de aula experimental - {booking.full_name}'
        
        html_content = render_to_string('emails/trial_booking_notification.html', {
            'booking': booking,
            'site_url': settings.SITE_URL,
        })
        
        text_content = f"""
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
        
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        
        return f'Notificação de agendamento enviada'
    except Exception as e:
        return f'Erro ao enviar notificação de agendamento: {str(e)}'

@shared_task
def send_trial_booking_confirmation(booking_id):
    """Enviar confirmação de agendamento experimental"""
    from schedule.models import TrialClassBooking
    
    try:
        booking = TrialClassBooking.objects.get(id=booking_id)
        
        subject = f'Confirmação de Agendamento - {booking.class_obj.name}'
        
        html_content = render_to_string('emails/trial_booking_confirmation.html', {
            'booking': booking,
            'site_url': settings.SITE_URL,
        })
        
        text_content = f"""Olá {booking.full_name},

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
        
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [booking.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        
        return f'Confirmação de agendamento enviada para {booking.email}'
    except Exception as e:
        return f'Erro ao enviar confirmação de agendamento: {str(e)}'

@shared_task
def send_newsletter_confirmation(subscriber_id):
    """Enviar e-mail de confirmação da newsletter"""
    from newsletter.models import NewsletterSubscriber
    
    try:
        subscriber = NewsletterSubscriber.objects.get(id=subscriber_id)
        
        subject = 'Confirme sua inscrição na newsletter ASBJJ'
        
        confirmation_url = f"{settings.SITE_URL}/newsletter/confirmar/{subscriber.verification_token}/"
        
        html_content = render_to_string('emails/newsletter_confirmation.html', {
            'subscriber': subscriber,
            'confirmation_url': confirmation_url,
            'site_url': settings.SITE_URL,
        })
        
        text_content = f"""
Olá {subscriber.full_name or 'Prezado(a)'},

Obrigado por se inscrever na newsletter da ASBJJ!

Para confirmar sua inscrição e começar a receber nossas novidades, clique no link abaixo:

{confirmation_url}

O que você receberá:
- Novidades sobre nossas modalidades
- Dicas de treino e saúde
- Promoções especiais
- Eventos e competições
- Conteúdo exclusivo

Se você não se inscreveu em nossa newsletter, pode ignorar este e-mail.

Atenciosamente,
Equipe ASBJJ - Alexandre Salgado Brazilian Jiu-Jitsu
        """
        
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [subscriber.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        
        return f'Confirmação de newsletter enviada para {subscriber.email}'
    except Exception as e:
        return f'Erro ao enviar confirmação de newsletter: {str(e)}'

@shared_task
def send_testimonial_notification(testimonial_id):
    """Enviar notificação de novo depoimento"""
    from testimonials.models import Testimonial
    
    try:
        testimonial = Testimonial.objects.get(id=testimonial_id)
        
        subject = f'[ASBJJ] Novo depoimento aguardando aprovação - {testimonial.author_name}'
        
        html_content = render_to_string('emails/testimonial_notification.html', {
            'testimonial': testimonial,
            'site_url': settings.SITE_URL,
        })
        
        text_content = f"""
Novo depoimento aguardando aprovação:

Autor: {testimonial.author_name}
E-mail: {testimonial.author_email}
Avaliação: {testimonial.rating}/5 estrelas
Título: {testimonial.title}

Depoimento:
{testimonial.content}

Aula relacionada: {testimonial.class_related.name if testimonial.class_related else 'Nenhuma'}

---
Enviado em: {testimonial.created_at}
IP: {testimonial.ip_address}
        """
        
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        
        return f'Notificação de depoimento enviada'
    except Exception as e:
        return f'Erro ao enviar notificação de depoimento: {str(e)}'

@shared_task
def cleanup_old_sessions():
    """Limpar sessões antigas"""
    from django.contrib.sessions.models import Session
    from django.utils import timezone
    
    # Remover sessões expiradas
    expired_sessions = Session.objects.filter(expire_date__lt=timezone.now())
    count = expired_sessions.count()
    expired_sessions.delete()
    
    return f'{count} sessões expiradas removidas'

@shared_task
def send_weekly_newsletter():
    """Enviar newsletter semanal"""
    from newsletter.models import NewsletterSubscriber
    from core.models import BlogPost
    
    try:
        # Buscar posts da semana
        week_ago = timezone.now() - timedelta(days=7)
        recent_posts = BlogPost.objects.filter(
            status='published',
            published_at__gte=week_ago
        ).order_by('-published_at')[:3]
        
        # Assinantes ativos
        subscribers = NewsletterSubscriber.objects.filter(
            is_active=True,
            is_verified=True,
            frequency__in=['weekly', 'monthly']
        )
        
        subject = 'Newsletter Semanal ASBJJ - Novidades e Dicas'
        
        for subscriber in subscribers:
            html_content = render_to_string('emails/weekly_newsletter.html', {
                'subscriber': subscriber,
                'posts': recent_posts,
                'site_url': settings.SITE_URL,
                'unsubscribe_url': f"{settings.SITE_URL}/newsletter/descadastrar/{subscriber.unsubscribe_token}/",
            })
            
            text_content = f"""
Olá {subscriber.full_name or 'Prezado(a)'},

Confira as novidades desta semana na ASBJJ:

"""
            for post in recent_posts:
                text_content += f"- {post.title}\n  {post.excerpt}\n  Leia mais: {settings.SITE_URL}{post.get_absolute_url()}\n\n"
            
            text_content += f"""
Para se descadastrar, acesse: {settings.SITE_URL}/newsletter/descadastrar/{subscriber.unsubscribe_token}/

Atenciosamente,
Equipe ASBJJ
            """
            
            msg = EmailMultiAlternatives(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [subscriber.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        
        return f'Newsletter semanal enviada para {subscribers.count()} assinantes'
    except Exception as e:
        return f'Erro ao enviar newsletter semanal: {str(e)}'
