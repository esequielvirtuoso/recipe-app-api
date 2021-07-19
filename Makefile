include help.mk

# environment variables
POSTGRES_NAME = postgres_recipe
NETWORK_NAME  = network_recipe
APP_NAME = recipe_app_api

print_env:
	@echo $(POSTGRES_NAME)

build:
	docker-compose build

env: ##@environment Create network and run postgres container.
	POSTGRES_NAME=${POSTGRES_NAME} \
	NETWORK_NAME=${NETWORK_NAME} \
	APP_NAME=${APP_NAME} \
	docker-compose up -d

env-stop: ##@environment Remove postgres container and remove network.
	POSTGRES_NAME=${POSTGRES_NAME} NETWORK_NAME=${NETWORK_NAME} docker-compose kill
	POSTGRES_NAME=${POSTGRES_NAME} NETWORK_NAME=${NETWORK_NAME} docker-compose rm -vf
	docker network rm $(NETWORK_NAME)

lint:
	POSTGRES_NAME=${POSTGRES_NAME} \
	NETWORK_NAME=${NETWORK_NAME} \
	APP_NAME=${APP_NAME} \
	docker-compose run app sh -c "flake8"

test:
	POSTGRES_NAME=${POSTGRES_NAME} \
	NETWORK_NAME=${NETWORK_NAME} \
	APP_NAME=${APP_NAME} \
	docker-compose run --rm app sh -c "python manage.py test"

# commands used for creating apps
# the migration, admin, and models will be placed only on core app
create_core_app:
	docker-compose run app sh -c "python manage.py startapp core"

start_core_objects_migration:
	POSTGRES_NAME=${POSTGRES_NAME} \
	NETWORK_NAME=${NETWORK_NAME} \
	APP_NAME=${APP_NAME} \
	docker-compose run app sh -c "python manage.py makemigrations core"

create_user_app:
	docker-compose run --rm app sh -c "python manage.py startapp user"

create_recipe_app:
	docker-compose run --rm app sh -c "python manage.py startapp recipe"

migrations:
	POSTGRES_NAME=${POSTGRES_NAME} \
	NETWORK_NAME=${NETWORK_NAME} \
	APP_NAME=${APP_NAME} \
	docker-compose run app sh -c "python manage.py makemigrations"
