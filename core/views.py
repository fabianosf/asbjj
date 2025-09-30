from django.shortcuts import render, get_object_or_404, redirect
from django import forms
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.views.generic import TemplateView, ListView, DetailView, FormView
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods

from .models import SiteSettings, ContactMessage, Instructor, Gallery, BlogPost, Product, ProductCategory, ProductReview, Cart, CartItem, Order, OrderItem, Coupon, Wishlist, WishlistItem
from .payment_service import mercado_pago_service
from .forms import ContactForm, TrialClassBookingForm
from students.models import Student


class HomeView(TemplateView):
    """Página inicial"""
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Configurações do site
        try:
            context['site_settings'] = SiteSettings.objects.first()
        except:
            context['site_settings'] = None
        
        # Instrutores
        context['featured_instructors'] = Instructor.objects.filter(is_active=True, is_featured=True)[:4]
        
        # Galeria
        context['gallery_images'] = Gallery.objects.filter(is_featured=True)[:8]
        
        # Blog posts recentes
        context['recent_posts'] = BlogPost.objects.filter(
            status='published'
        ).order_by('-published_at')[:3]
        
        return context


class AboutView(TemplateView):
    """Página sobre"""
    template_name = 'core/sobre.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Instrutores
        context['instructors'] = Instructor.objects.filter(is_active=True)
        
        # Configurações do site
        try:
            context['site_settings'] = SiteSettings.objects.first()
        except:
            context['site_settings'] = None
        
        return context


class ServicesView(TemplateView):
    """Página de serviços"""
    template_name = 'core/servicos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Configurações do site
        try:
            context['site_settings'] = SiteSettings.objects.first()
        except:
            context['site_settings'] = None
        
        return context


class ContactView(FormView):
    """Página de contato"""
    template_name = 'core/contato.html'
    form_class = ContactForm
    success_url = reverse_lazy('core:contact')

    def form_valid(self, form):
        # Salvar a mensagem
        contact_message = form.save(commit=False)
        contact_message.ip_address = self.get_client_ip()
        contact_message.user_agent = self.request.META.get('HTTP_USER_AGENT', '')
        contact_message.save()

        # Enviar notificação por e-mail
        try:
            self.send_notification_email(contact_message)
        except Exception as e:
            # Log do erro, mas não falha o processo
            pass
        
        # Enviar notificação via WhatsApp
        try:
            self.send_whatsapp_notification(contact_message)
        except Exception as e:
            # Log do erro, mas não falha o processo
            pass

        messages.success(
            self.request, 
            'Sua mensagem foi enviada com sucesso! Entraremos em contato em breve.'
        )
        return super().form_valid(form)

    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

    def send_notification_email(self, contact_message):
        """Envia e-mail de notificação para o administrador"""
        from django.core.mail import EmailMultiAlternatives
        from django.template.loader import render_to_string
        
        subject = f'[ASBJJ] Nova mensagem de contato de {contact_message.name}'
        
        # Template HTML
        html_content = render_to_string('emails/contact_notification.html', {
            'contact_message': contact_message,
            'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://127.0.0.1:8001',
        })
        
        # Texto simples para fallback
        text_content = f"""
Nova mensagem de contato recebida:

Nome: {contact_message.name}
E-mail: {contact_message.email}
Telefone: {contact_message.phone or 'Não informado'}
Categoria: {contact_message.get_category_display()}

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
            [settings.ADMIN_EMAIL if hasattr(settings, 'ADMIN_EMAIL') else 'admin@asbjj.com.br'],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    
    def send_whatsapp_notification(self, contact_message):
        """Envia notificação via WhatsApp"""
        import urllib.parse
        
        # Número do WhatsApp do administrador (configurável via settings)
        admin_whatsapp = getattr(settings, 'ADMIN_WHATSAPP', None)
        
        if not admin_whatsapp:
            return
        
        # Formatar a mensagem
        mensagem = f"""🔔 *Nova mensagem de contato ASBJJ*

