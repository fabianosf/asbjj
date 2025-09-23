# ASBJJ - Makefile para comandos de desenvolvimento e produção

.PHONY: help install run migrate collectstatic shell test clean build up down logs celery beat

# Variáveis
PYTHON := python
PIP := pip
MANAGE := python manage.py
DOCKER_COMPOSE := docker-compose

# Comando padrão
help:
	@echo "Comandos disponíveis:"
	@echo "  install     - Instalar dependências"
	@echo "  run         - Executar servidor de desenvolvimento"
	@echo "  migrate     - Aplicar migrações"
	@echo "  makemigrations - Criar migrações"
	@echo "  collectstatic - Coletar arquivos estáticos"
	@echo "  shell       - Abrir shell do Django"
	@echo "  test        - Executar testes"
	@echo "  clean       - Limpar arquivos temporários"
	@echo "  build       - Buildar imagem Docker"
	@echo "  up          - Subir serviços com Docker Compose"
	@echo "  down        - Parar serviços Docker Compose"
	@echo "  logs        - Ver logs dos serviços"
	@echo "  celery      - Executar worker do Celery"
	@echo "  beat        - Executar scheduler do Celery"
	@echo "  superuser   - Criar superusuário"

# Instalação e setup
install:
	$(PIP) install -r requirements.txt

# Desenvolvimento
run:
	$(MANAGE) runserver

migrate:
	$(MANAGE) migrate

makemigrations:
	$(MANAGE) makemigrations

collectstatic:
	$(MANAGE) collectstatic --noinput

shell:
	$(MANAGE) shell

test:
	$(MANAGE) test

superuser:
	$(MANAGE) createsuperuser

# Limpeza
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/

# Docker
build:
	docker build -t asbjj .

up:
	$(DOCKER_COMPOSE) up -d

down:
	$(DOCKER_COMPOSE) down

logs:
	$(DOCKER_COMPOSE) logs -f

# Celery
celery:
	celery -A projeto worker --loglevel=info

beat:
	celery -A projeto beat --loglevel=info

# Produção
deploy:
	$(MANAGE) check --deploy
	$(MANAGE) migrate --noinput
	$(MANAGE) collectstatic --noinput

# Backup do banco
backup:
	$(MANAGE) dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission > backup_$(shell date +%Y%m%d_%H%M%S).json

# Restaurar backup
restore:
	@echo "Digite o nome do arquivo de backup:"
	@read file; $(MANAGE) loaddata $$file
