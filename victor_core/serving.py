"""
Model Serving Infrastructure
==============================

REST API server for deploying Victor AGI models to production.

Provides HTTP endpoints for model inference, health checks, and metrics.

Author: Brandon Emery x Victor
License: Proprietary - Massive Magnetics
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading


@dataclass
class ModelMetadata:
    """
    Model metadata for serving.
    
    Attributes:
        name: Model name
        version: Model version
        input_shape: Expected input shape
        output_shape: Expected output shape
        description: Model description
    """
    name: str
    version: str
    input_shape: tuple
    output_shape: tuple
    description: str = ""


@dataclass
class ServingStats:
    """
    Serving statistics.
    
    Attributes:
        total_requests: Total number of requests
        successful_requests: Number of successful requests
        failed_requests: Number of failed requests
        total_latency: Total processing time (seconds)
        start_time: Server start time
    """
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_latency: float = 0.0
    start_time: float = field(default_factory=time.time)
    
    @property
    def avg_latency(self) -> float:
        """Average request latency."""
        if self.successful_requests == 0:
            return 0.0
        return self.total_latency / self.successful_requests
    
    @property
    def uptime(self) -> float:
        """Server uptime in seconds."""
        return time.time() - self.start_time
    
    @property
    def success_rate(self) -> float:
        """Request success rate."""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests


class ModelServer:
    """
    HTTP server for model inference.
    
    Provides REST API endpoints for:
    - POST /predict - Model inference
    - GET /health - Health check
    - GET /metrics - Performance metrics
    - GET /metadata - Model metadata
    
    Example:
        >>> from victor_core.serving import ModelServer
        >>> 
        >>> def predict_fn(inputs):
        ...     # Your model inference logic
        ...     return {"predictions": inputs["data"] * 2}
        >>> 
        >>> metadata = ModelMetadata(
        ...     name="my_model",
        ...     version="v1.0.0",
        ...     input_shape=(None, 10),
        ...     output_shape=(None, 1)
        ... )
        >>> 
        >>> server = ModelServer(predict_fn, metadata, port=8080)
        >>> server.start()
    """
    
    def __init__(
        self,
        predict_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
        metadata: ModelMetadata,
        host: str = "0.0.0.0",
        port: int = 8080
    ):
        """
        Initialize model server.
        
        Args:
            predict_fn: Function that takes inputs dict and returns predictions dict
            metadata: Model metadata
            host: Server host (default: 0.0.0.0)
            port: Server port (default: 8080)
        """
        self.predict_fn = predict_fn
        self.metadata = metadata
        self.host = host
        self.port = port
        self.stats = ServingStats()
        self.server = None
        self.server_thread = None
        
    def start(self, blocking: bool = True) -> None:
        """
        Start the server.
        
        Args:
            blocking: If True, blocks until server stops. If False, runs in background thread.
        """
        handler = self._create_request_handler()
        self.server = HTTPServer((self.host, self.port), handler)
        
        print(f"Model server starting on http://{self.host}:{self.port}")
        print(f"Model: {self.metadata.name} {self.metadata.version}")
        print(f"Endpoints: /predict, /health, /metrics, /metadata")
        
        if blocking:
            self.server.serve_forever()
        else:
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
    
    def stop(self) -> None:
        """Stop the server."""
        if self.server:
            self.server.shutdown()
            print("Model server stopped")
    
    def _create_request_handler(self):
        """Create HTTP request handler class."""
        # Capture self reference for handler
        server_instance = self
        
        class RequestHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                """Override to suppress request logging."""
                pass
            
            def do_GET(self):
                """Handle GET requests."""
                parsed_path = urlparse(self.path)
                path = parsed_path.path
                
                if path == "/health":
                    self._handle_health()
                elif path == "/metrics":
                    self._handle_metrics()
                elif path == "/metadata":
                    self._handle_metadata()
                else:
                    self._send_error(404, "Endpoint not found")
            
            def do_POST(self):
                """Handle POST requests."""
                parsed_path = urlparse(self.path)
                path = parsed_path.path
                
                if path == "/predict":
                    self._handle_predict()
                else:
                    self._send_error(404, "Endpoint not found")
            
            def _handle_health(self):
                """Health check endpoint."""
                response = {
                    "status": "healthy",
                    "model": server_instance.metadata.name,
                    "version": server_instance.metadata.version,
                    "uptime": server_instance.stats.uptime
                }
                self._send_json_response(200, response)
            
            def _handle_metrics(self):
                """Metrics endpoint."""
                response = {
                    "total_requests": server_instance.stats.total_requests,
                    "successful_requests": server_instance.stats.successful_requests,
                    "failed_requests": server_instance.stats.failed_requests,
                    "success_rate": server_instance.stats.success_rate,
                    "avg_latency": server_instance.stats.avg_latency,
                    "uptime": server_instance.stats.uptime
                }
                self._send_json_response(200, response)
            
            def _handle_metadata(self):
                """Metadata endpoint."""
                response = {
                    "name": server_instance.metadata.name,
                    "version": server_instance.metadata.version,
                    "input_shape": list(server_instance.metadata.input_shape),
                    "output_shape": list(server_instance.metadata.output_shape),
                    "description": server_instance.metadata.description
                }
                self._send_json_response(200, response)
            
            def _handle_predict(self):
                """Prediction endpoint."""
                server_instance.stats.total_requests += 1
                start_time = time.time()
                
                try:
                    # Read request body
                    content_length = int(self.headers['Content-Length'])
                    body = self.rfile.read(content_length)
                    inputs = json.loads(body.decode('utf-8'))
                    
                    # Run prediction
                    predictions = server_instance.predict_fn(inputs)
                    
                    # Update stats
                    latency = time.time() - start_time
                    server_instance.stats.successful_requests += 1
                    server_instance.stats.total_latency += latency
                    
                    # Send response
                    response = {
                        "predictions": predictions,
                        "latency": latency
                    }
                    self._send_json_response(200, response)
                    
                except Exception as e:
                    server_instance.stats.failed_requests += 1
                    self._send_error(500, str(e))
            
            def _send_json_response(self, status_code, data):
                """Send JSON response."""
                self.send_response(status_code)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode('utf-8'))
            
            def _send_error(self, status_code, message):
                """Send error response."""
                response = {"error": message}
                self._send_json_response(status_code, response)
        
        return RequestHandler


def serve_model(
    predict_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
    metadata: ModelMetadata,
    port: int = 8080
) -> ModelServer:
    """
    Quick utility to serve a model.
    
    Args:
        predict_fn: Prediction function
        metadata: Model metadata
        port: Server port
        
    Returns:
        ModelServer instance (already started in background)
        
    Example:
        >>> def my_predict(inputs):
        ...     return {"result": inputs["x"] * 2}
        >>> 
        >>> metadata = ModelMetadata("my_model", "v1", (1,), (1,))
        >>> server = serve_model(my_predict, metadata, port=8000)
        >>> # Server running in background
        >>> # ... do other work ...
        >>> server.stop()
    """
    server = ModelServer(predict_fn, metadata, port=port)
    server.start(blocking=False)
    return server
