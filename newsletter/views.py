from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, FormView
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

from .models import NewsletterSubscriber, NewsletterCampaign, EmailLog
from core.forms import NewsletterForm


class NewsletterSubscribeView(FormView):
    """Inscrição na newsletter"""
    form_class = NewsletterForm
    template_name = 'newsletter/subscribe.html'
    success_url = reverse_lazy('newsletter:subscribe_success')

    def form_valid(self, form):
        # Verificar se já existe uma inscrição ativa
        email = form.cleaned_data['email']
        existing_subscriber = NewsletterSubscriber.objects.filter(
            email=email,
            is_active=True
        ).first()

        if existing_subscriber:
            messages.info(
                self.request,
                'Este e-mail já está cadastrado em nossa newsletter.'
            )
            return redirect('newsletter:subscribe_success')

        # Criar nova inscrição
        subscriber = form.save(commit=False)
        subscriber.ip_address = self.get_client_ip()
        subscriber.user_agent = self.request.META.get('HTTP_USER_AGENT', '')
        subscriber.source = self.request.GET.get('source', 'website')
        subscriber.save()

        # Enviar e-mail de confirmação
        try:
            self.send_confirmation_email(subscriber)
        except Exception as e:
            pass

        messages.success(
            self.request,
            'Inscrição realizada com sucesso! Verifique seu e-mail para confirmar.'
        )
        return super().form_valid(form)

    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

    def send_confirmation_email(self, subscriber):
        """Enviar e-mail de confirmação"""
        subject = 'Confirme sua inscrição na newsletter ASBJJ'
        
        confirmation_url = f"{settings.SITE_URL}/newsletter/confirmar/{subscriber.verification_token}/"
        
        message = f"""
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
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [subscriber.email],
            fail_silently=False,
        )


class NewsletterConfirmView(TemplateView):
    """Confirmar inscrição na newsletter"""
    template_name = 'newsletter/confirm.html'

    def get(self, request, *args, **kwargs):
        token = kwargs.get('token')
        subscriber = get_object_or_404(
            NewsletterSubscriber,
            verification_token=token,
            is_active=True
        )

        if not subscriber.is_verified:
            subscriber.is_verified = True
            subscriber.save()

            # Enviar e-mail de boas-vindas
            try:
                self.send_welcome_email(subscriber)
            except Exception as e:
                pass

            messages.success(
                request,
                'Inscrição confirmada com sucesso! Bem-vindo(a) à nossa newsletter.'
            )
        else:
            messages.info(
                request,
                'Sua inscrição já estava confirmada.'
            )

        return super().get(request, *args, **kwargs)

    def send_welcome_email(self, subscriber):
        """Enviar e-mail de boas-vindas"""
        subject = 'Bem-vindo(a) à newsletter ASBJJ!'

        message = f"""
Olá {subscriber.full_name or 'Prezado(a)'},

Seja bem-vindo(a) à família ASBJJ!

Sua inscrição na newsletter foi confirmada com sucesso. A partir de agora, você receberá:

🎯 Novidades sobre nossas modalidades (Jiu-Jitsu, Defesa Pessoal, Yoga)
💪 Dicas de treino e condicionamento físico
🍎 Orientações sobre nutrição e saúde
🏆 Eventos, competições e graduações
🎁 Promoções e ofertas especiais
📚 Conteúdo exclusivo sobre artes marciais

Nossa newsletter é enviada semanalmente e você pode cancelar a qualquer momento.

Para gerenciar suas preferências ou se descadastrar, use o link no rodapé dos nossos e-mails.

Atenciosamente,
Equipe ASBJJ - Alexandre Salgado Brazilian Jiu-Jitsu

---
ASBJJ - Alexandre Salgado Brazilian Jiu-Jitsu
📍 {settings.SITE_URL}
📧 {settings.ADMIN_EMAIL}
📱 {settings.WHATSAPP_NUMBER}
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [subscriber.email],
            fail_silently=False,
        )


