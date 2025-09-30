#!/bin/bash
# Script para facilitar a troca de senha do administrador
# Uso: ./trocar_senha_admin.sh

echo "================================================"
echo "🔐 ASBJJ - Troca de Senha do Administrador"
echo "================================================"
echo ""

# Verificar se está no diretório correto
if [ ! -f "manage.py" ]; then
    echo "❌ Erro: Este script deve ser executado no diretório raiz do projeto!"
    echo "   Execute: cd /home/fabianosf/Documents/asbjj"
    exit 1
fi

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "❌ Erro: Ambiente virtual não encontrado!"
    echo "   Crie o ambiente virtual primeiro: python3 -m venv venv"
    exit 1
fi

# Ativar ambiente virtual
echo "📦 Ativando ambiente virtual..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ Erro ao ativar ambiente virtual!"
    exit 1
fi

echo "✅ Ambiente virtual ativado!"
echo ""

# Executar comando de troca de senha
echo "🔑 Iniciando processo de troca de senha..."
echo ""

python manage.py change_admin_password

# Verificar se o comando foi executado com sucesso
if [ $? -eq 0 ]; then
    echo ""
    echo "================================================"
    echo "✅ Processo concluído!"
    echo "================================================"
    echo ""
    echo "📌 Próximos passos:"
    echo "   1. Tente fazer login com a nova senha"
    echo "   2. Caso necessário, reinicie o servidor:"
    echo "      ./restart_server.sh"
    echo ""
else
    echo ""
    echo "================================================"
    echo "❌ Erro ao trocar senha!"
    echo "================================================"
    echo ""
    echo "💡 Tente usar um dos métodos alternativos:"
    echo "   python manage.py changepassword admin"
    echo ""
fi

# Desativar ambiente virtual
deactivate 2>/dev/null

exit 0