👤 *Nome:* {contact_message.name}
📧 *E-mail:* {contact_message.email}
📱 *Telefone:* {contact_message.phone or 'Não informado'}
📋 *Categoria:* {contact_message.get_category_display()}

💬 *Mensagem:*
{contact_message.message}

⏰ Enviado em: {contact_message.created_at.strftime('%d/%m/%Y às %H:%M')}"""
        
        # Criar URL do WhatsApp
        mensagem_encoded = urllib.parse.quote(mensagem)
        whatsapp_url = f"https://api.whatsapp.com/send?phone={admin_whatsapp}&text={mensagem_encoded}"
        
        # Armazenar URL para uso posterior (opcional)
        contact_message.whatsapp_url = whatsapp_url
        contact_message.save(update_fields=['whatsapp_url'])
        
        # Em produção, você pode usar uma API do WhatsApp Business
        # Para desenvolvimento, apenas armazenamos a URL


# Views antigas para compatibilidade
def index(request):
    """View antiga da página inicial"""
    return HomeView.as_view()(request)


def sobre(request):
    """View antiga da página sobre"""
    return AboutView.as_view()(request)


def servicos(request):
    """View antiga da página de serviços"""
    return ServicesView.as_view()(request)


def contato(request):
    """View antiga da página de contato"""
    if request.method == 'POST':
        return ContactView.as_view()(request)
    else:
        return ContactView.as_view()(request)


@require_http_methods(["GET"])
def healthz(request):
    """Endpoint de health-check simples"""
    return JsonResponse({
        'status': 'ok',
        'time': timezone.now().isoformat(),
        'debug': settings.DEBUG,
    })


def csrf_failure(request, reason=""):
    """Custom CSRF failure view"""
    from django.http import JsonResponse
    from django.template.loader import render_to_string
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'error': 'CSRF token missing or incorrect',
            'detail': 'Please refresh the page and try again.'
        }, status=403)
    
    return render(request, 'core/csrf_failure.html', {
        'reason': reason
    }, status=403)


class GalleryListView(ListView):
    """Galeria de fotos"""
    model = Gallery
    template_name = 'core/galeria.html'
    context_object_name = 'images'
    paginate_by = 24

    def get_queryset(self):
        queryset = Gallery.objects.all().order_by('order', '-created_at')
        category = self.request.GET.get('categoria')
        if category:
            queryset = queryset.filter(category=category)
        return queryset


class BlogListView(ListView):
    """Lista de posts do blog"""
    model = BlogPost
    template_name = 'core/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = BlogPost.objects.filter(status='published').order_by('-published_at')
        category = self.request.GET.get('categoria')
        if category:
            queryset = queryset.filter(category=category)
        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(Q(title__icontains=search) | Q(content__icontains=search))
        return queryset


class BlogDetailView(DetailView):
    """Detalhe do post do blog"""
    model = BlogPost
    template_name = 'core/blog_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'


class EnrollmentApplicationView(FormView):
    """Formulário de inscrição de novos alunos"""
    template_name = 'core/inscricao.html'
    success_url = reverse_lazy('core:enrollment')

    class EnrollmentForm(forms.Form):
        first_name = forms.CharField(label='Nome', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
        last_name = forms.CharField(label='Sobrenome', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
        email = forms.EmailField(label='E-mail', widget=forms.EmailInput(attrs={'class': 'form-control'}))
        phone = forms.CharField(label='Telefone', max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
        birth_date = forms.DateField(label='Data de Nascimento', widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
        cpf = forms.CharField(label='CPF', max_length=14, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}))
        address = forms.CharField(label='Endereço', widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))
        city = forms.CharField(label='Cidade', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
        state = forms.CharField(label='Estado', max_length=2, widget=forms.TextInput(attrs={'class': 'form-control'}))
        zip_code = forms.CharField(label='CEP', max_length=10, widget=forms.TextInput(attrs={'class': 'form-control'}))
        whatsapp = forms.CharField(label='WhatsApp', max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
        medical_conditions = forms.CharField(label='Condições Médicas', required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
        allergies = forms.CharField(label='Alergias', required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))

        def clean_cpf(self):
            cpf = self.cleaned_data.get('cpf', '').strip()
            # Normalizar apenas dígitos
            digits = ''.join(filter(str.isdigit, cpf))
            if len(digits) != 11:
                raise ValidationError('CPF deve ter 11 dígitos.')
            # Rejeitar CPFs com todos dígitos iguais
            if digits == digits[0] * 11:
                raise ValidationError('CPF inválido.')
            # Validar dígitos verificadores
            def calc_dv(nums, factor):
                total = 0
                for n in nums:
                    total += int(n) * factor
                    factor -= 1
                resto = (total * 10) % 11
                return '0' if resto == 10 else str(resto)
            dv1 = calc_dv(digits[:9], 10)
            dv2 = calc_dv(digits[:10], 11)
            if digits[-2:] != dv1 + dv2:
                raise ValidationError('CPF inválido.')
            # Formatar
            cpf_formatted = f"{digits[0:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:11]}"
            if Student.objects.filter(cpf=cpf_formatted).exists() or Student.objects.filter(cpf=digits).exists():
                raise ValidationError('Este CPF já está cadastrado.')
            return cpf_formatted

        def clean_email(self):
            email = self.cleaned_data.get('email', '').strip().lower()
            if Student.objects.filter(email=email).exists():
                raise ValidationError('Este e-mail já está cadastrado.')
            return email

    form_class = EnrollmentForm

    def form_valid(self, form):
        # Validações de unicidade extras para evitar erro 500
        if Student.objects.filter(cpf=form.cleaned_data['cpf']).exists():
            form.add_error('cpf', 'Este CPF já está cadastrado.')
            return self.form_invalid(form)
        if Student.objects.filter(email=form.cleaned_data['email']).exists():
            form.add_error('email', 'Este e-mail já está cadastrado.')
            return self.form_invalid(form)

        try:
            # Criar registro básico de aluno (sem exigir login)
            Student.objects.create(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                whatsapp=form.cleaned_data.get('whatsapp', ''),
                cpf=form.cleaned_data['cpf'],
                rg='',
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                state=form.cleaned_data['state'],
                zip_code=form.cleaned_data['zip_code'],
                birth_date=form.cleaned_data['birth_date'],
                emergency_contact_name=form.cleaned_data['first_name'] + ' ' + form.cleaned_data['last_name'],
                emergency_contact_phone=form.cleaned_data['phone'],
                medical_conditions=form.cleaned_data.get('medical_conditions', ''),
                allergies=form.cleaned_data.get('allergies', ''),
                created_by=None,
            )
        except IntegrityError:
            # Fallback: caso outro campo único conflite
            form.add_error(None, 'Não foi possível concluir a inscrição. Verifique os dados e tente novamente.')
            return self.form_invalid(form)

        messages.success(self.request, 'Inscrição enviada! Entraremos em contato para finalizar a matrícula.')
        return super().form_valid(form)


class CalendarView(TemplateView):
    """Calendário de eventos/competições"""
    template_name = 'core/calendario.html'


class ShopView(ListView):
    """Loja com filtros e ordenação"""
    model = Product
    template_name = 'core/loja.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(status='published').select_related('category')
        
        # Filtro por categoria
        category_slug = self.request.GET.get('categoria')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Filtro por cor
        color = self.request.GET.get('cor')
        if color:
            queryset = queryset.filter(colors__contains=[color])
        
        # Filtro por tamanho
        size = self.request.GET.get('tamanho')
        if size:
            queryset = queryset.filter(sizes__contains=[size])
        
        # Busca por texto
        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) |
                Q(short_description__icontains=search)
            )
        
        # Ordenação
        order = self.request.GET.get('ordenar', 'novidades')
        if order == 'preco_menor':
            queryset = queryset.order_by('price')
        elif order == 'preco_maior':
            queryset = queryset.order_by('-price')
        elif order == 'nome':
            queryset = queryset.order_by('name')
        elif order == 'mais_vendidos':
            queryset = queryset.filter(is_bestseller=True).order_by('-view_count')
        else:  # novidades (padrão)
            queryset = queryset.order_by('-created_at')
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Categorias para filtro
        context['categories'] = ProductCategory.objects.filter(is_active=True)
        
        # Cores disponíveis
        colors = set()
        for product in Product.objects.filter(status='published'):
            colors.update(product.colors or [])
        context['available_colors'] = sorted(colors)
        
        # Tamanhos disponíveis
        sizes = set()
        for product in Product.objects.filter(status='published'):
            sizes.update(product.sizes or [])
        context['available_sizes'] = sorted(sizes)
        
        # Parâmetros de filtro atuais
        context['current_category'] = self.request.GET.get('categoria', '')
        context['current_color'] = self.request.GET.get('cor', '')
        context['current_size'] = self.request.GET.get('tamanho', '')
        context['current_search'] = self.request.GET.get('q', '')
        context['current_order'] = self.request.GET.get('ordenar', 'novidades')
        
        # Contagem de produtos
        context['total_products'] = self.get_queryset().count()
        
        return context


class ProductDetailView(DetailView):
    """Detalhe do produto"""
    model = Product
    template_name = 'core/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'

    def get_queryset(self):
        return Product.objects.filter(status='published').select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Produtos relacionados
        context['related_products'] = Product.objects.filter(
            category=self.object.category,
            status='published'
        ).exclude(id=self.object.id)[:4]
        
        # Avaliações aprovadas
        context['reviews'] = ProductReview.objects.filter(
            product=self.object,
            is_approved=True
        ).order_by('-created_at')[:10]
        
        # Média de avaliações
        reviews = context['reviews']
        if reviews:
            context['average_rating'] = sum(r.rating for r in reviews) / len(reviews)
            context['total_reviews'] = len(reviews)
        else:
            context['average_rating'] = 0
            context['total_reviews'] = 0
        
        # Incrementar contador de visualizações
        self.object.view_count += 1
        self.object.save(update_fields=['view_count'])
        
        return context


class ShopCategoryView(ListView):
    """Loja filtrada por categoria"""
    model = Product
    template_name = 'core/loja.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        self.category = get_object_or_404(ProductCategory, slug=self.kwargs['slug'], is_active=True)
        return Product.objects.filter(
            category=self.category,
            status='published'
        ).select_related('category').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = ProductCategory.objects.filter(is_active=True)
        return context


def get_or_create_cart(request):
    """Obtém ou cria carrinho baseado na sessão"""
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    
    cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


class CartView(TemplateView):
    """Visualização do carrinho"""
    template_name = 'core/cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = get_or_create_cart(self.request)
        context['cart'] = cart
        context['cart_items'] = cart.items.select_related('product')
        return context


@require_http_methods(["POST"])
def add_to_cart(request, product_id):
    """Adiciona produto ao carrinho"""
    try:
        product = Product.objects.get(id=product_id, status='published')
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            return JsonResponse({'success': False, 'message': 'Quantidade inválida'})
        
        cart = get_or_create_cart(request)
        cart_item = cart.add_item(product, quantity)
        
        # Verificar se é uma requisição AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'{product.name} adicionado ao carrinho',
                'cart_total_items': cart.total_items,
                'cart_total_price': float(cart.total_price),
                'cart_total_price_formatted': f'R$ {cart.total_price:.2f}'.replace('.', ','),
                'item_price': float(product.price),
                'item_price_formatted': f'R$ {product.price:.2f}'.replace('.', ','),
                'item_quantity': quantity
            })
        else:
            # Redirecionar para a loja com mensagem de sucesso
            from django.contrib import messages
            messages.success(request, f'{product.name} adicionado ao carrinho!')
            return redirect('core:shop')
    
    except Product.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Produto não encontrado'})
        else:
            from django.contrib import messages
            messages.error(request, 'Produto não encontrado')
            return redirect('core:shop')
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Erro ao adicionar produto'})
        else:
            from django.contrib import messages
            messages.error(request, 'Erro ao adicionar produto')
            return redirect('core:shop')


@require_http_methods(["POST"])
def remove_from_cart(request, product_id):
    """Remove produto do carrinho"""
    try:
        product = Product.objects.get(id=product_id)
        cart = get_or_create_cart(request)
        cart.remove_item(product)
        
        return JsonResponse({
            'success': True,
            'message': f'{product.name} removido do carrinho',
            'cart_total_items': cart.total_items,
            'cart_total_price': float(cart.total_price)
        })
    
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Produto não encontrado'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Erro ao remover produto'})


@require_http_methods(["POST"])
def update_cart_item(request, item_id):
    """Atualiza quantidade de item no carrinho"""
    try:
        cart_item = CartItem.objects.get(id=item_id)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()
        
        cart = cart_item.cart
        return JsonResponse({
            'success': True,
            'cart_total_items': cart.total_items,
            'cart_total_price': float(cart.total_price),
            'item_total_price': float(cart_item.total_price)
        })
    
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Item não encontrado'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Erro ao atualizar item'})


@require_http_methods(["POST"])
def clear_cart(request):
    """Limpa o carrinho"""
    cart = get_or_create_cart(request)
    cart.clear()
    
    return JsonResponse({
        'success': True,
        'message': 'Carrinho limpo',
        'cart_total_items': 0,
        'cart_total_price': 0
    })


@require_http_methods(["GET"])
def cart_total(request):
    """Retorna o total do carrinho"""
    cart = get_or_create_cart(request)
    return JsonResponse({
        'success': True,
        'cart_total_items': cart.total_items,
        'cart_total_price': float(cart.total_price),
        'cart_total_price_formatted': f'R$ {cart.total_price:.2f}'.replace('.', ',')
    })


class CheckoutView(FormView):
    """Checkout do pedido"""
    template_name = 'core/checkout.html'
    success_url = reverse_lazy('core:order_success')

    class CheckoutForm(forms.Form):
        # Informações do cliente
        customer_name = forms.CharField(
            label='Nome Completo',
            max_length=200,
            widget=forms.TextInput(attrs={'class': 'form-control'})
        )
        customer_email = forms.EmailField(
            label='E-mail',
            widget=forms.EmailInput(attrs={'class': 'form-control'})
        )
        customer_phone = forms.CharField(
            label='Telefone',
            max_length=20,
            widget=forms.TextInput(attrs={'class': 'form-control'})
        )
        
        # Endereço de entrega
        shipping_address = forms.CharField(
            label='Endereço',
            widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        )
        shipping_city = forms.CharField(
            label='Cidade',
            max_length=100,
            widget=forms.TextInput(attrs={'class': 'form-control'})
        )
        shipping_state = forms.CharField(
            label='Estado',
            max_length=2,
            widget=forms.TextInput(attrs={'class': 'form-control'})
        )
        shipping_zip_code = forms.CharField(
            label='CEP',
            max_length=10,
            widget=forms.TextInput(attrs={'class': 'form-control'})
        )
        
        # Método de pagamento
        payment_method = forms.ChoiceField(
            label='Método de Pagamento',
            choices=[
                ('pix', 'PIX'),
                ('credit_card', 'Cartão de Crédito'),
                ('debit_card', 'Cartão de Débito'),
                ('bank_transfer', 'Transferência Bancária'),
            ],
            widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
        )
        
        # Observações
        notes = forms.CharField(
            label='Observações',
            required=False,
            widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        )

    form_class = CheckoutForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = get_or_create_cart(self.request)
        context['cart'] = cart
        context['cart_items'] = cart.items.select_related('product')
        return context

    def form_valid(self, form):
        cart = get_or_create_cart(self.request)
        
        if cart.total_items == 0:
            messages.error(self.request, 'Seu carrinho está vazio')
            return self.form_invalid(form)
        
        # Criar pedido
        order = Order.objects.create(
            customer_name=form.cleaned_data['customer_name'],
            customer_email=form.cleaned_data['customer_email'],
            customer_phone=form.cleaned_data['customer_phone'],
            shipping_address=form.cleaned_data['shipping_address'],
            shipping_city=form.cleaned_data['shipping_city'],
            shipping_state=form.cleaned_data['shipping_state'],
            shipping_zip_code=form.cleaned_data['shipping_zip_code'],
            payment_method=form.cleaned_data['payment_method'],
            notes=form.cleaned_data['notes'],
            subtotal=cart.total_price,
            shipping_cost=0,  # Frete grátis por enquanto
            total=cart.total_price
        )
        
        # Criar itens do pedido
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price,
                total_price=cart_item.total_price
            )
        
        # Limpar carrinho
        cart.clear()
        
        # Salvar ID do pedido na sessão para redirecionamento
        self.request.session['order_id'] = order.id
        
        # Redirecionar para página de pagamento
        from django.http import HttpResponseRedirect
        from django.urls import reverse
        return HttpResponseRedirect(reverse('core:payment', kwargs={'order_id': order.id}))

    def send_order_confirmation_email(self, order):
        """Envia email de confirmação do pedido"""
        subject = f'[ASBJJ] Confirmação do Pedido {order.order_number}'
        message = f"""
