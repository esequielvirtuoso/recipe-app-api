FROM python:3.7-alpine AS base

ENV PYTHONUNBUFFERED 1

# --- install dependencies ---
FROM base AS dependencies
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# create projects root directory in the container
FROM dependencies AS setup
RUN mkdir /app
WORKDIR /app
COPY ./app /app

# create a user for running the application only - security purpose
FROM setup AS security
RUN adduser -D user
USER user