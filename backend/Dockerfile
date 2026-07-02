# Build a small Python runtime image for the FastAPI service.
FROM python:3.11-slim AS runtime

WORKDIR /app

# Install dependencies before source code so Docker can cache this expensive layer.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and data scripts into the container.
COPY app ./app
COPY data ./data

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
