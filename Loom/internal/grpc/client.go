package grpc

import (
	"context"
	"fmt"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"

	"github.com/sadhasivam/texture/pb"
)

// Client wraps the gRPC client to Weaver
type Client struct {
	conn   *grpc.ClientConn
	client pb.WeaverServiceClient
}

// NewClient creates a new gRPC client to Weaver
func NewClient(weaverAddr string) (*Client, error) {
	// Connect to Weaver gRPC server
	conn, err := grpc.NewClient(
		weaverAddr,
		grpc.WithTransportCredentials(insecure.NewCredentials()),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to weaver: %w", err)
	}

	client := pb.NewWeaverServiceClient(conn)

	return &Client{
		conn:   conn,
		client: client,
	}, nil
}

// Close closes the gRPC connection
func (c *Client) Close() error {
	return c.conn.Close()
}

// HealthCheck checks if Weaver is healthy
func (c *Client) HealthCheck(ctx context.Context) (*pb.HealthResponse, error) {
	ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()

	resp, err := c.client.HealthCheck(ctx, &pb.Empty{})
	if err != nil {
		return nil, fmt.Errorf("health check failed: %w", err)
	}

	return resp, nil
}

// ValidateRun validates if a run can be executed
func (c *Client) ValidateRun(ctx context.Context, req *pb.ValidateRunRequest) (*pb.ValidateRunResponse, error) {
	ctx, cancel := context.WithTimeout(ctx, 10*time.Second)
	defer cancel()

	resp, err := c.client.ValidateRun(ctx, req)
	if err != nil {
		return nil, fmt.Errorf("validate run failed: %w", err)
	}

	return resp, nil
}

// ExecuteRun executes an algorithm run
func (c *Client) ExecuteRun(ctx context.Context, req *pb.ExecuteRunRequest) (*pb.ExecuteRunResponse, error) {
	// Longer timeout for ML computation
	ctx, cancel := context.WithTimeout(ctx, 120*time.Second)
	defer cancel()

	resp, err := c.client.ExecuteRun(ctx, req)
	if err != nil {
		return nil, fmt.Errorf("execute run failed: %w", err)
	}

	return resp, nil
}

// InferSchema infers schema from CSV data
func (c *Client) InferSchema(ctx context.Context, req *pb.InferSchemaRequest) (*pb.InferSchemaResponse, error) {
	ctx, cancel := context.WithTimeout(ctx, 30*time.Second)
	defer cancel()

	resp, err := c.client.InferSchema(ctx, req)
	if err != nil {
		return nil, fmt.Errorf("infer schema failed: %w", err)
	}

	return resp, nil
}
