include help.mk

build:
	DOCKER_BUILDKIT=1 \
	docker build --progress=plain \
		--target=security \
		--file=Dockerfile .

lint:
	docker-compose run app sh -c "flake8"

test:
	docker-compose run app sh -c "python manage.py test"

start_core:
	docker-compose run app sh -c "python manage.py startapp core"

migrate_objects:
	docker-compose run app sh -c "python manage.py makemigrations core"
