# Stage 1: Build Stage
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Copy requirements.txt to install dependencies
COPY requirements.txt .

# Install dependencies in a virtual environment
RUN python -m venv /opt/venv \
    && . /opt/venv/bin/activate \
    && pip install --no-cache-dir -r requirements.txt

# Stage 2: Production Stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy the rest of the application code
COPY . .

# Expose port 8000
EXPOSE 8000

#  Run the start script
ENTRYPOINT [ "./start.sh" ]

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
