.PHONY: help setup start stop restart build logs shell test test-agents test-views test-specific up clean lint migrate all

# Configuração padrão
all: start

# Iniciar todos os serviços
start:
	docker compose up -d

# Iniciar todos os serviços em primeiro plano (com logs)
up:
	docker compose up

# Parar todos os serviços
stop:
	docker compose down

# Construir os serviços
build:
	docker compose build

# Configuração completa (build + start + migrate)
setup: build start migrate

# Reiniciar serviços
restart: stop start

# Ver logs
logs:
	docker compose logs -f

# Acessar shell Django
shell:
	docker compose exec web poetry run python manage.py shell

# Executar migrações
migrate:
	docker compose exec web poetry run python manage.py migrate

# Testes
test:
	docker compose exec web poetry run python manage.py test analyzer.tests --keepdb

test-agents:
	docker compose exec web poetry run python manage.py test analyzer.tests.test_agents --keepdb

test-views:
	docker compose exec web poetry run python manage.py test analyzer.tests.test_upload_and_report --keepdb