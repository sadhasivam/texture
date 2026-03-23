package middleware

import (
	"net/http"
	"os"
	"strings"

	"github.com/go-chi/cors"
)

// CORS creates a CORS middleware configured from ALLOWED_ORIGINS env var
// If ALLOWED_ORIGINS is not set, defaults to same-origin only (no CORS)
func CORS() func(http.Handler) http.Handler {
	// Read ALLOWED_ORIGINS from environment
	allowedOriginsEnv := os.Getenv("ALLOWED_ORIGINS")

	var allowedOrigins []string
	if allowedOriginsEnv != "" {
		// Split by comma and trim whitespace
		for _, origin := range strings.Split(allowedOriginsEnv, ",") {
			origin = strings.TrimSpace(origin)
			if origin != "" {
				allowedOrigins = append(allowedOrigins, origin)
			}
		}
	} else {
		// If not set, default to same-origin only (empty list = no CORS)
		allowedOrigins = []string{}
	}

	return cors.Handler(cors.Options{
		AllowedOrigins: allowedOrigins,
		AllowedMethods: []string{
			"GET",
			"POST",
			"PUT",
			"PATCH",
			"DELETE",
			"OPTIONS",
		},
		AllowedHeaders: []string{
			"Accept",
			"Authorization",
			"Content-Type",
			"Content-Length",
			"X-CSRF-Token",
			"X-Requested-With",
		},
		ExposedHeaders: []string{
			"Link",
			"Content-Length",
			"Content-Type",
		},
		AllowCredentials: len(allowedOrigins) > 0 && allowedOrigins[0] != "*", // Only with specific origins
		MaxAge:           300, // Cache preflight requests for 5 minutes
	})
}
