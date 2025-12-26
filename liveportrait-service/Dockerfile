# Placeholder Dockerfile for LivePortrait service
# TODO: Implement LivePortrait service container
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install fastapi uvicorn

# Copy service code (to be implemented)
COPY . /app

EXPOSE 8002

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]

