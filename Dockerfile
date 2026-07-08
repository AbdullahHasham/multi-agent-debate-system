# Base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Prevent Python from generating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install standard API server (Uvicorn) and Streamlit
RUN pip install uvicorn streamlit

# Copy the rest of the code
COPY . .

# Expose the INTERNAL ports (Standard for Python apps)
EXPOSE 8000
EXPOSE 8501

# Default command
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]