from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
import os

resource = Resource(attributes={"service.name" :"notification-service"})

trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

exporter = OTLPSpanExporter(endpoint="http://jaeger:14000", insecure=True)
span_processor = BatchSpanProcessor(exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

def instrument_app(app):
    FastAPIInstrumentor.instrument_app(app)
    RedisInstrumentor().instrument()

def create_span(name: str, attributes: dict = None):
    with tracer.start_as_current_span(name, attributes=attributes):
        yield