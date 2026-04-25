.PHONY: help up up-obs down build rebuild logs \
        migrate migrations createsuperuser collectstatic shell-backend \
        create-buckets minio-alias minio-ls minio-clear-media minio-clear-static \
        minio-policy-media minio-policy-static \
        reset-db reset-all

COMPOSE      = docker compose -f docker-compose.prod.yml
COMPOSE_OBS  = $(COMPOSE) -f docker-compose.observability.yml
ENV_FILE     = .env.prod

MC             = $(COMPOSE) --env-file $(ENV_FILE) exec minio mc
MINIO_ALIAS    = local
MINIO_ENDPOINT = http://localhost:9000
BUCKET_MEDIA  ?= media
BUCKET_STATIC ?= static

help:
	@echo ""
	@echo "  Production"
	@echo "    up               Start core services"
	@echo "    up-obs           Start core + observability services"
	@echo "    down             Stop all services"
	@echo "    build            Rebuild all images without cache"
	@echo "    rebuild          Rebuild and restart one service: make rebuild service=backend"
	@echo "    logs             Follow logs (all services)"
	@echo ""
	@echo "  Django"
	@echo "    migrate          Apply pending migrations"
	@echo "    migrations       Create new migrations"
	@echo "    createsuperuser  Create Django superuser"
	@echo "    collectstatic    Push static files to MinIO"
	@echo "    shell-backend    Open Django shell"
	@echo ""
	@echo "  Data"
	@echo "    reset-db            Drop postgres volume and restart (loses all DB data)"
	@echo "    reset-all           Drop ALL volumes and restart (loses DB + MinIO + cache)"
	@echo ""
	@echo "  MinIO"
	@echo "    create-buckets      Create media/static buckets and set public policy"
	@echo "    minio-alias         Register local alias in mc"
	@echo "    minio-ls            List all buckets"
	@echo "    minio-clear-media   Delete all objects in media bucket"
	@echo "    minio-clear-static  Delete all objects in static bucket"
	@echo "    minio-policy-media  Show media bucket policy"
	@echo "    minio-policy-static Show static bucket policy"
	@echo ""

# ─── DOCKER ────────────────────────────────────────────────────────────────

up:
	$(COMPOSE) --env-file $(ENV_FILE) up -d

up-obs:
	$(COMPOSE_OBS) --env-file $(ENV_FILE) up -d

down:
	$(COMPOSE) --env-file $(ENV_FILE) down

build:
	$(COMPOSE) --env-file $(ENV_FILE) build --no-cache

rebuild:
	$(COMPOSE) --env-file $(ENV_FILE) build --no-cache $(service)
	$(COMPOSE) --env-file $(ENV_FILE) up -d $(service)

logs:
	$(COMPOSE) --env-file $(ENV_FILE) logs -f

# ─── DJANGO ────────────────────────────────────────────────────────────────

migrate:
	$(COMPOSE) --env-file $(ENV_FILE) exec backend python manage.py migrate

migrations:
	$(COMPOSE) --env-file $(ENV_FILE) exec backend python manage.py makemigrations

createsuperuser:
	$(COMPOSE) --env-file $(ENV_FILE) exec backend python manage.py createsuperuser

collectstatic:
	$(COMPOSE) --env-file $(ENV_FILE) exec backend python manage.py collectstatic --noinput

shell-backend:
	$(COMPOSE) --env-file $(ENV_FILE) exec backend python manage.py shell

# ─── MINIO ─────────────────────────────────────────────────────────────────

minio-alias:
	$(MC) alias set $(MINIO_ALIAS) $(MINIO_ENDPOINT) $${AWS_ACCESS_KEY_ID} $${AWS_SECRET_ACCESS_KEY}

create-buckets: minio-alias
	$(MC) mb --ignore-existing $(MINIO_ALIAS)/$(BUCKET_MEDIA) $(MINIO_ALIAS)/$(BUCKET_STATIC)
	$(MC) anonymous set public $(MINIO_ALIAS)/$(BUCKET_MEDIA)
	$(MC) anonymous set public $(MINIO_ALIAS)/$(BUCKET_STATIC)

minio-ls: minio-alias
	$(MC) ls $(MINIO_ALIAS)

minio-clear-media: minio-alias
	$(MC) rm --recursive --force $(MINIO_ALIAS)/$(BUCKET_MEDIA)

minio-clear-static: minio-alias
	$(MC) rm --recursive --force $(MINIO_ALIAS)/$(BUCKET_STATIC)

minio-policy-media: minio-alias
	$(MC) anonymous get $(MINIO_ALIAS)/$(BUCKET_MEDIA)

minio-policy-static: minio-alias
	$(MC) anonymous get $(MINIO_ALIAS)/$(BUCKET_STATIC)

# ─── DATA ──────────────────────────────────────────────────────────────────

reset-db:
	$(COMPOSE) --env-file $(ENV_FILE) down
	docker volume rm $$(docker volume ls -q | grep postgres_data) 2>/dev/null || true
	$(COMPOSE) --env-file $(ENV_FILE) up -d

reset-all:
	$(COMPOSE) --env-file $(ENV_FILE) down -v
	$(COMPOSE) --env-file $(ENV_FILE) up -d
