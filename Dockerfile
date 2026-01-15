FROM python:3.12-slim

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory
WORKDIR /app

# Copy the project files
COPY . .

# Install dependencies using uv
# --frozen ensures we use exact versions from uv.lock
RUN uv sync --frozen

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Expose port 8000
EXPOSE 8000

# Run the FastAPI application
CMD ["fastapi", "run", "src/api/main.py", "--port", "8000", "--host", "0.0.0.0"]
