# Stage 1: Build stage for installing dependencies
FROM python:3.12-slim AS build
# Install curl and other build essentials if needed in the build stage
RUN apt-get update && apt-get install -y curl ca-certificates && rm -rf /var/lib/apt/lists/*

# Copy the uv binary from the official uv image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Set environment variables for uv best practices
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_TOOL_BIN_DIR=/usr/local/bin

# Copy lock file and project files for caching
COPY pyproject.toml uv.lock ./

# Install dependencies into a virtual environment using cache mounts
# This layer is cached as long as pyproject.toml or uv.lock don't change
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Stage 2: Runtime stage
FROM python:3.12-slim AS runtime

# Set the working directory
WORKDIR /app

# Copy the installed venv from the build stage
COPY --from=build /app/.venv /app/.venv

# Copy the application source code
COPY . /app

# Ensure the virtual environment executables are on the PATH
ENV PATH="/app/.venv/bin:$PATH"

# Use a non-root user for security (optional but recommended)
RUN groupadd --system --gid 999 nonroot && useradd --system --gid 999 --uid 999 --create-home nonroot
USER nonroot

# Command to run the application (e.g., a FastAPI application)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
