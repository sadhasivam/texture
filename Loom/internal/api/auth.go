package api

import (
	"context"
	"net/http"

	"github.com/danielgtaylor/huma/v2"
	"github.com/sadhasivam/texture/internal/middleware"
)

// AuthResponse represents the response from auth endpoints
type AuthResponse struct {
	Body struct {
		Message string            `json:"message" example:"Authentication successful"`
		User    *middleware.ClerkUser `json:"user,omitempty"`
	}
}

// LoginInput represents login request (handled by Clerk frontend SDK)
type LoginInput struct{}

// LogoutInput represents logout request
type LogoutInput struct{}

// RegisterAuthRoutes registers authentication-related routes
func RegisterAuthRoutes(api huma.API) {
	// GET /api/v1/auth/me - Get current user info
	huma.Register(api, huma.Operation{
		OperationID: "get-current-user",
		Method:      http.MethodGet,
		Path:        "/api/v1/auth/me",
		Summary:     "Get current authenticated user",
		Description: "Returns the current authenticated user's information",
		Tags:        []string{"Auth"},
	}, func(ctx context.Context, input *struct{}) (*AuthResponse, error) {
		user, ok := middleware.GetUser(ctx)
		if !ok {
			return nil, huma.Error401Unauthorized("User not authenticated")
		}

		resp := &AuthResponse{}
		resp.Body.Message = "User authenticated"
		resp.Body.User = user
		return resp, nil
	})

	// POST /api/v1/auth/logout - Logout (invalidate session client-side)
	huma.Register(api, huma.Operation{
		OperationID: "logout",
		Method:      http.MethodPost,
		Path:        "/api/v1/auth/logout",
		Summary:     "Logout user",
		Description: "Invalidates the user's session (handled client-side with Clerk)",
		Tags:        []string{"Auth"},
	}, func(ctx context.Context, input *LogoutInput) (*AuthResponse, error) {
		// With Clerk, logout is primarily client-side
		// This endpoint just confirms the action
		resp := &AuthResponse{}
		resp.Body.Message = "Logout successful. Clear your session on the client side."
		return resp, nil
	})
}

// Note: Login is handled entirely by Clerk's frontend SDK
// The frontend will:
// 1. Use Clerk's <SignIn /> component or signIn() method
// 2. Receive a JWT token from Clerk
// 3. Include that token in Authorization header for subsequent requests
// 4. This backend verifies the JWT using ClerkAuth middleware
