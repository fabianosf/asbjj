from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView, CreateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q, Avg
from django.http import JsonResponse
from django.core.paginator import Paginator

from .models import Testimonial, Review, FAQ
from core.forms import TestimonialForm
from classes.models import Class


class TestimonialListView(ListView):
    """Lista de depoimentos aprovados"""
    model = Testimonial
    template_name = 'testimonials/list.html'
    context_object_name = 'testimonials'
    paginate_by = 12

    def get_queryset(self):
        return Testimonial.objects.filter(
            status='approved'
        ).order_by('-is_featured', '-approved_at', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Depoimentos em destaque
        context['featured_testimonials'] = Testimonial.objects.filter(
            status='approved',
            is_featured=True
        ).order_by('-approved_at')[:6]
        
        # Estatísticas
        context['total_testimonials'] = Testimonial.objects.filter(status='approved').count()
        context['average_rating'] = Testimonial.objects.filter(
            status='approved'
        ).aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        
        return context


class TestimonialCreateView(CreateView):
    """Criar novo depoimento"""
    model = Testimonial
    form_class = TestimonialForm
    template_name = 'testimonials/create.html'
    success_url = reverse_lazy('testimonials:create_success')

    def form_valid(self, form):
        # Salvar o depoimento
        testimonial = form.save(commit=False)
        testimonial.ip_address = self.get_client_ip()
        testimonial.user_agent = self.request.META.get('HTTP_USER_AGENT', '')
        testimonial.save()

        # Enviar notificação para o administrador
        try:
            self.send_notification_email(testimonial)
        except Exception as e:
            pass

        messages.success(
            self.request,
            'Seu depoimento foi enviado com sucesso! Será publicado após aprovação.'
        )
        return super().form_valid(form)

    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

    def send_notification_email(self, testimonial):
        """Enviar notificação de novo depoimento"""
        from django.core.mail import send_mail
        from django.conf import settings

        subject = f'[ASBJJ] Novo depoimento aguardando aprovação - {testimonial.author_name}'
        message = f"""
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
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=False,
        )


class TestimonialDetailView(DetailView):
    """Detalhes de um depoimento"""
    model = Testimonial
    template_name = 'testimonials/detail.html'
    context_object_name = 'testimonial'

    def get_queryset(self):
        return Testimonial.objects.filter(status='approved')


class ReviewCreateView(CreateView):
    """Criar avaliação de aula"""
    model = Review
    fields = ['title', 'content', 'instructor_rating', 'content_rating', 'facility_rating', 'overall_rating']
    template_name = 'testimonials/create_review.html'
    success_url = reverse_lazy('testimonials:create_review_success')

    def dispatch(self, request, *args, **kwargs):
        self.class_obj = get_object_or_404(Class, id=self.kwargs['class_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['class_obj'] = self.class_obj
        return context

    def form_valid(self, form):
        review = form.save(commit=False)
        review.user = self.request.user
        review.class_obj = self.class_obj
        review.save()

        messages.success(
            self.request,
            'Sua avaliação foi enviada com sucesso!'
        )
        return super().form_valid(form)


class FAQView(TemplateView):
    """Página de perguntas frequentes"""
    template_name = 'testimonials/faq.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Agrupar FAQs por categoria
        faqs_by_category = {}
        for category, _ in FAQ._meta.get_field('category').choices:
            faqs = FAQ.objects.filter(category=category, is_active=True).order_by('order')
            if faqs.exists():
                faqs_by_category[category] = faqs
        
        context['faqs_by_category'] = faqs_by_category
        return context


class TestimonialCreateSuccessView(TemplateView):
    """Página de sucesso ao criar depoimento"""
    template_name = 'testimonials/create_success.html'


class ReviewCreateSuccessView(TemplateView):
    """Página de sucesso ao criar avaliação"""
    template_name = 'testimonials/create_review_success.html'


def search_testimonials(request):
    """Buscar depoimentos"""
    if request.method == 'GET':
        query = request.GET.get('q', '').strip()
        category = request.GET.get('category', '')
        rating = request.GET.get('rating', '')
        
        testimonials = Testimonial.objects.filter(status='approved')
        
        if query:
            testimonials = testimonials.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(author_name__icontains=query)
            )
        
        if category:
            testimonials = testimonials.filter(class_related__category__slug=category)
        
        if rating:
            testimonials = testimonials.filter(rating=int(rating))
        
        testimonials = testimonials.order_by('-is_featured', '-approved_at')
        
        # Paginação
        paginator = Paginator(testimonials, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'testimonials': page_obj,
            'query': query,
            'selected_category': category,
            'selected_rating': rating,
            'categories': Class.objects.values_list('category__name', 'category__slug').distinct()
        }
        
        return render(request, 'testimonials/search_results.html', context)
    
    return redirect('testimonials:list')


def testimonial_stats_api(request):
    """API para estatísticas de depoimentos"""
    if request.method == 'GET':
        try:
            # Total de depoimentos
            total_testimonials = Testimonial.objects.filter(status='approved').count()
            
            # Média de avaliações
            average_rating = Testimonial.objects.filter(
                status='approved'
            ).aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
            
            # Distribuição por estrelas
            rating_distribution = {}
            for i in range(1, 6):
                count = Testimonial.objects.filter(
                    status='approved',
                    rating=i
                ).count()
                rating_distribution[i] = count
            
            # Depoimentos por categoria de aula
            category_stats = {}
            for testimonial in Testimonial.objects.filter(status='approved', class_related__isnull=False):
                category_name = testimonial.class_related.category.name
                if category_name not in category_stats:
                    category_stats[category_name] = 0
                category_stats[category_name] += 1
            
            # Depoimentos recentes
            recent_testimonials = Testimonial.objects.filter(
                status='approved'
            ).order_by('-approved_at')[:5]
            
            recent_data = []
            for testimonial in recent_testimonials:
                recent_data.append({
                    'id': testimonial.id,
                    'author_name': testimonial.author_name,
                    'title': testimonial.title,
                    'rating': testimonial.rating,
                    'approved_at': testimonial.approved_at.strftime('%d/%m/%Y') if testimonial.approved_at else None
                })
            
            data = {
                'total_testimonials': total_testimonials,
                'average_rating': round(average_rating, 1),
                'rating_distribution': rating_distribution,
                'category_stats': category_stats,
                'recent_testimonials': recent_data
            }
            
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)
