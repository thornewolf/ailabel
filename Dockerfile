FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
# Copy the project into the image
ADD . /app

# Sync the project into a new environment, using the frozen lockfile
WORKDIR /app

RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*

RUN uv sync --frozen
RUN npx tailwindcss -i ./static/css/styles.css -o ./static/css/tailwind.css --content "/app/templates/*.html"

# Set the startup command
CMD ["uv", "run", "/app/main.py"]