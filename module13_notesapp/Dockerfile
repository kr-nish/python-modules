#Stage 1  : builder (deps + migration)
FROM python:3.12-slim AS builder

ARG FLASK_ENV=dev
ENV FLASK_ENV=$FLASK_ENV

WORKDIR /app
COPY . .
RUN apt-get update && apt-get install -y gcc postgresql-client && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y gcc & rm -rf /var/lib/apt/lists/*

COPY . .
# # COPY migrate.py .
# # RUN python migrate.py 

#stage 2

FROM builder AS tester
COPY test_app.py .
RUN pytest test_app.py -v 

# stage 3
FROM builder AS runtime
WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . /app
COPY ./app.py /app/

RUN groupadd -r appuser && useradd -r -g appuser appuser && \
    pip install --no-cache-dir -r requirements.txt && \
    chown -R appuser:appuser /app && \
    mkdir -p /app/data && chown appuser:appuser /app/data

USER appuser

EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

CMD ["python", "app.py"]