Olá {order.customer_name},

Seu pedido foi confirmado com sucesso!

Número do Pedido: {order.order_number}
Data: {order.created_at.strftime('%d/%m/%Y %H:%M')}

Itens do Pedido:
"""
        
        for item in order.items.all():
            message += f"- {item.product.name} x{item.quantity} = R$ {item.total_price}\n"
        
        message += f"""
Subtotal: R$ {order.subtotal}
Frete: R$ {order.shipping_cost}
Total: R$ {order.total}

Método de Pagamento: {order.get_payment_method_display()}

Endereço de Entrega:
{order.shipping_address}
{order.shipping_city} - {order.shipping_state}
CEP: {order.shipping_zip_code}

Em breve entraremos em contato para finalizar o pagamento.

Obrigado por escolher a ASBJJ!

---
ASBJJ - Alexandre Salgado Brazilian Jiu-Jitsu
        """
        
        from django.core.mail import send_mail
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.customer_email],
            fail_silently=False,
        )


class OrderSuccessView(TemplateView):
    """Página de sucesso do pedido"""
    template_name = 'core/order_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.request.session.get('order_id')
        
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                context['order'] = order
                # Limpar ID da sessão
                del self.request.session['order_id']
            except Order.DoesNotExist:
                pass
        
        return context


class OrderDetailView(DetailView):
    """Detalhes do pedido"""
    model = Order
    template_name = 'core/order_detail.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_id'

    def get_queryset(self):
        return Order.objects.prefetch_related('items__product')


def get_or_create_wishlist(request):
    """Obtém ou cria lista de desejos baseada na sessão"""
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    
    wishlist, created = Wishlist.objects.get_or_create(session_key=session_key)
    return wishlist


class CustomerAreaView(TemplateView):
    """Área do cliente para acompanhar pedidos"""
    template_name = 'core/customer_area.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Buscar pedidos por email (simulação de área do cliente)
        email = self.request.GET.get('email', '')
        orders = []
        
        if email:
            orders = Order.objects.filter(
                customer_email__iexact=email
            ).prefetch_related('items__product').order_by('-created_at')
        
        context['orders'] = orders
        context['search_email'] = email
        return context


class WishlistView(TemplateView):
    """Lista de desejos"""
    template_name = 'core/wishlist.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wishlist = get_or_create_wishlist(self.request)
        context['wishlist'] = wishlist
        context['wishlist_items'] = wishlist.items.select_related('product')
        return context


@require_http_methods(["POST"])
def add_to_wishlist(request, product_id):
    """Adiciona produto à lista de desejos"""
    try:
        product = Product.objects.get(id=product_id, status='published')
        wishlist = get_or_create_wishlist(request)
        wishlist.add_item(product)
        
        return JsonResponse({
            'success': True,
            'message': f'{product.name} adicionado aos favoritos',
            'wishlist_total_items': wishlist.total_items
        })
    
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Produto não encontrado'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Erro ao adicionar aos favoritos'})


@require_http_methods(["POST"])
def remove_from_wishlist(request, product_id):
    """Remove produto da lista de desejos"""
    try:
        product = Product.objects.get(id=product_id)
        wishlist = get_or_create_wishlist(request)
        wishlist.remove_item(product)
        
        return JsonResponse({
            'success': True,
            'message': f'{product.name} removido dos favoritos',
            'wishlist_total_items': wishlist.total_items
        })
    
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Produto não encontrado'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Erro ao remover dos favoritos'})


@require_http_methods(["POST"])
def apply_coupon(request):
    """Aplica cupom de desconto"""
    try:
        coupon_code = request.POST.get('coupon_code', '').strip().upper()
        cart = get_or_create_cart(request)
        
        if not coupon_code:
            return JsonResponse({'success': False, 'message': 'Código do cupom é obrigatório'})
        
        try:
            coupon = Coupon.objects.get(code=coupon_code)
        except Coupon.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Cupom não encontrado'})
        
        if not coupon.is_valid():
            return JsonResponse({'success': False, 'message': 'Cupom inválido ou expirado'})
        
        discount = coupon.calculate_discount(cart.total_price)
        
        if discount <= 0:
            return JsonResponse({'success': False, 'message': 'Cupom não aplicável ao valor atual'})
        
        # Salvar cupom na sessão
        request.session['applied_coupon'] = {
            'code': coupon.code,
            'discount': float(discount),
            'discount_type': coupon.discount_type,
            'discount_value': float(coupon.discount_value)
        }
        
        return JsonResponse({
            'success': True,
            'message': f'Cupom {coupon.code} aplicado com sucesso!',
            'discount': float(discount),
            'new_total': float(cart.total_price - discount)
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Erro ao aplicar cupom'})


@require_http_methods(["POST"])
def remove_coupon(request):
    """Remove cupom aplicado"""
    if 'applied_coupon' in request.session:
        del request.session['applied_coupon']
    
    cart = get_or_create_cart(request)
    return JsonResponse({
        'success': True,
        'message': 'Cupom removido',
        'new_total': float(cart.total_price)
    })


def calculate_shipping(request):
    """Calcula frete por CEP"""
    cep = request.GET.get('cep', '').replace('-', '').replace(' ', '')
    
    if not cep or len(cep) != 8:
        return JsonResponse({'success': False, 'message': 'CEP inválido'})
    
    # Simulação de cálculo de frete
    # Em produção, integrar com API dos Correios ou transportadora
    try:
        cep_int = int(cep)
        
        # Regras de frete simuladas
        if cep_int >= 1000000 and cep_int <= 19999999:  # São Paulo
            shipping_cost = 15.00
            delivery_days = 1
        elif cep_int >= 20000000 and cep_int <= 29999999:  # Rio de Janeiro
            shipping_cost = 20.00
            delivery_days = 2
        elif cep_int >= 30000000 and cep_int <= 39999999:  # Minas Gerais
            shipping_cost = 25.00
            delivery_days = 3
        else:  # Outros estados
            shipping_cost = 30.00
            delivery_days = 5
        
        # Frete grátis para pedidos acima de R$ 200
        cart = get_or_create_cart(request)
        if cart.total_price >= 200:
            shipping_cost = 0
            delivery_days = max(1, delivery_days - 1)
        
        return JsonResponse({
            'success': True,
            'shipping_cost': shipping_cost,
            'delivery_days': delivery_days,
            'message': f'Frete: R$ {shipping_cost:.2f} - Entrega em {delivery_days} dia(s)'
        })
    
    except ValueError:
        return JsonResponse({'success': False, 'message': 'CEP inválido'})


class SalesReportView(TemplateView):
    """Relatório de vendas (admin)"""
    template_name = 'core/sales_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estatísticas de vendas
        from django.db.models import Sum, Count, Avg
        from datetime import datetime, timedelta
        
        today = datetime.now().date()
        this_month = today.replace(day=1)
        last_month = (this_month - timedelta(days=1)).replace(day=1)
        
        # Vendas do mês atual
        current_month_orders = Order.objects.filter(
            created_at__date__gte=this_month,
            payment_status='paid'
        )
        
        # Vendas do mês anterior
        last_month_orders = Order.objects.filter(
            created_at__date__gte=last_month,
            created_at__date__lt=this_month,
            payment_status='paid'
        )
        
        # Estatísticas
        context.update({
            'current_month_sales': current_month_orders.aggregate(
                total=Sum('total'),
                count=Count('id'),
                avg=Avg('total')
            ),
            'last_month_sales': last_month_orders.aggregate(
                total=Sum('total'),
                count=Count('id'),
                avg=Avg('total')
            ),
            'total_orders': Order.objects.count(),
            'pending_orders': Order.objects.filter(status='pending').count(),
            'paid_orders': Order.objects.filter(payment_status='paid').count(),
            'recent_orders': Order.objects.select_related().order_by('-created_at')[:10],
            'top_products': Product.objects.annotate(
                total_sold=Sum('orderitem__quantity')
            ).order_by('-total_sold')[:10]
        })
        
        return context


class PaymentView(TemplateView):
    """Página de pagamento"""
    template_name = 'core/payment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs.get('order_id')
        
        try:
            order = Order.objects.get(id=order_id)
            context['order'] = order
            
            # Criar preferência no Mercado Pago
            if order.payment_method in ['pix', 'credit_card', 'debit_card']:
                payment_result = mercado_pago_service.create_preference(order)
                
                if payment_result['success']:
                    context['payment_url'] = payment_result['init_point']
                    context['preference_id'] = payment_result['preference_id']
                else:
                    context['payment_error'] = payment_result['error']
            
        except Order.DoesNotExist:
            context['order'] = None
            context['payment_error'] = 'Pedido não encontrado'
        
        return context


@require_http_methods(["POST"])
def mercado_pago_webhook(request):
    """Webhook do Mercado Pago"""
    try:
        import json
        data = json.loads(request.body)
        
        result = mercado_pago_service.process_webhook(data)
        
        if result['success']:
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400)
            
    except Exception as e:
        return HttpResponse(status=500)


class PaymentSuccessView(TemplateView):
    """Página de sucesso do pagamento"""
    template_name = 'core/payment_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Parâmetros do Mercado Pago
        payment_id = self.request.GET.get('payment_id')
        status = self.request.GET.get('status')
        
        if payment_id:
            payment_info = mercado_pago_service.get_payment_info(payment_id)
            
            if payment_info['success']:
                context['payment'] = payment_info['payment']
                context['payment_id'] = payment_id
                context['status'] = status
        
        return context


class PaymentErrorView(TemplateView):
    """Página de erro no pagamento"""
    template_name = 'core/payment_error.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Parâmetros do Mercado Pago
        payment_id = self.request.GET.get('payment_id')
        status = self.request.GET.get('status')
        
        context['payment_id'] = payment_id
        context['status'] = status
        
        return context


class PaymentPendingView(TemplateView):
    """Página de pagamento pendente"""
    template_name = 'core/payment_pending.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Parâmetros do Mercado Pago
        payment_id = self.request.GET.get('payment_id')
        status = self.request.GET.get('status')
        
        context['payment_id'] = payment_id
        context['status'] = status
        
        return context