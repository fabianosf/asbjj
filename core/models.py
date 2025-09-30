from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
import uuid


class SiteSettings(models.Model):
    """Configurações gerais do site"""
    site_name = models.CharField('Nome do Site', max_length=200, default='ASBJJ')
    site_description = models.TextField('Descrição do Site', blank=True)
    site_logo = models.ImageField('Logo', upload_to='site/images/', blank=True, null=True)
    site_favicon = models.ImageField('Favicon', upload_to='site/images/', blank=True, null=True)
    
    # Informações de contato
    contact_email = models.EmailField('E-mail de Contato')
    contact_phone = models.CharField(
        'Telefone de Contato',
        max_length=20,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Formato de telefone inválido."
        )]
    )
    contact_address = models.TextField('Endereço', blank=True)
    contact_whatsapp = models.CharField('WhatsApp', max_length=20, blank=True)
    
    # Redes sociais
    instagram_url = models.URLField('Instagram', blank=True)
    facebook_url = models.URLField('Facebook', blank=True)
    youtube_url = models.URLField('YouTube', blank=True)
    tiktok_url = models.URLField('TikTok', blank=True)
    google_maps_url = models.URLField('Google Maps (embed/view URL)', blank=True)
    
    # SEO
    meta_title = models.CharField('Meta Title', max_length=200, blank=True)
    meta_description = models.TextField('Meta Description', blank=True)
    meta_keywords = models.TextField('Meta Keywords', blank=True)
    google_analytics_id = models.CharField('Google Analytics ID', max_length=20, blank=True)
    tawkto_property_id = models.CharField('Tawk.to Property ID', max_length=100, blank=True)
    
    # Configurações
    is_maintenance_mode = models.BooleanField('Modo Manutenção', default=False)
    maintenance_message = models.TextField('Mensagem de Manutenção', blank=True)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Configuração do Site'
        verbose_name_plural = 'Configurações do Site'

    def __str__(self):
        return f"Configurações - {self.site_name}"

    def save(self, *args, **kwargs):
        # Garantir que apenas uma instância exista
        if not self.pk and SiteSettings.objects.exists():
            raise ValueError('Apenas uma instância de SiteSettings é permitida')
        super().save(*args, **kwargs)


class ContactMessage(models.Model):
    """Mensagens de contato recebidas"""
    STATUS_CHOICES = [
        ('new', 'Nova'),
        ('read', 'Lida'),
        ('replied', 'Respondida'),
        ('archived', 'Arquivada'),
    ]

    # Informações do remetente
    name = models.CharField('Nome', max_length=200)
    email = models.EmailField('E-mail')
    phone = models.CharField('Telefone', max_length=20, blank=True)
    
    # Conteúdo da mensagem
    subject = models.CharField('Assunto', max_length=300, blank=True)
    message = models.TextField('Mensagem')
    
    # Categoria e prioridade
    category = models.CharField(
        'Categoria',
        max_length=50,
        choices=[
            ('general', 'Geral'),
            ('classes', 'Aulas'),
            ('schedule', 'Horários'),
            ('pricing', 'Preços'),
            ('complaint', 'Reclamação'),
            ('suggestion', 'Sugestão'),
        ],
        default='general'
    )
    priority = models.CharField(
        'Prioridade',
        max_length=20,
        choices=[
            ('low', 'Baixa'),
            ('normal', 'Normal'),
            ('high', 'Alta'),
            ('urgent', 'Urgente'),
        ],
        default='normal'
    )
    
    # Status e resposta
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='new')
    response = models.TextField('Resposta', blank=True)
    responded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contact_responses',
        verbose_name='Respondido por'
    )
    responded_at = models.DateTimeField('Respondido em', null=True, blank=True)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    ip_address = models.GenericIPAddressField('Endereço IP', null=True, blank=True)
    user_agent = models.TextField('User Agent', blank=True)
    whatsapp_url = models.TextField('URL WhatsApp', blank=True, help_text='URL para enviar a mensagem via WhatsApp')

    class Meta:
        verbose_name = 'Mensagem de Contato'
        verbose_name_plural = 'Mensagens de Contato'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject or 'Sem assunto'}"


