FROM python:3.13-alpine3.21 AS builder
LABEL authors="sskry"

# ARG HTTP_PROXY=http://TKZfRFyA:rDvDMuHV@109.197.16.225:63264
# ARG HTTPS_PROXY=http://TKZfRFyA:rDvDMuHV@109.197.16.225:63264

WORKDIR /app
COPY poetry.lock pyproject.toml ./

RUN python -m pip install --no-cache-dir poetry==2.2.1 \
    && poetry config virtualenvs.in-project true \
    # && poetry install --without dev,test --no-interaction --no-ansi
    && poetry install --no-interaction --no-ansi --no-root


FROM python:3.13-alpine3.21

WORKDIR /app

COPY --from=builder /app /app

COPY ./src /app

ENV PATH="/app/.venv/bin:$PATH"
