FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION=1.6.1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install "poetry==$POETRY_VERSION"

COPY pyproject.toml poetry.lock* /app/

RUN poetry config virtualenvs.create false

RUN poetry install --no-interaction --no-ansi --no-root || \
    (poetry lock --no-update && poetry install --no-interaction --no-ansi --no-root)

COPY . /app/

RUN mkdir -p /app/staticfiles && chmod -R 755 /app/staticfiles

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]