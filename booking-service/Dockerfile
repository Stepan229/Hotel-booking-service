FROM python:3.13-alpine3.21 AS builder
LABEL authors="sskry"

WORKDIR /app
COPY poetry.lock pyproject.toml ./
# COPY README.md ./s

RUN python -m pip install --no-cache-dir poetry==2.2.1 \
    && poetry config virtualenvs.in-project true \
    # && poetry install --without dev,test --no-interaction --no-ansi
    && poetry install --no-interaction --no-ansi --no-root


FROM python:3.13-alpine3.21


COPY --from=builder /app /app

COPY /src /app

