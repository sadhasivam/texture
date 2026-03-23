"""Entry point for Weaver gRPC server."""

import logging
import os

from app.grpc_server.server import serve

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Extract port from WEAVER_GRPC_URL (format: "localhost:50051")
    grpc_url = os.getenv("WEAVER_GRPC_URL", "localhost:50051")
    port = int(grpc_url.split(":")[-1])

    server = serve(port=port)

    print(f"Weaver gRPC server running on {grpc_url}")
    print("Press Ctrl+C to stop")

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.stop(0)
