from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from core.models import ProductCategory, Product
import os


class Command(BaseCommand):
    help = 'Popula a loja com dados de exemplo'

    def handle(self, *args, **options):
        self.stdout.write('Criando categorias...')
        
        # Criar categorias
        categories_data = [
            {
                'name': 'Kimonos',
                'slug': 'kimonos',
                'description': 'Kimonos oficiais da academia ASBJJ',
                'order': 1
            },
            {
                'name': 'Camisetas',
                'slug': 'camisetas',
                'description': 'Camisetas e roupas casuais',
                'order': 2
            },
            {
                'name': 'Acessórios',
                'slug': 'acessorios',
                'description': 'Acessórios para treino e competição',
                'order': 3
            },
            {
                'name': 'Equipamentos',
                'slug': 'equipamentos',
                'description': 'Equipamentos de treino',
                'order': 4
            }
        ]
        
        for cat_data in categories_data:
            category, created = ProductCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'Categoria criada: {category.name}')
            else:
                self.stdout.write(f'Categoria já existe: {category.name}')
        
        self.stdout.write('Criando produtos...')
        
        # Produtos de exemplo
        products_data = [
            {
                'name': 'Kimono ASBJJ Oficial',
                'slug': 'kimono-asbjj-oficial',
                'description': 'Kimono oficial da academia ASBJJ, confeccionado em algodão premium com patches bordados. Ideal para treinos e competições.',
                'short_description': 'Kimono oficial premium com patches bordados',
                'category_slug': 'kimonos',
                'price': 399.00,
                'compare_price': 499.00,
                'stock_quantity': 15,
                'colors': ['Branco', 'Azul', 'Preto'],
                'sizes': ['A0', 'A1', 'A2', 'A3', 'A4', 'A5'],
                'is_featured': True,
                'is_bestseller': True
            },
            {
                'name': 'Camiseta ASBJJ',
                'slug': 'camiseta-asbjj',
                'description': 'Camiseta 100% algodão com logo da academia. Confortável e durável para uso no dia a dia.',
                'short_description': 'Camiseta 100% algodão com logo da academia',
                'category_slug': 'camisetas',
                'price': 69.90,
                'stock_quantity': 50,
                'colors': ['Branco', 'Preto', 'Azul', 'Vermelho'],
                'sizes': ['P', 'M', 'G', 'GG'],
                'is_featured': True
            },
            {
                'name': 'Mochila ASBJJ',
                'slug': 'mochila-asbjj',
                'description': 'Mochila resistente com compartimento especial para kimono. Ideal para levar seus equipamentos para o treino.',
                'short_description': 'Mochila com compartimento para kimono',
                'category_slug': 'acessorios',
                'price': 149.00,
                'stock_quantity': 20,
                'colors': ['Preto', 'Azul'],
                'sizes': ['Único']
            },
            {
                'name': 'Faixa Branca',
                'slug': 'faixa-branca',
                'description': 'Faixa oficial de Jiu-Jitsu, confeccionada em algodão de alta qualidade.',
                'short_description': 'Faixa oficial de Jiu-Jitsu',
                'category_slug': 'acessorios',
                'price': 25.00,
                'stock_quantity': 100,
                'colors': ['Branco'],
                'sizes': ['A1', 'A2', 'A3', 'A4', 'A5']
            },
            {
                'name': 'Protetor Bucal',
                'slug': 'protetor-bucal',
                'description': 'Protetor bucal moldável para treinos e competições. Protege seus dentes durante o combate.',
                'short_description': 'Protetor bucal moldável',
                'category_slug': 'equipamentos',
                'price': 35.00,
                'stock_quantity': 30,
                'colors': ['Transparente', 'Azul', 'Rosa'],
                'sizes': ['Único']
            },
            {
                'name': 'Caneleira ASBJJ',
                'slug': 'caneleira-asbjj',
                'description': 'Caneleira de proteção para treinos de chute. Confortável e segura.',
                'short_description': 'Caneleira de proteção para treinos',
                'category_slug': 'equipamentos',
                'price': 89.90,
                'stock_quantity': 25,
                'colors': ['Preto', 'Azul'],
                'sizes': ['P', 'M', 'G']
            },
            {
                'name': 'Boné ASBJJ',
                'slug': 'bone-asbjj',
                'description': 'Boné com logo da academia. Ideal para uso no dia a dia e eventos.',
                'short_description': 'Boné com logo da academia',
                'category_slug': 'acessorios',
                'price': 45.00,
                'stock_quantity': 40,
                'colors': ['Preto', 'Azul', 'Branco'],
                'sizes': ['Único']
            },
            {
                'name': 'Kimono de Treino',
                'slug': 'kimono-treino',
                'description': 'Kimono básico para treinos diários. Confortável e resistente.',
                'short_description': 'Kimono básico para treinos diários',
                'category_slug': 'kimonos',
                'price': 299.00,
                'stock_quantity': 20,
                'colors': ['Branco', 'Azul'],
                'sizes': ['A0', 'A1', 'A2', 'A3', 'A4', 'A5']
            }
        ]
        
        for prod_data in products_data:
            category = ProductCategory.objects.get(slug=prod_data.pop('category_slug'))
            
            # Criar uma imagem placeholder simples
            from PIL import Image
            import io
            
            # Criar uma imagem simples
            img = Image.new('RGB', (400, 400), color='#f0f0f0')
            img_io = io.BytesIO()
            img.save(img_io, format='JPEG')
            img_content = ContentFile(img_io.getvalue(), name=f"{prod_data['slug']}.jpg")
            
            product, created = Product.objects.get_or_create(
                slug=prod_data['slug'],
                defaults={
                    **prod_data,
                    'category': category,
                    'status': 'published',
                    'main_image': img_content
                }
            )
            
            if created:
                self.stdout.write(f'Produto criado: {product.name}')
            else:
                self.stdout.write(f'Produto já existe: {product.name}')
        
        self.stdout.write(
            self.style.SUCCESS('Loja populada com sucesso!')
        )
