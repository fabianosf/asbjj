#!/bin/bash

# Script de Deploy Automático para ASBJJ
# Executa instalação completa no servidor

set -e

SERVER="fabianosf@92.113.33.16"
PASSWORD="123"
SUDO_PASSWORD="123"

echo "🚀 Iniciando deploy automático para asbjj.com.br"

# Criar script de instalação que será executado no servidor
cat > remote_install.sh << 'EOFREMOTE'
#!/bin/bash
set -e

echo "📦 Atualizando sistema..."
echo "123" | sudo -S apt update -y
echo "123" | sudo -S apt upgrade -y

echo "📦 Instalando dependências..."
echo "123" | sudo -S apt install -y python3-pip python3-venv python3-dev \
    postgresql postgresql-contrib \
    redis-server \
    nginx \
    git \
    supervisor \
    certbot python3-certbot-nginx \
    libpq-dev

echo "🗄️ Configurando PostgreSQL..."
echo "123" | sudo -S -u postgres psql -c "DROP DATABASE IF EXISTS asbjj_db;" || true
echo "123" | sudo -S -u postgres psql -c "DROP USER IF EXISTS asbjj_user;" || true
echo "123" | sudo -S -u postgres psql << EOF
CREATE DATABASE asbjj_db;
CREATE USER asbjj_user WITH PASSWORD 'asbjj2024secure!';
ALTER ROLE asbjj_user SET client_encoding TO 'utf8';
ALTER ROLE asbjj_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE asbjj_user SET timezone TO 'America/Sao_Paulo';
GRANT ALL PRIVILEGES ON DATABASE asbjj_db TO asbjj_user;
ALTER DATABASE asbjj_db OWNER TO asbjj_user;
EOF

echo "📁 Criando estrutura de diretórios..."
echo "123" | sudo -S mkdir -p /var/www/asbjj
echo "123" | sudo -S chown -R $USER:$USER /var/www/asbjj

if [ -d "/var/www/asbjj/.git" ]; then
    echo "📥 Atualizando repositório..."
    cd /var/www/asbjj
    git pull origin main || git clone https://github.com/fabianosf/asbjj.git .
else
    echo "📥 Clonando repositório..."
    cd /var/www/asbjj
    git clone https://github.com/fabianosf/asbjj.git .
fi

echo "🐍 Configurando Python..."
cd /var/www/asbjj
python3 -m venv venv
source venv/bin/activate

echo "📦 Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

echo "⚙️ Configurando variáveis de ambiente..."
cat > .env << 'EOFENV'
DEBUG=False
SECRET_KEY=django-insecure-production-key-$(date +%s)-$(openssl rand -hex 32)
ALLOWED_HOSTS=asbjj.com.br,www.asbjj.com.br,92.113.33.16,localhost,127.0.0.1

DATABASE_URL=postgresql://asbjj_user:asbjj2024secure!@localhost:5432/asbjj_db

REDIS_URL=redis://localhost:6379/1

EMAIL_CONSOLE=True
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@asbjj.com.br
ADMIN_EMAIL=admin@asbjj.com.br

SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

SITE_URL=http://92.113.33.16

ADMIN_WHATSAPP=5521989307826

ADMIN_URL=admin-secure/
EOFENV

echo "📁 Criando diretórios..."
mkdir -p media/shop/products
mkdir -p staticfiles
mkdir -p logs

echo "🗄️ Executando migrações..."
python manage.py migrate --noinput

echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "👤 Criando superusuário..."
python manage.py shell << 'PYEOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@asbjj.com.br', 'admin123')
    print('✅ Superusuário criado: admin/admin123')
else:
    print('ℹ️ Superusuário já existe')
PYEOF

echo "📊 Populando loja..."
python manage.py populate_shop || echo "⚠️ Dados já existem"

echo "🔧 Configurando Nginx..."
echo "123" | sudo -S tee /etc/nginx/sites-available/asbjj > /dev/null << 'EOFNGINX'
server {
    listen 80;
    server_name asbjj.com.br www.asbjj.com.br 92.113.33.16;
    
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
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }
}
EOFNGINX

echo "123" | sudo -S ln -sf /etc/nginx/sites-available/asbjj /etc/nginx/sites-enabled/
echo "123" | sudo -S rm -f /etc/nginx/sites-enabled/default
echo "123" | sudo -S nginx -t
echo "123" | sudo -S systemctl restart nginx

echo "🔧 Configurando Supervisor..."
echo "123" | sudo -S tee /etc/supervisor/conf.d/asbjj.conf > /dev/null << EOFSUP
[program:asbjj]
command=/var/www/asbjj/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 --timeout 300 projeto.wsgi:application
directory=/var/www/asbjj
user=$USER
autostart=true
autorestart=true
stderr_logfile=/var/www/asbjj/logs/gunicorn.err.log
stdout_logfile=/var/www/asbjj/logs/gunicorn.out.log
environment=PATH="/var/www/asbjj/venv/bin"

[group:asbjj]
programs=asbjj
EOFSUP

echo "123" | sudo -S supervisorctl reread
echo "123" | sudo -S supervisorctl update
echo "123" | sudo -S supervisorctl restart asbjj:* || echo "123" | sudo -S supervisorctl start asbjj:*

echo "✅ Deploy concluído com sucesso!"
echo ""
echo "🌐 Acesse o site em:"
echo "   http://92.113.33.16"
echo "   http://asbjj.com.br (após configurar DNS)"
echo ""
echo "🔐 Admin:"
echo "   http://92.113.33.16/admin-secure/"
echo "   Usuário: admin"
echo "   Senha: admin123"
echo ""
echo "📊 Comandos úteis:"
echo "   sudo supervisorctl status"
echo "   sudo supervisorctl restart asbjj:*"
echo "   tail -f /var/www/asbjj/logs/gunicorn.err.log"
EOFREMOTE

chmod +x remote_install.sh

echo "📤 Enviando script para o servidor..."
sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no remote_install.sh $SERVER:~/

echo "🚀 Executando instalação no servidor..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER 'chmod +x remote_install.sh && ./remote_install.sh'

echo ""
echo "✅ Deploy automático concluído!"
echo ""
echo "🌐 Acesse:"
echo "   Site: http://92.113.33.16"
echo "   Admin: http://92.113.33.16/admin-secure/"
echo "   User: admin / Senha: admin123"

