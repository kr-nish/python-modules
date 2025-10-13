from flask import Flask, jsonify
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

app = Flask(__name__)
 
# Setup OpenTelemetry for tracing
trace.set_tracer_provider(
    TracerProvider(resource=Resource.create({"service.name": "flask-app"}))
)
tracer = trace.get_tracer(__name__)

# Export traces to Jaeger (via OTLP)
otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:14317", insecure=True)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))

# Also print traces to console (optional for debugging)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

# Auto instrumentation
FlaskInstrumentor().instrument_app(app)

@app.route("/process", methods=["GET"])
def process_data():
    with tracer.start_as_current_span("data_processing"):
        import time; time.sleep(2)
        return jsonify({"Message": "this took longer than expected"})

if __name__ == "__main__":
    app.run(debug=True)
