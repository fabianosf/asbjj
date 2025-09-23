from celery.schedules import crontab

# Configuração do Celery Beat para tarefas agendadas
CELERY_BEAT_SCHEDULE = {
    # Limpar sessões expiradas diariamente às 2:00
    'cleanup-old-sessions': {
        'task': 'core.tasks.cleanup_old_sessions',
        'schedule': crontab(hour=2, minute=0),
    },
    
    # Enviar newsletter semanal às segundas-feiras às 9:00
    'send-weekly-newsletter': {
        'task': 'core.tasks.send_weekly_newsletter',
        'schedule': crontab(hour=9, minute=0, day_of_week=1),
    },
    
    # Backup do banco de dados diariamente às 3:00
    'database-backup': {
        'task': 'core.tasks.database_backup',
        'schedule': crontab(hour=3, minute=0),
    },
    
    # Limpar logs antigos semanalmente aos domingos às 1:00
    'cleanup-old-logs': {
        'task': 'core.tasks.cleanup_old_logs',
        'schedule': crontab(hour=1, minute=0, day_of_week=0),
    },
    
    # Enviar lembretes de pagamento mensalmente
    'send-payment-reminders': {
        'task': 'core.tasks.send_payment_reminders',
        'schedule': crontab(hour=10, minute=0, day=1),  # Todo dia 1 do mês às 10:00
    },
    
    # Estatísticas mensais
    'generate-monthly-stats': {
        'task': 'core.tasks.generate_monthly_stats',
        'schedule': crontab(hour=11, minute=0, day=1),  # Todo dia 1 do mês às 11:00
    },
}
