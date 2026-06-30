build:
	docker compose build

up:
	docker compose up -d

ps:
	docker compose ps

migrate:
	docker compose exec app python manage.py migrate

collectstatic:
	docker compose exec app python manage.py collectstatic --noinput

createsuperuser:
	docker compose exec app python manage.py createsuperuser


logs:
	docker compose logs -f 

stop:
	docker compose stop

rm: stop:
	docker compose rm -f