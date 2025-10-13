import time
import uuid
from flask import g, request


def request_logger_middleware(app):

    @app.before_request
    def start_timer():
        g.start_time = time.time()
        g.request_id = str(uuid.uuid4())
        print(f"[START] Request {g.request_id}: {request.method} {request.path}")

    @app.after_request
    def log_request(response):
        duration = time.time() - g.start_time
        print(f"[END] Request {g.request_id}: {request.method} {request.path} completed in {duration:.3f}s")
        response.headers["X-Request-ID"] = g.request_id
        response.headers["X-Request-Duration"] = f"{duration:.3f}s"
        return response
