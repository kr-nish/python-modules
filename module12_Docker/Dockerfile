FROM python:3.12-slim AS builder

RUN apt-get update && apy-get install -y \
    gcc \
    & rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# stage 2
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

EXPOSE 8080

CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]