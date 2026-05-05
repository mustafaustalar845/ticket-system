FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
# We will copy the app package
COPY . /app/backend

# Change working directory so we can run it as a module
WORKDIR /app

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
