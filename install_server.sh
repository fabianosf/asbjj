#!/bin/bash
set -e

echo "🔧 Configurando servidor..."

# Atualizar sistema
echo "📦 Atualizando sistema..."
sudo apt update
sudo apt upgrade -y

# Instalar dependências
echo "📦 Instalando dependências..."
sudo apt install -y python3-pip python3-venv python3-dev \
    postgresql postgresql-contrib \
    redis-server \
    nginx \
    git \
    supervisor \
    certbot python3-certbot-nginx

# Configurar PostgreSQL
echo "🗄️ Configurando PostgreSQL..."
sudo -u postgres psql << EOF
CREATE DATABASE asbjj_db;
CREATE USER asbjj_user WITH PASSWORD 'CHANGE_THIS_PASSWORD';
ALTER ROLE asbjj_user SET client_encoding TO 'utf8';
ALTER ROLE asbjj_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE asbjj_user SET timezone TO 'America/Sao_Paulo';
GRANT ALL PRIVILEGES ON DATABASE asbjj_db TO asbjj_user;
\q
EOF

# Criar diretório do projeto
echo "📁 Criando estrutura de diretórios..."
sudo mkdir -p /var/www/asbjj
sudo chown $USER:$USER /var/www/asbjj
cd /var/www/asbjj

# Clonar repositório
echo "📥 Clonando repositório..."
git clone https://github.com/fabianosf/asbjj.git .

# Criar ambiente virtual
echo "🐍 Criando ambiente virtual..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependências Python
echo "📦 Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Copiar .env de produção
echo "⚙️ Configurando variáveis de ambiente..."
cp .env.production .env

# Coletar arquivos estáticos
echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Criar diretórios
mkdir -p media/shop/products
mkdir -p staticfiles
mkdir -p logs

# Executar migrações
echo "🗄️ Executando migrações..."
python manage.py migrate

# Criar superusuário
echo "👤 Criando superusuário..."
python manage.py shell << PYEOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@asbjj.com.br', 'admin123')
    print('Superusuário criado: admin/admin123')
PYEOF

# Popular dados iniciais
echo "📊 Populando dados iniciais..."
python manage.py populate_shop || true

echo "✅ Instalação concluída!"
