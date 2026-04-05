.PHONY: help \
        up down restart logs \
        migrate migrations createsuperuser collectstatic create-buckets \
        minio-alias minio-ls minio-clear-media minio-clear-static \
        minio-policy-media minio-policy-static \
        minio-public-media minio-public-static

MINIO_ALIAS     = local
MINIO_ENDPOINT  = http://localhost:9000
MINIO_USER      ?= minioadmin
MINIO_PASSWORD  ?= minioadmin123
BUCKET_MEDIA    ?= media
BUCKET_STATIC   ?= static

MC = docker compose exec minio mc

# ─── HELP ──────────────────────────────────────────────────────────────────

help:
	@echo ""
	@echo "  Docker"
	@echo "    up               Start all services"
	@echo "    down             Stop all services"
	@echo "    restart          Restart all services"
	@echo "    logs             Follow logs"
	@echo ""
	@echo "  Django"
	@echo "    migrate          Apply migrations"
	@echo "    migrations       Create new migrations"
	@echo "    createsuperuser  Create Django superuser"
	@echo "    collectstatic    Upload static files to MinIO"
	@echo "    create-buckets   Create and configure MinIO buckets"
	@echo ""
	@echo "  MinIO"
	@echo "    minio-alias      Register local alias in mc"
	@echo "    minio-ls         List all buckets"
	@echo "    minio-clear-media   Clear media bucket"
	@echo "    minio-clear-static  Clear static bucket"
	@echo "    minio-policy-media  Show media bucket policy"
	@echo "    minio-policy-static Show static bucket policy"
	@echo ""

# ─── DOCKER ────────────────────────────────────────────────────────────────

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

# ─── DJANGO ────────────────────────────────────────────────────────────────

migrate:
	python manage.py migrate

migrations:
	python manage.py makemigrations

createsuperuser:
	python manage.py createsuperuser

collectstatic:
	python manage.py collectstatic --noinput

create-buckets:
	python manage.py create_buckets

# ─── MINIO ─────────────────────────────────────────────────────────────────

minio-alias:
	$(MC) alias set $(MINIO_ALIAS) $(MINIO_ENDPOINT) $(MINIO_USER) $(MINIO_PASSWORD)

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

minio-public-media: minio-alias
	$(MC) mb --ignore-existing $(MINIO_ALIAS)/$(BUCKET_MEDIA)
	$(MC) anonymous set public $(MINIO_ALIAS)/$(BUCKET_MEDIA)

minio-public-static: minio-alias
	$(MC) mb --ignore-existing $(MINIO_ALIAS)/$(BUCKET_STATIC)
	$(MC) anonymous set public $(MINIO_ALIAS)/$(BUCKET_STATIC)
