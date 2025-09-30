#!/bin/bash

# Script de Deploy para Produção - ASBJJ
# Servidor: 92.113.33.16
# Domínio: asbjj.com.br

set -e

echo "🚀 Iniciando deploy para produção..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configurações
SERVER_IP="92.113.33.16"
SERVER_USER="fabianosf"
DOMAIN="asbjj.com.br"
PROJECT_NAME="asbjj"
REPO_URL="https://github.com/fabianosf/asbjj.git"

echo -e "${GREEN}📦 Preparando arquivos para deploy...${NC}"

# Criar arquivo .env de produção
cat > .env.production << 'EOF'
# Django Settings
DEBUG=False
SECRET_KEY=CHANGE_THIS_TO_A_RANDOM_SECRET_KEY_IN_PRODUCTION
ALLOWED_HOSTS=asbjj.com.br,www.asbjj.com.br,92.113.33.16

# Database (PostgreSQL)
DATABASE_URL=postgresql://asbjj_user:CHANGE_DB_PASSWORD@localhost:5432/asbjj_db

# Redis
REDIS_URL=redis://localhost:6379/1

# Email
EMAIL_CONSOLE=False
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu_email@gmail.com
EMAIL_HOST_PASSWORD=sua_senha_de_app
DEFAULT_FROM_EMAIL=noreply@asbjj.com.br
ADMIN_EMAIL=admin@asbjj.com.br

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Site
SITE_URL=https://asbjj.com.br

# WhatsApp
ADMIN_WHATSAPP=5521989307826

# Admin
ADMIN_URL=admin-asbjj-secure/
EOF

echo -e "${GREEN}✅ Arquivo .env.production criado${NC}"

# Criar script de instalação no servidor
cat > install_server.sh << 'EOFSCRIPT'
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
EOFSCRIPT

chmod +x install_server.sh

# Criar configuração do Nginx
cat > nginx_asbjj.conf << 'EOF'
server {
    listen 80;
    server_name asbjj.com.br www.asbjj.com.br;
    
    client_max_body_size 10M;
    
    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
    }
    
    location /static/ {
        alias /var/www/asbjj/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /var/www/asbjj/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Criar configuração do Supervisor
cat > supervisor_asbjj.conf << 'EOF'
[program:asbjj]
command=/var/www/asbjj/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 projeto.wsgi:application
directory=/var/www/asbjj
user=fabianosf
autostart=true
autorestart=true
stderr_logfile=/var/www/asbjj/logs/gunicorn.err.log
stdout_logfile=/var/www/asbjj/logs/gunicorn.out.log

[group:asbjj]
programs=asbjj
EOF

echo -e "${GREEN}✅ Arquivos de configuração criados${NC}"
echo ""
echo -e "${YELLOW}📋 Próximos passos:${NC}"
echo ""
echo "1. Envie os arquivos para o servidor:"
echo -e "   ${GREEN}scp install_server.sh nginx_asbjj.conf supervisor_asbjj.conf .env.production fabianosf@92.113.33.16:~/${NC}"
echo ""
echo "2. Conecte ao servidor via SSH:"
echo -e "   ${GREEN}ssh fabianosf@92.113.33.16${NC}"
echo ""
echo "3. No servidor, execute:"
echo -e "   ${GREEN}chmod +x install_server.sh${NC}"
echo -e "   ${GREEN}./install_server.sh${NC}"
echo ""
echo "4. Configure o Nginx:"
echo -e "   ${GREEN}sudo cp nginx_asbjj.conf /etc/nginx/sites-available/asbjj${NC}"
echo -e "   ${GREEN}sudo ln -s /etc/nginx/sites-available/asbjj /etc/nginx/sites-enabled/${NC}"
echo -e "   ${GREEN}sudo nginx -t${NC}"
echo -e "   ${GREEN}sudo systemctl restart nginx${NC}"
echo ""
echo "5. Configure o Supervisor:"
echo -e "   ${GREEN}sudo cp supervisor_asbjj.conf /etc/supervisor/conf.d/asbjj.conf${NC}"
echo -e "   ${GREEN}sudo supervisorctl reread${NC}"
echo -e "   ${GREEN}sudo supervisorctl update${NC}"
echo -e "   ${GREEN}sudo supervisorctl start asbjj:*${NC}"
echo ""
echo "6. Configure SSL com Let's Encrypt:"
echo -e "   ${GREEN}sudo certbot --nginx -d asbjj.com.br -d www.asbjj.com.br${NC}"
echo ""
echo -e "${YELLOW}⚠️ IMPORTANTE:${NC}"
echo "- Altere a SECRET_KEY no arquivo .env"
echo "- Configure as senhas do banco de dados"
echo "- Configure as credenciais de email"
echo "- Altere a senha do superusuário admin"
echo ""
echo -e "${GREEN}🎉 Deploy preparado com sucesso!${NC}"

