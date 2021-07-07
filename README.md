# recipe-app-api
Recipe app api source code.


# Notes

Adding django project.
```
docker-compose run app sh -c "django-admin.py startproject app ."
```

## REST API Documentation

All available REST API documentation exposed by the project was documented using the [OpenAPI](https://www.openapis.org/) standard.

To view this documentation locally use the following command:
```bash
make run-swagger
```

_API routes documentation generate by [Swagger-UI](https://github.com/swagger-api/swagger-ui)._


## Getting Started

### Prerequisites

- [Python](https://www.python.org)(>=3.7)
- [GNU Make](https://www.gnu.org/software/make/)
- [Docker](http://docker.com)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Requirements
If you want to install the requirements locally on the host machine you can run the following command.
```
pip install -r /requirements.txt
```

## Building the application
```
make build
```

## Verifying code issues
```
make lint
```

## Running the test
```
make test
```