class Instructor(models.Model):
    """Instrutores da academia"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='instructor_profile',
        verbose_name='Usuário'
    )
    
    # Informações profissionais
    bio = models.TextField('Biografia', blank=True)
    experience_years = models.PositiveIntegerField('Anos de Experiência', default=0)
    certifications = models.JSONField('Certificações', default=list, blank=True)
    specializations = models.JSONField('Especializações', default=list, blank=True)
    
    # Foto e mídia
    photo = models.ImageField('Foto', upload_to='instructors/photos/', blank=True, null=True)
    social_links = models.JSONField('Links Sociais', default=dict, blank=True)
    
    # Status
    is_active = models.BooleanField('Ativo', default=True)
    is_featured = models.BooleanField('Destaque', default=False)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Instrutor'
        verbose_name_plural = 'Instrutores'
        ordering = ['user__first_name', 'user__last_name']

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username


class Gallery(models.Model):
    """Galeria de imagens do site"""
    title = models.CharField('Título', max_length=200)
    description = models.TextField('Descrição', blank=True)
    image = models.ImageField('Imagem', upload_to='gallery/images/')
    category = models.CharField(
        'Categoria',
        max_length=50,
        choices=[
            ('academy', 'Academia'),
            ('classes', 'Aulas'),
            ('events', 'Eventos'),
            ('graduations', 'Graduações'),
            ('competitions', 'Competições'),
            ('team', 'Equipe'),
        ],
        default='academy'
    )
    is_featured = models.BooleanField('Destaque', default=False)
    order = models.PositiveIntegerField('Ordem', default=0)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Imagem da Galeria'
        verbose_name_plural = 'Galeria de Imagens'
        ordering = ['category', 'order', '-created_at']

    def __str__(self):
        return self.title


class BlogPost(models.Model):
    """Posts do blog"""
    STATUS_CHOICES = [
        ('draft', 'Rascunho'),
        ('published', 'Publicado'),
        ('archived', 'Arquivado'),
    ]

    title = models.CharField('Título', max_length=300)
    slug = models.SlugField('Slug', unique=True)
    excerpt = models.TextField('Resumo', max_length=500)
    content = models.TextField('Conteúdo')
    
    # Imagens
    featured_image = models.ImageField('Imagem Destacada', upload_to='blog/images/', blank=True, null=True)
    
    # Autor e categoria
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blog_posts',
        verbose_name='Autor'
    )
    category = models.CharField(
        'Categoria',
        max_length=50,
        choices=[
            ('news', 'Notícias'),
            ('tips', 'Dicas'),
            ('techniques', 'Técnicas'),
            ('events', 'Eventos'),
            ('nutrition', 'Nutrição'),
            ('health', 'Saúde'),
        ],
        default='news'
    )
    
    # SEO
    meta_title = models.CharField('Meta Title', max_length=300, blank=True)
    meta_description = models.TextField('Meta Description', blank=True)
    
    # Status e visibilidade
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField('Destaque', default=False)
    allow_comments = models.BooleanField('Permitir Comentários', default=True)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    published_at = models.DateTimeField('Publicado em', null=True, blank=True)
    view_count = models.PositiveIntegerField('Visualizações', default=0)

    class Meta:
        verbose_name = 'Post do Blog'
        verbose_name_plural = 'Posts do Blog'
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('core:blog_detail', kwargs={'slug': self.slug})


class ProductCategory(models.Model):
    """Categorias de produtos"""
    name = models.CharField('Nome', max_length=100)
    slug = models.SlugField('Slug', unique=True)
    description = models.TextField('Descrição', blank=True)
    image = models.ImageField('Imagem', upload_to='shop/categories/', blank=True, null=True)
    is_active = models.BooleanField('Ativo', default=True)
    order = models.PositiveIntegerField('Ordem', default=0)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Categoria de Produto'
        verbose_name_plural = 'Categorias de Produtos'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('core:shop_category', kwargs={'slug': self.slug})


class Product(models.Model):
    """Produtos da loja"""
    STATUS_CHOICES = [
        ('draft', 'Rascunho'),
        ('published', 'Publicado'),
        ('out_of_stock', 'Esgotado'),
        ('discontinued', 'Descontinuado'),
    ]

    # Informações básicas
    name = models.CharField('Nome', max_length=200)
    slug = models.SlugField('Slug', unique=True)
    description = models.TextField('Descrição')
    short_description = models.CharField('Descrição Curta', max_length=300, blank=True)
    
    # Categoria e status
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Categoria'
    )
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Preços
    price = models.DecimalField('Preço', max_digits=10, decimal_places=2)
    compare_price = models.DecimalField('Preço de Comparação', max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Estoque
    stock_quantity = models.PositiveIntegerField('Quantidade em Estoque', default=0)
    track_stock = models.BooleanField('Controlar Estoque', default=True)
    
    # Imagens
    main_image = models.ImageField('Imagem Principal', upload_to='shop/products/')
    images = models.JSONField('Imagens Adicionais', default=list, blank=True)
    
    # Atributos
    weight = models.DecimalField('Peso (kg)', max_digits=8, decimal_places=3, null=True, blank=True)
    dimensions = models.CharField('Dimensões (LxAxP cm)', max_length=50, blank=True)
    colors = models.JSONField('Cores Disponíveis', default=list, blank=True)
    sizes = models.JSONField('Tamanhos Disponíveis', default=list, blank=True)
    
    # SEO
    meta_title = models.CharField('Meta Title', max_length=200, blank=True)
    meta_description = models.TextField('Meta Description', blank=True)
    
    # Destaque e ordenação
    is_featured = models.BooleanField('Destaque', default=False)
    is_bestseller = models.BooleanField('Mais Vendido', default=False)
    order = models.PositiveIntegerField('Ordem', default=0)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    view_count = models.PositiveIntegerField('Visualizações', default=0)

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('core:product_detail', kwargs={'slug': self.slug})

    @property
    def is_available(self):
        """Verifica se o produto está disponível para venda"""
        if self.status != 'published':
            return False
        if self.track_stock and self.stock_quantity <= 0:
            return False
        return True

    @property
    def discount_percentage(self):
        """Calcula a porcentagem de desconto"""
        if self.compare_price and self.compare_price > self.price:
            return int(((self.compare_price - self.price) / self.compare_price) * 100)
        return 0

    @property
    def main_image_url(self):
        """Retorna a URL da imagem principal"""
        if self.main_image:
            return self.main_image.url
        return '/static/img/no-image.png'


class ProductReview(models.Model):
    """Avaliações de produtos"""
    RATING_CHOICES = [
        (1, '1 Estrela'),
        (2, '2 Estrelas'),
        (3, '3 Estrelas'),
        (4, '4 Estrelas'),
        (5, '5 Estrelas'),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Produto'
    )
    name = models.CharField('Nome', max_length=100)
    email = models.EmailField('E-mail')
    rating = models.PositiveIntegerField('Avaliação', choices=RATING_CHOICES)
    title = models.CharField('Título', max_length=200)
    comment = models.TextField('Comentário')
    is_approved = models.BooleanField('Aprovado', default=False)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Avaliação de Produto'
        verbose_name_plural = 'Avaliações de Produtos'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.product.name} ({self.rating} estrelas)"


class Cart(models.Model):
    """Carrinho de compras"""
    session_key = models.CharField('Chave da Sessão', max_length=40, unique=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Carrinho'
        verbose_name_plural = 'Carrinhos'
        ordering = ['-updated_at']

    def __str__(self):
        return f"Carrinho - {self.session_key}"

    @property
    def total_items(self):
        """Total de itens no carrinho"""
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        """Preço total do carrinho"""
        return sum(item.total_price for item in self.items.all())

    def add_item(self, product, quantity=1):
        """Adiciona item ao carrinho"""
        cart_item, created = CartItem.objects.get_or_create(
            cart=self,
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        return cart_item

    def remove_item(self, product):
        """Remove item do carrinho"""
        try:
            cart_item = self.items.get(product=product)
            cart_item.delete()
        except CartItem.DoesNotExist:
            pass

    def clear(self):
        """Limpa o carrinho"""
        self.items.all().delete()


class CartItem(models.Model):
    """Item do carrinho"""
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Carrinho'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Produto'
    )
    quantity = models.PositiveIntegerField('Quantidade', default=1)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Item do Carrinho'
        verbose_name_plural = 'Itens do Carrinho'
        unique_together = ['cart', 'product']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

    @property
    def total_price(self):
        """Preço total do item"""
        return self.product.price * self.quantity


class Order(models.Model):
    """Pedido"""
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('confirmed', 'Confirmado'),
        ('processing', 'Processando'),
        ('shipped', 'Enviado'),
        ('delivered', 'Entregue'),
        ('cancelled', 'Cancelado'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('paid', 'Pago'),
        ('failed', 'Falhou'),
        ('refunded', 'Reembolsado'),
    ]

    # Informações do pedido
    order_number = models.CharField('Número do Pedido', max_length=20, unique=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField('Status do Pagamento', max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Informações do cliente
    customer_name = models.CharField('Nome do Cliente', max_length=200)
    customer_email = models.EmailField('E-mail do Cliente')
    customer_phone = models.CharField('Telefone do Cliente', max_length=20)
    
    # Endereço de entrega
    shipping_address = models.TextField('Endereço de Entrega')
    shipping_city = models.CharField('Cidade', max_length=100)
    shipping_state = models.CharField('Estado', max_length=2)
    shipping_zip_code = models.CharField('CEP', max_length=10)
    
    # Valores
    subtotal = models.DecimalField('Subtotal', max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField('Custo de Envio', max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField('Total', max_digits=10, decimal_places=2)
    
    # Informações de pagamento
    payment_method = models.CharField('Método de Pagamento', max_length=50, blank=True)
    payment_reference = models.CharField('Referência do Pagamento', max_length=100, blank=True)
    
    # Observações
    notes = models.TextField('Observações', blank=True)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-created_at']

    def __str__(self):
        return f"Pedido {self.order_number} - {self.customer_name}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    def generate_order_number(self):
        """Gera número único do pedido"""
        import random
        import string
        from datetime import datetime
        
        # Formato: ASBJJ-YYYYMMDD-XXXX
        date_str = datetime.now().strftime('%Y%m%d')
        random_str = ''.join(random.choices(string.digits, k=4))
        return f"ASBJJ-{date_str}-{random_str}"

    @property
    def total_items(self):
        """Total de itens no pedido"""
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    """Item do pedido"""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Pedido'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Produto'
    )
    quantity = models.PositiveIntegerField('Quantidade')
    price = models.DecimalField('Preço Unitário', max_digits=10, decimal_places=2)
    total_price = models.DecimalField('Preço Total', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'
        ordering = ['-id']

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

    def save(self, *args, **kwargs):
        self.total_price = self.price * self.quantity
        super().save(*args, **kwargs)


class Coupon(models.Model):
    """Cupons de desconto"""
    code = models.CharField('Código', max_length=20, unique=True)
    description = models.TextField('Descrição', blank=True)
    discount_type = models.CharField('Tipo de Desconto', max_length=10, choices=[
        ('percentage', 'Porcentagem'),
        ('fixed', 'Valor Fixo'),
    ], default='percentage')
    discount_value = models.DecimalField('Valor do Desconto', max_digits=10, decimal_places=2)
    minimum_amount = models.DecimalField('Valor Mínimo', max_digits=10, decimal_places=2, default=0)
    maximum_discount = models.DecimalField('Desconto Máximo', max_digits=10, decimal_places=2, null=True, blank=True)
    usage_limit = models.PositiveIntegerField('Limite de Uso', null=True, blank=True)
    used_count = models.PositiveIntegerField('Vezes Usado', default=0)
    is_active = models.BooleanField('Ativo', default=True)
    valid_from = models.DateTimeField('Válido de')
    valid_until = models.DateTimeField('Válido até')
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Cupom'
        verbose_name_plural = 'Cupons'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.discount_value}%"

    def is_valid(self):
        """Verifica se o cupom é válido"""
        from django.utils import timezone
        now = timezone.now()
        
        if not self.is_active:
            return False
        
        if now < self.valid_from or now > self.valid_until:
            return False
        
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False
        
        return True

    def calculate_discount(self, cart_total):
        """Calcula o desconto para um valor do carrinho"""
        if not self.is_valid() or cart_total < self.minimum_amount:
            return 0
        
        if self.discount_type == 'percentage':
            discount = (cart_total * self.discount_value) / 100
            if self.maximum_discount:
                discount = min(discount, self.maximum_discount)
        else:  # fixed
            discount = self.discount_value
        
        return min(discount, cart_total)


class Wishlist(models.Model):
    """Lista de desejos"""
    session_key = models.CharField('Chave da Sessão', max_length=40, unique=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Lista de Desejos'
        verbose_name_plural = 'Listas de Desejos'
        ordering = ['-updated_at']

    def __str__(self):
        return f"Lista de Desejos - {self.session_key}"

    @property
    def total_items(self):
        return self.items.count()

    def add_item(self, product):
        """Adiciona produto à lista de desejos"""
        wishlist_item, created = WishlistItem.objects.get_or_create(
            wishlist=self,
            product=product
        )
        return wishlist_item

    def remove_item(self, product):
        """Remove produto da lista de desejos"""
        try:
            wishlist_item = self.items.get(product=product)
            wishlist_item.delete()
        except WishlistItem.DoesNotExist:
            pass

    def clear(self):
        """Limpa a lista de desejos"""
        self.items.all().delete()


class WishlistItem(models.Model):
    """Item da lista de desejos"""
    wishlist = models.ForeignKey(
        Wishlist,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Lista de Desejos'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Produto'
    )
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Item da Lista de Desejos'
        verbose_name_plural = 'Itens da Lista de Desejos'
        unique_together = ['wishlist', 'product']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} - {self.wishlist.session_key}"


class LoyaltyProgram(models.Model):
    """Programa de fidelidade"""
    name = models.CharField('Nome', max_length=100)
    description = models.TextField('Descrição', blank=True)
    points_per_real = models.DecimalField('Pontos por Real', max_digits=5, decimal_places=2, default=1.00)
    points_for_signup = models.PositiveIntegerField('Pontos por Cadastro', default=100)
    points_for_review = models.PositiveIntegerField('Pontos por Avaliação', default=50)
    is_active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Programa de Fidelidade'
        verbose_name_plural = 'Programas de Fidelidade'

    def __str__(self):
        return self.name


class CustomerLoyalty(models.Model):
    """Fidelidade do cliente"""
    email = models.EmailField('E-mail', unique=True)
    total_points = models.PositiveIntegerField('Total de Pontos', default=0)
    used_points = models.PositiveIntegerField('Pontos Usados', default=0)
    level = models.CharField('Nível', max_length=20, choices=[
        ('bronze', 'Bronze'),
        ('silver', 'Prata'),
        ('gold', 'Ouro'),
        ('platinum', 'Platina'),
    ], default='bronze')
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Fidelidade do Cliente'
        verbose_name_plural = 'Fidelidades dos Clientes'
        ordering = ['-total_points']

    def __str__(self):
        return f"{self.email} - {self.get_level_display()}"

    @property
    def available_points(self):
        """Pontos disponíveis para uso"""
        return self.total_points - self.used_points

    def add_points(self, points, reason=''):
        """Adiciona pontos ao cliente"""
        self.total_points += points
        self.update_level()
        self.save()
        
        # Registrar histórico
        LoyaltyHistory.objects.create(
            customer=self,
            points=points,
            reason=reason,
            type='earned'
        )

    def use_points(self, points, reason=''):
        """Usa pontos do cliente"""
        if points <= self.available_points:
            self.used_points += points
            self.save()
            
            # Registrar histórico
            LoyaltyHistory.objects.create(
                customer=self,
                points=-points,
                reason=reason,
                type='used'
            )
            return True
        return False

    def update_level(self):
        """Atualiza o nível do cliente baseado nos pontos"""
        if self.total_points >= 10000:
            self.level = 'platinum'
        elif self.total_points >= 5000:
            self.level = 'gold'
        elif self.total_points >= 2000:
            self.level = 'silver'
        else:
            self.level = 'bronze'


class LoyaltyHistory(models.Model):
    """Histórico de pontos de fidelidade"""
    customer = models.ForeignKey(
        CustomerLoyalty,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name='Cliente'
    )
    points = models.IntegerField('Pontos')
    reason = models.CharField('Motivo', max_length=200, blank=True)
    type = models.CharField('Tipo', max_length=10, choices=[
        ('earned', 'Ganho'),
        ('used', 'Usado'),
        ('expired', 'Expirado'),
    ])
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Pedido'
    )
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Histórico de Fidelidade'
        verbose_name_plural = 'Históricos de Fidelidade'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer.email} - {self.points} pontos - {self.get_type_display()}"


class LoyaltyReward(models.Model):
    """Recompensas do programa de fidelidade"""
    name = models.CharField('Nome', max_length=100)
    description = models.TextField('Descrição')
    points_cost = models.PositiveIntegerField('Custo em Pontos')
    discount_percentage = models.DecimalField('Desconto (%)', max_digits=5, decimal_places=2, null=True, blank=True)
    discount_amount = models.DecimalField('Desconto (R$)', max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Recompensa'
        verbose_name_plural = 'Recompensas'
        ordering = ['points_cost']

    def __str__(self):
        return f"{self.name} - {self.points_cost} pontos"
