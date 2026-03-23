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
	cd ../Weaver && uv run python -m grpc_tools.protoc -I../proto --python_out=app/pb --grpc_python_out=app/pb ../proto/*.proto

# Generate both
generate: generate-go generate-python

clean:
	rm -rf ../Loom/pb/*
	rm -rf ../Weaver/app/pb/*
