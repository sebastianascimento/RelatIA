FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION=1.6.1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install "poetry==$POETRY_VERSION"

# Copy poetry configuration files
COPY pyproject.toml poetry.lock* /app/

# Configure poetry to not use virtualenv
RUN poetry config virtualenvs.create false

# Install dependencies - with more robust error handling
RUN poetry install --no-interaction --no-ansi --no-root || \
    (poetry lock --no-update && poetry install --no-interaction --no-ansi --no-root)

# Copy project
COPY . /app/

# Create static files directory and set permissions
RUN mkdir -p /app/staticfiles && chmod -R 755 /app/staticfiles

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]