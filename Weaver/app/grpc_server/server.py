"""gRPC server for Weaver compute service."""

import logging
from concurrent import futures

import grpc

from app.grpc_server.handlers import WeaverServiceHandler
from app.pb import weaver_pb2_grpc
from app.services.spec_registry import spec_registry

logger = logging.getLogger(__name__)


def serve(port: int = 50051):
    """Start the gRPC server."""
    # Auto-discover algorithms
    logger.info("Loading algorithms from YAML specs...")
    spec_registry.auto_discover_and_register()
    algorithms = spec_registry.get_all_summaries()
    logger.info(f"Loaded {len(algorithms)} algorithms")

    # Create gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Add service handler
    weaver_pb2_grpc.add_WeaverServiceServicer_to_server(WeaverServiceHandler(), server)

    # Listen on port
    server.add_insecure_port(f"[::]:{port}")

    logger.info(f"Starting Weaver gRPC server on port {port}")
    server.start()

    return server


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server = serve()
    server.wait_for_termination()
