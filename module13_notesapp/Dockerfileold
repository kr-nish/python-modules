#Stage 1 
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#stage 2

FROM python:3.12-slim
WORKDIR /app

ARG FLASK_ENV=dev
ENV FLASK_ENV=$FLASK_ENV

ENV NOTE_STORAGE_PATH=/app/data


COPY --from=builder /usr/local/lib/python3.12/site-packages  /usr/local/lib/python3.12/site-packages 
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .
RUN mkdir -p /app/data
EXPOSE 5000
CMD [ "python", "app.py" ]
