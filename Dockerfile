FROM python:3.7-alpine AS base

ENV PYTHONUNBUFFERED 1

# --- install dependencies ---
FROM base AS dependencies
COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
        gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev
RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps

# create projects root directory in the container
FROM dependencies AS setup
RUN mkdir /app
WORKDIR /app
COPY ./app /app

# create a user for running the application only - security purpose
FROM setup AS security
RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
RUN adduser -D user
RUN chown -R user:user /vol/
RUN chmod -R 755 /vol/web
USER user
