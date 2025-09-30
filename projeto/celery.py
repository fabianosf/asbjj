import os
from celery import Celery

# Configurar o Django antes de importar os apps
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projeto.settings')

app = Celery('asbjj')

# Configurações do Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-descobrir tarefas nos apps
app.autodiscover_tasks()

# Configurações adicionais
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Sao_Paulo',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutos
    task_soft_time_limit=25 * 60,  # 25 minutos
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

@app.task(bind=True)
def debug_task(self):
    # Request logged
