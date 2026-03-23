package middleware

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
	"time"

	"github.com/clerk/clerk-sdk-go/v2/jwt"
)

type contextKey string

const UserContextKey contextKey = "user"

// CustomClaims represents the custom claims in the JWT template
type CustomClaims struct {
	Env    string `json:"env"`
	Email  string `json:"email"`
	UserID string `json:"user_id"`
}

// ClerkUser represents the authenticated user with custom claims
type ClerkUser struct {
	ID    string
	Email string
	Env   string // Custom claim: environment (development/production)
}

// ClerkAuth creates a middleware that verifies Clerk JWT tokens
// Uses custom JWT template with custom claims
func ClerkAuth() func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			// Extract token from Authorization header
			authHeader := r.Header.Get("Authorization")
			if authHeader == "" {
				writeError(w, http.StatusUnauthorized, "Missing authorization header")
				return
			}

			// Remove "Bearer " prefix
			token := strings.TrimPrefix(authHeader, "Bearer ")
			if token == authHeader {
				writeError(w, http.StatusUnauthorized, "Invalid authorization header format")
				return
			}

			// Verify the JWT token using Clerk's JWT verification with custom claims
			claims, err := jwt.Verify(r.Context(), &jwt.VerifyParams{
				Token: token,
				// Allow 5 seconds clock skew as configured in Clerk
				Leeway: 5 * time.Second,
				// Custom claims constructor for JWT template
				CustomClaimsConstructor: func(_ context.Context) any {
					return &CustomClaims{}
				},
			})
			if err != nil {
				writeError(w, http.StatusUnauthorized, fmt.Sprintf("Invalid token: %v", err))
				return
			}

			// Extract user info from standard claims
			user := &ClerkUser{
				ID: claims.Subject,
			}

			// Extract custom claims from the JWT template
			if customClaims, ok := claims.Custom.(*CustomClaims); ok && customClaims != nil {
				user.Email = customClaims.Email
				user.Env = customClaims.Env
			}

			// Add user to context
			ctx := context.WithValue(r.Context(), UserContextKey, user)
			next.ServeHTTP(w, r.WithContext(ctx))
		})
	}
}

// GetUser extracts the authenticated user from the context
func GetUser(ctx context.Context) (*ClerkUser, bool) {
	user, ok := ctx.Value(UserContextKey).(*ClerkUser)
	return user, ok
}

func writeError(w http.ResponseWriter, status int, message string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(map[string]string{
		"error": message,
	})
}
