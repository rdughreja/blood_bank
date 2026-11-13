FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm
# Node 22 for the Next.js frontend + Postgres client for pg_isready checks
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get update && apt-get install -y --no-install-recommends nodejs postgresql-client \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