class NewsletterUnsubscribeView(TemplateView):
    """Descadastrar da newsletter"""
    template_name = 'newsletter/unsubscribe.html'

    def get(self, request, *args, **kwargs):
        token = kwargs.get('token')
        self.subscriber = get_object_or_404(
            NewsletterSubscriber,
            unsubscribe_token=token,
            is_active=True
        )
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        token = kwargs.get('token')
        subscriber = get_object_or_404(
            NewsletterSubscriber,
            unsubscribe_token=token,
            is_active=True
        )

        reason = request.POST.get('reason', '')
        
        # Desativar inscrição
        subscriber.is_active = False
        subscriber.save()

        # Enviar confirmação de descadastro
        try:
            self.send_unsubscribe_confirmation(subscriber, reason)
        except Exception as e:
            pass

        messages.success(
            request,
            'Você foi descadastrado da nossa newsletter com sucesso.'
        )
        
        return redirect('newsletter:unsubscribe_success')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subscriber'] = self.subscriber
        return context

    def send_unsubscribe_confirmation(self, subscriber, reason):
        """Enviar confirmação de descadastro"""
        subject = 'Confirmação de descadastro - Newsletter ASBJJ'

        message = f"""
Olá {subscriber.full_name or 'Prezado(a)'},

Confirmamos que você foi descadastrado da nossa newsletter.

Motivo informado: {reason or 'Não informado'}

Se foi um erro e você deseja se inscrever novamente, visite nosso site:
{settings.SITE_URL}/newsletter/inscrever/

Obrigado por ter sido nosso assinante!

Atenciosamente,
Equipe ASBJJ - Alexandre Salgado Brazilian Jiu-Jitsu
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [subscriber.email],
            fail_silently=False,
        )


class NewsletterPreferencesView(TemplateView):
    """Gerenciar preferências da newsletter"""
    template_name = 'newsletter/preferences.html'

    def get(self, request, *args, **kwargs):
        token = kwargs.get('token')
        self.subscriber = get_object_or_404(
            NewsletterSubscriber,
            unsubscribe_token=token,
            is_active=True
        )
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        token = kwargs.get('token')
        subscriber = get_object_or_404(
            NewsletterSubscriber,
            unsubscribe_token=token,
            is_active=True
        )

        # Atualizar preferências
        subscriber.frequency = request.POST.get('frequency', subscriber.frequency)
        subscriber.interests = request.POST.getlist('interests')
        subscriber.email_notifications = 'email_notifications' in request.POST
        subscriber.whatsapp_notifications = 'whatsapp_notifications' in request.POST
        subscriber.save()

        messages.success(
            request,
            'Suas preferências foram atualizadas com sucesso!'
        )
        
        return redirect('newsletter:preferences', token=token)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subscriber'] = self.subscriber
        return context


class NewsletterSubscribeSuccessView(TemplateView):
    """Página de sucesso da inscrição"""
    template_name = 'newsletter/subscribe_success.html'


class NewsletterUnsubscribeSuccessView(TemplateView):
    """Página de sucesso do descadastro"""
    template_name = 'newsletter/unsubscribe_success.html'


def newsletter_stats_api(request):
    """API para estatísticas da newsletter"""
    if request.method == 'GET':
        try:
            # Total de assinantes
            total_subscribers = NewsletterSubscriber.objects.filter(is_active=True).count()
            verified_subscribers = NewsletterSubscriber.objects.filter(
                is_active=True, 
                is_verified=True
            ).count()
            
            # Assinantes por frequência
            frequency_stats = {}
            for frequency, _ in NewsletterSubscriber._meta.get_field('frequency').choices:
                count = NewsletterSubscriber.objects.filter(
                    is_active=True,
                    frequency=frequency
                ).count()
                frequency_stats[frequency] = count
            
            # Assinantes por mês (últimos 12 meses)
            monthly_stats = []
            for i in range(12):
                month = timezone.now().replace(day=1) - timezone.timedelta(days=30*i)
                count = NewsletterSubscriber.objects.filter(
                    subscription_date__year=month.year,
                    subscription_date__month=month.month,
                    is_active=True
                ).count()
                monthly_stats.append({
                    'month': month.strftime('%m/%Y'),
                    'count': count
                })
            
            monthly_stats.reverse()
            
            # Campanhas recentes
            recent_campaigns = NewsletterCampaign.objects.order_by('-created_at')[:5]
            campaigns_data = []
            for campaign in recent_campaigns:
                campaigns_data.append({
                    'title': campaign.title,
                    'status': campaign.get_status_display(),
                    'total_sent': campaign.total_sent,
                    'total_opened': campaign.total_opened,
                    'open_rate': round((campaign.total_opened / campaign.total_sent * 100), 1) if campaign.total_sent > 0 else 0,
                    'created_at': campaign.created_at.strftime('%d/%m/%Y')
                })
            
            data = {
                'total_subscribers': total_subscribers,
                'verified_subscribers': verified_subscribers,
                'verification_rate': round((verified_subscribers / total_subscribers * 100), 1) if total_subscribers > 0 else 0,
                'frequency_stats': frequency_stats,
                'monthly_stats': monthly_stats,
                'recent_campaigns': campaigns_data
            }
            
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)
