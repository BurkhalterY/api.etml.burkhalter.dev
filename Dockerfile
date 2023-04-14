# syntax=docker/dockerfile:1
FROM python:3.10-alpine
WORKDIR /doc-docker
COPY . .
RUN pip install poetry
RUN poetry install
EXPOSE 8000
CMD ["poetry", "run", "start"]