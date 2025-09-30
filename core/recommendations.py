"""
Sistema de recomendações de produtos
"""
from django.db.models import Count, Q, F
from .models import Product, ProductCategory, OrderItem, CartItem


class RecommendationEngine:
    """Motor de recomendações"""
    
    @staticmethod
    def get_popular_products(limit=8):
        """Produtos mais populares baseado em vendas"""
        return Product.objects.filter(
            status='published'
        ).annotate(
            total_sold=Count('orderitem')
        ).order_by('-total_sold', '-created_at')[:limit]
    
    @staticmethod
    def get_recent_products(limit=8):
        """Produtos mais recentes"""
        return Product.objects.filter(
            status='published'
        ).order_by('-created_at')[:limit]
    
    @staticmethod
    def get_related_products(product, limit=4):
        """Produtos relacionados baseado na categoria"""
        return Product.objects.filter(
            category=product.category,
            status='published'
        ).exclude(id=product.id).order_by('-created_at')[:limit]
    
    @staticmethod
    def get_frequently_bought_together(product, limit=4):
        """Produtos frequentemente comprados juntos"""
        # Buscar pedidos que contêm este produto
        orders_with_product = OrderItem.objects.filter(
            product=product
        ).values_list('order_id', flat=True)
        
        # Buscar outros produtos nesses pedidos
        related_products = OrderItem.objects.filter(
            order_id__in=orders_with_product
        ).exclude(
            product=product
        ).values('product').annotate(
            frequency=Count('product')
        ).order_by('-frequency')[:limit]
        
        product_ids = [item['product'] for item in related_products]
        return Product.objects.filter(
            id__in=product_ids,
            status='published'
        )
    
    @staticmethod
    def get_category_recommendations(category, limit=6):
        """Recomendações por categoria"""
        return Product.objects.filter(
            category=category,
            status='published'
        ).order_by('-created_at')[:limit]
    
    @staticmethod
    def get_price_range_products(min_price, max_price, limit=6):
        """Produtos em uma faixa de preço"""
        return Product.objects.filter(
            price__gte=min_price,
            price__lte=max_price,
            status='published'
        ).order_by('-created_at')[:limit]
    
    @staticmethod
    def get_cart_recommendations(cart_items, limit=4):
        """Recomendações baseadas no carrinho"""
        if not cart_items.exists():
            return Product.objects.filter(
                status='published'
            ).order_by('-created_at')[:limit]
        
        # Buscar produtos de categorias similares
        categories = cart_items.values_list('product__category', flat=True)
        
        return Product.objects.filter(
            category__in=categories,
            status='published'
        ).exclude(
            id__in=cart_items.values_list('product_id', flat=True)
        ).order_by('-created_at')[:limit]
    
    @staticmethod
    def get_seasonal_recommendations(limit=6):
        """Recomendações sazonais"""
        from datetime import datetime
        
        current_month = datetime.now().month
        
        # Lógica sazonal simples
        if current_month in [12, 1, 2]:  # Verão
            seasonal_categories = ['camisetas', 'shorts', 'bonés']
        elif current_month in [3, 4, 5]:  # Outono
            seasonal_categories = ['camisetas', 'kimonos']
        elif current_month in [6, 7, 8]:  # Inverno
            seasonal_categories = ['kimonos', 'mochilas']
        else:  # Primavera
            seasonal_categories = ['kimonos', 'camisetas', 'acessórios']
        
        return Product.objects.filter(
            category__slug__in=seasonal_categories,
            status='published'
        ).order_by('-created_at')[:limit]
    
    @staticmethod
    def get_trending_products(limit=6):
        """Produtos em tendência (baseado em vendas recentes)"""
        from datetime import datetime, timedelta
        
        # Últimos 30 dias
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        return Product.objects.filter(
            orderitem__order__created_at__gte=thirty_days_ago,
            status='published'
        ).annotate(
            recent_sales=Count('orderitem')
        ).order_by('-recent_sales', '-created_at')[:limit]
    
    @staticmethod
    def get_personalized_recommendations(email, limit=6):
        """Recomendações personalizadas baseadas no histórico"""
        if not email:
            return Product.objects.filter(
                status='published'
            ).order_by('-created_at')[:limit]
        
        # Buscar histórico de compras do cliente
        customer_orders = OrderItem.objects.filter(
            order__customer_email=email
        ).values_list('product_id', flat=True)
        
        if not customer_orders:
            return Product.objects.filter(
                status='published'
            ).order_by('-created_at')[:limit]
        
        # Buscar categorias preferidas
        preferred_categories = Product.objects.filter(
            id__in=customer_orders
        ).values_list('category', flat=True)
        
        # Recomendar produtos de categorias similares
        return Product.objects.filter(
            category__in=preferred_categories,
            status='published'
        ).exclude(
            id__in=customer_orders
        ).order_by('-created_at')[:limit]


# Instância global do motor de recomendações
recommendation_engine = RecommendationEngine()
