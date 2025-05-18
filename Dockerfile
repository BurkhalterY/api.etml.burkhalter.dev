# syntax=docker/dockerfile:1
FROM python:3.10-alpine
WORKDIR /api
COPY . .
RUN pip3 install poetry
RUN poetry install
EXPOSE 8000
CMD ["poetry", "run", "start"]
