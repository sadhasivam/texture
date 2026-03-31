.PHONY: generate generate-go generate-python lint format breaking clean

# Generate code for both Go and Python
generate: generate-go generate-python
	@echo "✓ Generated protobuf files for Go and Python"

# Generate Go code using Buf with local plugins
generate-go:
	@echo "Generating Go protobuf code with Buf..."
	@mkdir -p ../Loom/pb
	@buf generate
	@echo "✓ Generated Go protobuf files"

# Generate Python code using grpcio-tools (.venv)
generate-python:
	@echo "Generating Python protobuf code with grpcio-tools..."
	@mkdir -p ../Weaver/app/pb
	@../Weaver/.venv/bin/python -m grpc_tools.protoc \
		-I. \
		--python_out=../Weaver/app/pb \
		--grpc_python_out=../Weaver/app/pb \
		--pyi_out=../Weaver/app/pb \
		*.proto
	@echo "Fixing Python imports to be relative..."
	@sed -i '' 's/^import weaver_pb2/from . import weaver_pb2/g' ../Weaver/app/pb/weaver_pb2_grpc.py
	@sed -i '' 's/^import common_pb2/from . import common_pb2/g' ../Weaver/app/pb/weaver_pb2.py ../Weaver/app/pb/weaver_pb2_grpc.py
	@echo "✓ Generated Python protobuf files"

# Lint protobuf files
lint:
	@echo "Linting protobuf files..."
	@buf lint
	@echo "✓ Lint passed"

# Format protobuf files
format:
	@echo "Formatting protobuf files..."
	@buf format -w
	@echo "✓ Formatted"

# Check for breaking changes
breaking:
	@echo "Checking for breaking changes..."
	@buf breaking --against '.git#branch=main'
	@echo "✓ No breaking changes detected"

# Legacy targets (for backward compatibility)
generate-go: generate
generate-python: generate

clean:
	@echo "Cleaning generated protobuf files..."
	@rm -rf ../Loom/pb/*
	@find ../Weaver/app/pb -type f -name '*_pb2.py' -delete
	@find ../Weaver/app/pb -type f -name '*_pb2.pyi' -delete
	@find ../Weaver/app/pb -type f -name '*_pb2_grpc.py' -delete
	@echo "✓ Cleaned"
