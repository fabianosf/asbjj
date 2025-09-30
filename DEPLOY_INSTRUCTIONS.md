# 🚀 Instruções de Deploy - ASBJJ

## ✅ Status Atual

- ✅ Código enviado para GitHub: https://github.com/fabianosf/asbjj
- ✅ Arquivos de configuração criados
- ✅ Scripts preparados

## 📋 Deploy Manual no Servidor

### Passo 1: Conectar ao Servidor

```bash
ssh fabianosf@92.113.33.16
# Senha: 123
```

### Passo 2: Instalar Dependências do Sistema

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências
sudo apt install -y python3-pip python3-venv python3-dev \
    postgresql postgresql-contrib \
    redis-server \
    nginx \
    git \
    supervisor \
    certbot python3-certbot-nginx
```

### Passo 3: Configurar PostgreSQL

```bash
# Entrar no PostgreSQL
sudo -u postgres psql

# No prompt do PostgreSQL, execute:
CREATE DATABASE asbjj_db;
CREATE USER asbjj_user WITH PASSWORD 'SuaSenhaForte123!';
ALTER ROLE asbjj_user SET client_encoding TO 'utf8';
ALTER ROLE asbjj_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE asbjj_user SET timezone TO 'America/Sao_Paulo';
GRANT ALL PRIVILEGES ON DATABASE asbjj_db TO asbjj_user;
\q
```

### Passo 4: Clonar o Projeto

```bash
# Criar diretório
sudo mkdir -p /var/www/asbjj
sudo chown $USER:$USER /var/www/asbjj
cd /var/www/asbjj

# Clonar repositório
git clone https://github.com/fabianosf/asbjj.git .
```

### Passo 5: Configurar Python

```bash
# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### Passo 6: Configurar Variáveis de Ambiente

```bash
# Criar arquivo .env
nano .env
```

Cole o seguinte conteúdo (ajuste as senhas):

```bash
# Django Settings
DEBUG=False
SECRET_KEY=GERE_UMA_CHAVE_SECRETA_ALEATORIA_AQUI
ALLOWED_HOSTS=asbjj.com.br,www.asbjj.com.br,92.113.33.16

# Database
DATABASE_URL=postgresql://asbjj_user:SuaSenhaForte123!@localhost:5432/asbjj_db

# Redis
REDIS_URL=redis://localhost:6379/1

# Email (Configure com suas credenciais)
EMAIL_CONSOLE=False
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu_email@gmail.com
EMAIL_HOST_PASSWORD=sua_senha_de_app_do_gmail
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
ADMIN_URL=admin-secure/
```

**💡 Para gerar SECRET_KEY:**
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Passo 7: Preparar Django

```bash
# Criar diretórios
mkdir -p media/shop/products
mkdir -p staticfiles
mkdir -p logs

# Executar migrações
python manage.py migrate

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Criar superusuário
python manage.py createsuperuser
# Username: admin
# Email: admin@asbjj.com.br
# Password: (escolha uma senha forte)

# Popular loja (opcional)
python manage.py populate_shop
```

### Passo 8: Configurar Nginx

```bash
# Criar configuração do Nginx
sudo nano /etc/nginx/sites-available/asbjj
```

Cole o seguinte conteúdo:

```nginx
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
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }
}
```

Ative o site:

```bash
sudo ln -s /etc/nginx/sites-available/asbjj /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Passo 9: Configurar Supervisor (Gunicorn)

```bash
# Criar configuração do Supervisor
sudo nano /etc/supervisor/conf.d/asbjj.conf
```

Cole o seguinte conteúdo:

```ini
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
```

Ative o Supervisor:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start asbjj:*
sudo supervisorctl status
```

### Passo 10: Configurar SSL (HTTPS)

```bash
# Instalar certificado SSL com Let's Encrypt
sudo certbot --nginx -d asbjj.com.br -d www.asbjj.com.br

# Email: seu_email@gmail.com
# Aceite os termos
# Escolha: Redirect (opção 2)
```

### Passo 11: Configurar DNS

No seu provedor de domínio (Registro.br ou outro), configure:

```
A Record:
asbjj.com.br → 92.113.33.16

CNAME Record:
www.asbjj.com.br → asbjj.com.br
```

## 🔧 Comandos Úteis

### Ver logs do Gunicorn
```bash
tail -f /var/www/asbjj/logs/gunicorn.out.log
tail -f /var/www/asbjj/logs/gunicorn.err.log
```

### Reiniciar aplicação
```bash
sudo supervisorctl restart asbjj:*
```

### Atualizar código do GitHub
```bash
cd /var/www/asbjj
git pull origin main
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
sudo supervisorctl restart asbjj:*
```

### Ver status dos serviços
```bash
# Nginx
sudo systemctl status nginx

# Supervisor
sudo supervisorctl status

# PostgreSQL
sudo systemctl status postgresql

# Redis
sudo systemctl status redis-server
```

## 🎯 Checklist Final

- [ ] PostgreSQL instalado e configurado
- [ ] Redis instalado
- [ ] Código clonado do GitHub
- [ ] Ambiente virtual criado
- [ ] Dependências instaladas
- [ ] Arquivo .env configurado
- [ ] Migrações executadas
- [ ] Superusuário criado
- [ ] Arquivos estáticos coletados
- [ ] Nginx configurado e rodando
- [ ] Supervisor configurado e rodando
- [ ] SSL configurado (HTTPS)
- [ ] DNS configurado

## 🌐 Acessar o Site

Após configurar tudo:

- **Site:** https://asbjj.com.br
- **Admin:** https://asbjj.com.br/admin-secure/

## 🆘 Troubleshooting

### Erro 502 Bad Gateway
```bash
# Verifique se o Gunicorn está rodando
sudo supervisorctl status asbjj:*

# Se não estiver, verifique os logs
tail -f /var/www/asbjj/logs/gunicorn.err.log
```

### Erro de permissão em arquivos estáticos
```bash
cd /var/www/asbjj
sudo chown -R fabianosf:www-data .
sudo chmod -R 755 staticfiles
sudo chmod -R 755 media
```

### Banco de dados não conecta
```bash
# Verifique se o PostgreSQL está rodando
sudo systemctl status postgresql

# Teste a conexão
psql -U asbjj_user -d asbjj_db -h localhost
```

## 📞 Suporte

Se precisar de ajuda, verifique os logs:

```bash
# Logs do Django/Gunicorn
tail -f /var/www/asbjj/logs/gunicorn.err.log

# Logs do Nginx
sudo tail -f /var/log/nginx/error.log

# Logs do Supervisor
sudo tail -f /var/log/supervisor/supervisord.log
```

