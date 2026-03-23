.PHONY: generate clean

# Generate Go code
generate-go:
	@echo "Generating Go protobuf code..."
	@mkdir -p ../Loom/pb
	protoc --go_out=../Loom/pb --go_opt=paths=source_relative \
		--go-grpc_out=../Loom/pb --go-grpc_opt=paths=source_relative \
		*.proto

# Generate Python code
generate-python:
	@echo "Generating Python protobuf code..."
	@mkdir -p ../Weaver/app/pb
	uv run --directory=../Weaver python -m grpc_tools.protoc \
		--proto_path=../proto \
		--python_out=app/pb \
		--grpc_python_out=app/pb \
		--pyi_out=app/pb \
		../proto/common.proto ../proto/weaver.proto
	@echo "Generated protobuf files successfully"

# Generate both
generate: generate-go generate-python

clean:
	rm -rf ../Loom/pb/*
	find ../Weaver/app/pb -type f -name '*_pb2.py' -delete
	find ../Weaver/app/pb -type f -name '*_pb2.pyi' -delete
	find ../Weaver/app/pb -type f -name '*_pb2_grpc.py' -delete
