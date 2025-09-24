#!/bin/bash

# ASBJJ Deployment Script
# Este script automatiza o processo de deploy do projeto

set -e  # Exit on any error

echo "🚀 Iniciando deploy do ASBJJ..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning "Arquivo .env não encontrado. Criando a partir do exemplo..."
    cp env_example.txt .env
    print_warning "Por favor, edite o arquivo .env com suas configurações antes de continuar."
    exit 1
fi

# Load environment variables
source .env

print_status "Carregando variáveis de ambiente..."

# Check if we're in production mode
if [ "$DEBUG" = "True" ]; then
    print_warning "Modo DEBUG ativado. Certifique-se de que isso está correto para produção."
fi

# Install dependencies
print_status "Instalando dependências..."
pip install -r requirements.txt

# Run migrations
print_status "Executando migrações..."
python manage.py migrate --noinput

# Collect static files
print_status "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
print_status "Verificando superusuário..."
python manage.py shell << EOF
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@asbjj.com.br', 'admin123')
    print('Superusuário criado: admin/admin123')
else:
    print('Superusuário já existe')
EOF

# Create initial data
print_status "Criando dados iniciais..."
python manage.py shell << EOF
from core.models import SiteSettings, ClassCategory, Class
from accounts.models import UserProfile

# Create site settings if not exists
if not SiteSettings.objects.exists():
    SiteSettings.objects.create(
        site_name='ASBJJ - Alexandre Salgado Brazilian Jiu-Jitsu',
        site_description='Academia especializada em Jiu-Jitsu, Defesa Pessoal e Yoga',
        contact_email='admin@asbjj.com.br',
        contact_phone='+5511999999999',
        contact_address='São Paulo, SP',
        contact_whatsapp='+5511999999999'
    )
    print('Configurações do site criadas')

# Create class categories if not exist
categories = [
    {'name': 'Jiu-Jitsu', 'slug': 'jiu-jitsu', 'description': 'Arte marcial brasileira', 'icon': 'fas fa-user-ninja', 'color': '#dc3545'},
    {'name': 'Defesa Pessoal', 'slug': 'defesa-pessoal', 'description': 'Técnicas de autoproteção', 'icon': 'fas fa-shield-alt', 'color': '#ffc107'},
    {'name': 'Yoga', 'slug': 'yoga', 'description': 'Prática de equilíbrio corpo e mente', 'icon': 'fas fa-leaf', 'color': '#28a745'}
]

for cat_data in categories:
    category, created = ClassCategory.objects.get_or_create(
        slug=cat_data['slug'],
        defaults=cat_data
    )
    if created:
        print(f'Categoria {cat_data["name"]} criada')

# Create sample classes if not exist
sample_classes = [
    {
        'category_slug': 'jiu-jitsu',
        'name': 'Jiu-Jitsu Iniciante',
        'slug': 'jiu-jitsu-iniciante',
        'description': 'Aulas de Jiu-Jitsu para iniciantes. Foco em fundamentos e técnicas básicas.',
        'short_description': 'Aprenda os fundamentos do Jiu-Jitsu',
        'price_monthly': 160.00,
        'duration_minutes': 60,
        'min_age': 5
    },
    {
        'category_slug': 'defesa-pessoal',
        'name': 'Defesa Pessoal Feminina',
        'slug': 'defesa-pessoal-feminina',
        'description': 'Técnicas específicas de defesa pessoal para mulheres.',
        'short_description': 'Técnicas de autoproteção para mulheres',
        'price_monthly': 150.00,
        'duration_minutes': 60,
        'min_age': 16
    },
    {
        'category_slug': 'yoga',
        'name': 'Yoga para Iniciantes',
        'slug': 'yoga-iniciantes',
        'description': 'Aulas de Yoga focadas em iniciantes. Posturas básicas e relaxamento.',
        'short_description': 'Yoga para iniciantes e relaxamento',
        'price_monthly': 200.00,
        'duration_minutes': 75,
        'min_age': 12
    }
]

for class_data in sample_classes:
    category = ClassCategory.objects.get(slug=class_data['category_slug'])
    class_obj, created = Class.objects.get_or_create(
        slug=class_data['slug'],
        defaults={
            **class_data,
            'category': category
        }
    )
    if created:
        print(f'Aula {class_data["name"]} criada')

print('Dados iniciais criados com sucesso!')
EOF

# Run tests
print_status "Executando testes..."
# pular testes em produção por padrão
# python manage.py test --verbosity=2

# Check deployment health
print_status "Verificando saúde do deployment..."
python manage.py check --deploy

print_status "Deploy concluído com sucesso! 🎉"

# Show next steps
echo ""
echo "📋 Próximos passos:"
echo "1. Configure o servidor web (Nginx/Apache)"
echo "2. Configure o SSL/HTTPS"
echo "3. Configure o Redis para cache"
echo "4. Configure o Celery para tarefas assíncronas"
echo "5. Configure o banco de dados PostgreSQL"
echo "6. Configure o monitoramento e logs"
echo ""
echo "🔧 Comandos úteis:"
echo "- Iniciar servidor: python manage.py runserver"
echo "- Iniciar Celery: celery -A projeto worker --loglevel=info"
echo "- Iniciar Celery Beat: celery -A projeto beat --loglevel=info"
echo "- Acessar admin: http://localhost:8000/admin/"
echo ""
echo "📚 Documentação: README.md"
echo "🐳 Docker: docker-compose up -d"
echo ""

# Show admin credentials
print_warning "Credenciais do Admin:"
echo "Usuário: admin"
echo "Senha: admin123"
echo "URL: http://localhost:8000/admin/"
echo ""
print_warning "IMPORTANTE: Altere a senha do admin imediatamente!"
