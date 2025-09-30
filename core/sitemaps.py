from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Product, ProductCategory, BlogPost, Gallery


class StaticViewSitemap(Sitemap):
    """Sitemap para páginas estáticas"""
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return [
            'core:index',
            'core:about',
            'core:services',
            'core:contact',
            'core:gallery',
            'core:shop',
            'core:enrollment',
            'core:calendar',
        ]

    def location(self, item):
        return reverse(item)

    def lastmod(self, item):
        # Para páginas estáticas, usar data de modificação do projeto
        from datetime import datetime
        return datetime.now()


class ProductSitemap(Sitemap):
    """Sitemap para produtos"""
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Product.objects.filter(status='published')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class ProductCategorySitemap(Sitemap):
    """Sitemap para categorias de produtos"""
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return ProductCategory.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class BlogPostSitemap(Sitemap):
    """Sitemap para posts do blog"""
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return BlogPost.objects.filter(status='published')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class GallerySitemap(Sitemap):
    """Sitemap para galeria"""
    changefreq = 'monthly'
    priority = 0.4

    def items(self):
        return Gallery.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()