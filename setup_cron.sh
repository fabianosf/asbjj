#!/bin/bash

# Script para configurar tarefas agendadas (cron) no servidor
# Execute este script no servidor após o deploy

echo "⏰ Configurando tarefas agendadas (cron)..."

# Adicionar cronjobs
(crontab -l 2>/dev/null; cat << 'EOFCRON'
# ASBJJ - Tarefas Agendadas

# Backup diário às 2h da manhã
0 2 * * * cd /var/www/asbjj && ./backup.sh daily >> /var/www/asbjj/logs/backup.log 2>&1

# Backup semanal aos domingos às 3h
0 3 * * 0 cd /var/www/asbjj && ./backup.sh weekly >> /var/www/asbjj/logs/backup.log 2>&1

# Backup mensal no primeiro dia do mês às 4h
0 4 1 * * cd /var/www/asbjj && ./backup.sh monthly >> /var/www/asbjj/logs/backup.log 2>&1

# Limpar sessões antigas diariamente às 1h
0 1 * * * cd /var/www/asbjj && source venv/bin/activate && python manage.py clearsessions >> /var/www/asbjj/logs/cleanup.log 2>&1

# Renovar certificado SSL (Let's Encrypt) - tenta renovar duas vezes por dia
0 */12 * * * certbot renew --quiet --post-hook "systemctl reload nginx" >> /var/www/asbjj/logs/certbot.log 2>&1

# Verificar saúde da aplicação a cada 5 minutos
*/5 * * * * curl -s http://127.0.0.1:8000/healthz > /dev/null || echo "ERRO: Site fora do ar em $(date)" >> /var/www/asbjj/logs/health.log

# Limpar logs antigos (> 30 dias) semanalmente
0 5 * * 1 find /var/www/asbjj/logs -name "*.log" -type f -mtime +30 -delete

# Atualizar código do GitHub diariamente às 5h (opcional - comente se não quiser)
# 0 5 * * * cd /var/www/asbjj && git pull origin main && source venv/bin/activate && python manage.py migrate --noinput && python manage.py collectstatic --noinput && supervisorctl restart asbjj:* >> /var/www/asbjj/logs/auto_update.log 2>&1

EOFCRON
) | crontab -

echo "✅ Cronjobs configurados com sucesso!"
echo ""
echo "📋 Tarefas agendadas:"
echo "  - Backup diário: 2h"
echo "  - Backup semanal: Domingo 3h"
echo "  - Backup mensal: Dia 1 às 4h"
echo "  - Limpeza de sessões: 1h"
echo "  - Renovação SSL: A cada 12h"
echo "  - Health check: A cada 5min"
echo "  - Limpeza de logs: Segunda-feira 5h"
echo ""
echo "Ver cronjobs ativos:"
echo "  crontab -l"
echo ""
echo "Logs dos cronjobs:"
echo "  tail -f /var/www/asbjj/logs/backup.log"
echo "  tail -f /var/www/asbjj/logs/cleanup.log"
echo "  tail -f /var/www/asbjj/logs/health.log"

