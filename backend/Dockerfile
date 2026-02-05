FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

# requirements-dev.txt is for dev and includes pytest and other tests
# requirements.txt is for prod
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

