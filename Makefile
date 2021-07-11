include help.mk

POSTGRES_NAME = postgres_recipe
NETWORK_NAME  = network_recipe

print_env:
	@echo $(POSTGRES_NAME)

build:
	DOCKER_BUILDKIT=1 \
	docker build --progress=plain \
		--target=security \
		--file=Dockerfile .

env: ##@environment Create network and run postgres container.
	POSTGRES_NAME=${POSTGRES_NAME} \
	NETWORK_NAME=${NETWORK_NAME} \
	docker-compose up -d

lint:
	docker-compose run app sh -c "flake8"

test:
	docker-compose run --rm app sh -c "python manage.py test"

create_core_app:
	docker-compose run app sh -c "python manage.py startapp core"

start_core_objects_migration:
	docker-compose run app sh -c "python manage.py makemigrations core"

create_user_app:
	docker-compose run --rm app sh -c "python manage.py startapp user"
