"""Generated protobuf package.

This __init__.py ensures generated protobuf files can import each other correctly.
grpc_tools.protoc generates absolute imports (e.g., 'import common_pb2') instead
of relative imports (e.g., 'from . import common_pb2'), so we need to ensure the
pb directory is in the module search path.
"""

import sys
from pathlib import Path

# Add pb directory to sys.path so absolute imports work
_pb_dir = str(Path(__file__).parent)
if _pb_dir not in sys.path:
    sys.path.insert(0, _pb_dir)

# Import generated modules
try:
    from . import common_pb2, weaver_pb2, weaver_pb2_grpc
finally:
    # Clean up sys.path
    if _pb_dir in sys.path:
        sys.path.remove(_pb_dir)

__all__ = [
    "common_pb2",
    "weaver_pb2",
    "weaver_pb2_grpc",
]
