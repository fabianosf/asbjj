#!/bin/bash
# Script de Deploy Automatizado para o Servidor ASBJJ
# Servidor: 92.113.33.16
# Domínio: asbjj.com.br

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                                                                    ║"
echo "║                  🚀 DEPLOY ASBJJ - asbjj.com.br                   ║"
echo "║                                                                    ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configurações
SERVER_USER="fabianosf"
SERVER_IP="92.113.33.16"
SERVER_PASSWORD="123"
PROJECT_PATH="/home/fabianosf/asbjj"
DOMAIN="asbjj.com.br"

echo -e "${BLUE}📡 Conectando ao servidor ${SERVER_IP}...${NC}"
echo ""

# Criar script de deploy remoto
cat > /tmp/remote_deploy.sh << 'REMOTE_SCRIPT'
#!/bin/bash
set -e

echo "🔄 Atualizando código do GitHub..."
cd /home/fabianosf/asbjj || cd /var/www/asbjj || exit 1

# Fazer backup antes de atualizar
echo "💾 Criando backup..."
BACKUP_DIR="/home/fabianosf/backups/asbjj_$(date +%Y%m%d_%H%M%S)"
mkdir -p /home/fabianosf/backups
cp -r . "$BACKUP_DIR" 2>/dev/null || echo "Aviso: Backup não criado"

# Atualizar do GitHub
echo "📥 Baixando atualizações do GitHub..."
git fetch origin
git reset --hard origin/main
git pull origin main

# Ativar ambiente virtual
echo "🐍 Ativando ambiente virtual..."
source venv/bin/activate || python3 -m venv venv && source venv/bin/activate

# Instalar/atualizar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt --upgrade

# Coletar arquivos estáticos
echo "🎨 Coletando arquivos estáticos..."
python manage.py collectstatic --no-input

# Aplicar migrações
echo "🗄️  Aplicando migrações do banco de dados..."
python manage.py migrate

# Criar superusuário se não existir
echo "👤 Verificando superusuário..."
python manage.py shell << 'PYCODE'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@asbjj.com.br', 'admin123')
    print("✅ Superusuário criado: admin / admin123")
else:
    print("✅ Superusuário já existe")
PYCODE

# Reiniciar serviços
echo "🔄 Reiniciando serviços..."

# Tentar diferentes métodos de reinicialização
if [ -f /etc/systemd/system/asbjj.service ]; then
    echo "  → Reiniciando via systemd..."
    sudo systemctl restart asbjj
    sudo systemctl restart nginx
elif [ -f /etc/supervisor/conf.d/asbjj.conf ] || [ -f /etc/supervisor/conf.d/supervisor_asbjj.conf ]; then
    echo "  → Reiniciando via supervisor..."
    sudo supervisorctl restart asbjj
    sudo systemctl restart nginx
elif pgrep -f "gunicorn.*asbjj" > /dev/null; then
    echo "  → Reiniciando gunicorn..."
    sudo pkill -HUP gunicorn
    sudo systemctl restart nginx
else
    echo "  ⚠️  Serviço não encontrado. Tentando reiniciar nginx..."
    sudo systemctl restart nginx
fi

# Verificar permissões
echo "🔐 Ajustando permissões..."
sudo chown -R www-data:www-data staticfiles/ media/ 2>/dev/null || \
sudo chown -R nginx:nginx staticfiles/ media/ 2>/dev/null || \
sudo chown -R $USER:$USER staticfiles/ media/

# Limpar cache do Django
echo "🧹 Limpando cache..."
python manage.py shell << 'PYCODE'
from django.core.cache import cache
cache.clear()
print("✅ Cache limpo")
PYCODE

echo ""
echo "✅ Deploy concluído com sucesso!"
echo ""
echo "🌐 Acesse: http://asbjj.com.br"
echo "🔐 Admin: http://asbjj.com.br/admin"
echo "   Login: admin"
echo "   Senha: admin123"
echo ""
REMOTE_SCRIPT

# Copiar e executar script no servidor
echo -e "${YELLOW}📤 Enviando script de deploy para o servidor...${NC}"
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no /tmp/remote_deploy.sh ${SERVER_USER}@${SERVER_IP}:/tmp/

echo -e "${YELLOW}⚙️  Executando deploy no servidor...${NC}"
echo ""
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} 'bash /tmp/remote_deploy.sh'

# Limpar
rm /tmp/remote_deploy.sh 2>/dev/null

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                                                                    ║"
echo "║                    ✅ DEPLOY CONCLUÍDO COM SUCESSO!                ║"
echo "║                                                                    ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}🎉 Seu site está no ar!${NC}"
echo ""
echo -e "${BLUE}🌐 URL do Site:${NC} http://asbjj.com.br"
echo -e "${BLUE}🔐 Painel Admin:${NC} http://asbjj.com.br/admin"
echo ""
echo -e "${YELLOW}📋 Credenciais de Acesso:${NC}"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo -e "${YELLOW}💡 Dica:${NC} Troque a senha do admin usando:"
echo "   ssh ${SERVER_USER}@${SERVER_IP}"
echo "   cd /home/fabianosf/asbjj"
echo "   ./trocar_senha_admin.sh"
echo ""

