# Use an official Python runtime as a parent image
FROM --platform=linux/amd64 python:3.12.4-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies, Node.js, npm, and Poetry in a single layer
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get install -y nodejs && \
    pip install --no-cache-dir poetry && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy only requirements to cache them in docker layer
COPY pyproject.toml poetry.lock* /app/

# Project initialization:
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root --only main

# Copy project files
COPY ./src ./src

# Create workspaces directory
# RUN mkdir -p workspaces

EXPOSE 80

HEALTHCHECK CMD curl --fail http://localhost:80/_stcore/health

# Run the application
CMD ["poetry", "run", "streamlit", "run", "src/travel_assistant.py", "--server.port=80", "--server.address=0.0.0.0"]