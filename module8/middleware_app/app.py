from flask import Flask, jsonify, request
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
import time, cProfile, io, pstats

app = Flask(__name__)
 
# Setup OpenTelemetry for tracing
trace.set_tracer_provider(
    TracerProvider(resource=Resource.create({"service.name": "flask-app"}))
)
tracer = trace.get_tracer(__name__)

# Export traces to Jaeger (via OTLP)
otlp_exporter = OTLPSpanExporter(endpoint="http://jaeger:4317", insecure=True)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))

# Also print traces to console (optional for debugging)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

# Auto instrumentation
FlaskInstrumentor().instrument_app(app)

@app.before_request
def start_profiler():
    request.profiler = cProfile.Profile()
    request.profiler.enable()

@app.after_request
def stop_profiler(response):
    request.profiler.disable()
    s = io.StringIO()
    ps = pstats.Stats(request.profiler, stream=s).sort_stats("cumulative")
    ps.print_stats(10)
    print("\n__Profiling_REPORT----\n", s.getvalue())
    return response
    


@app.route("/process", methods=["GET"])
def process_data():
    with tracer.start_as_current_span("data_processing"):
        import time; time.sleep(0.5)
        return jsonify({"Message": "this took longer than expected"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True) 