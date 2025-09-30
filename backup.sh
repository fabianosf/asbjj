#!/bin/bash

# Script de backup automático para ASBJJ
# Uso: ./backup.sh [tipo]
# Tipos: daily, weekly, monthly

set -e

# Configurações
PROJECT_DIR="/home/fabianosf/Documents/asbjj"
BACKUP_DIR="$PROJECT_DIR/backups"
VENV_DIR="$PROJECT_DIR/venv"
LOG_FILE="$BACKUP_DIR/backup.log"

# Criar diretório de backup se não existir
mkdir -p "$BACKUP_DIR"

# Função de log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Função para executar comando no ambiente virtual
run_in_venv() {
    source "$VENV_DIR/bin/activate"
    cd "$PROJECT_DIR"
    "$@"
    deactivate
}

# Determinar tipo de backup
BACKUP_TYPE=${1:-daily}

case $BACKUP_TYPE in
    daily)
        RETENTION_DAYS=7
        BACKUP_NAME="daily"
        ;;
    weekly)
        RETENTION_DAYS=30
        BACKUP_NAME="weekly"
        ;;
    monthly)
        RETENTION_DAYS=365
        BACKUP_NAME="monthly"
        ;;
    *)
        echo "Tipo de backup inválido. Use: daily, weekly ou monthly"
        exit 1
        ;;
esac

log "Iniciando backup $BACKUP_NAME"

# Verificar se o ambiente virtual existe
if [ ! -d "$VENV_DIR" ]; then
    log "ERRO: Ambiente virtual não encontrado em $VENV_DIR"
    exit 1
fi

# Verificar se o projeto existe
if [ ! -f "$PROJECT_DIR/manage.py" ]; then
    log "ERRO: Projeto Django não encontrado em $PROJECT_DIR"
    exit 1
fi

# Executar backup
log "Executando backup do banco de dados e mídia..."
run_in_venv python manage.py backup_database \
    --output-dir "$BACKUP_DIR" \
    --include-media \
    --compress

# Mover arquivo para nome específico do tipo
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/backup_*.zip | head -n1)
if [ -n "$LATEST_BACKUP" ]; then
    NEW_NAME="$BACKUP_DIR/${BACKUP_NAME}_backup_${TIMESTAMP}.zip"
    mv "$LATEST_BACKUP" "$NEW_NAME"
    log "Backup salvo como: $NEW_NAME"
fi

# Limpar backups antigos
log "Limpando backups antigos (mais de $RETENTION_DAYS dias)..."
find "$BACKUP_DIR" -name "${BACKUP_NAME}_backup_*.zip" -type f -mtime +$RETENTION_DAYS -delete

# Verificar espaço em disco
DISK_USAGE=$(df "$BACKUP_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
    log "AVISO: Uso de disco alto ($DISK_USAGE%). Considere limpar backups antigos."
fi

# Estatísticas do backup
BACKUP_SIZE=$(du -h "$NEW_NAME" | cut -f1)
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/*.zip 2>/dev/null | wc -l)

log "Backup $BACKUP_NAME concluído com sucesso!"
log "Tamanho: $BACKUP_SIZE"
log "Total de backups: $BACKUP_COUNT"

# Enviar notificação por email (opcional)
if [ -n "$BACKUP_EMAIL" ]; then
    echo "Backup $BACKUP_NAME concluído em $(date)" | \
    mail -s "Backup ASBJJ - $BACKUP_NAME" "$BACKUP_EMAIL"
fi

log "Backup finalizado"
