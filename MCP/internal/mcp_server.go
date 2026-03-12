package internal

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"

	"github.com/mark3labs/mcp-go/mcp"
	"github.com/mark3labs/mcp-go/server"
)

// GooglePlacesClient handles Google Places API requests
type GooglePlacesClient struct {
	APIKey string
}

// NewGooglePlacesClient creates a new Google Places API client
func NewGooglePlacesClient(apiKey string) *GooglePlacesClient {
	return &GooglePlacesClient{APIKey: apiKey}
}

// DisplayName represents the display name object from the API
type DisplayName struct {
	Text         string `json:"text,omitempty"`
	LanguageCode string `json:"languageCode,omitempty"`
}

// SearchResult represents a place search result from the new Places API
type SearchResult struct {
	DisplayName DisplayName `json:"displayName"`
	Address     string      `json:"formattedAddress,omitempty"`
	Rating      float64     `json:"rating,omitempty"`
	UserRatings int         `json:"userRatingCount,omitempty"`
	Types       []string    `json:"types,omitempty"`
	PriceLevel  string      `json:"priceLevel,omitempty"`
}

// UnmarshalJSON handles custom unmarshaling for SearchResult
func (s *SearchResult) UnmarshalJSON(data []byte) error {
	var raw struct {
		DisplayName DisplayName `json:"displayName"`
		Address     string      `json:"formattedAddress"`
		Rating      float64     `json:"rating"`
		UserRatings int         `json:"userRatingCount"`
		Types       []string    `json:"types"`
		PriceLevel  string      `json:"priceLevel"`
	}

	if err := json.Unmarshal(data, &raw); err != nil {
		return err
	}

	s.DisplayName = raw.DisplayName
	s.Address = raw.Address
	s.Rating = raw.Rating
	s.UserRatings = raw.UserRatings
	s.Types = raw.Types
	s.PriceLevel = raw.PriceLevel

	return nil
}

// PlacesAPIResponse represents the new Places API response
type PlacesAPIResponse struct {
	Places []SearchResult `json:"places,omitempty"`
	Status string         `json:"status,omitempty"`
}

// SearchResponse represents the old API response (for backward compatibility)
type SearchResponse struct {
	Results []SearchResult `json:"results"`
	Status  string         `json:"status"`
}

// SearchText searches for places using the new Google Places API (v1)
func (c *GooglePlacesClient) SearchText(query string) ([]SearchResult, error) {
	url := "https://places.googleapis.com/v1/places:searchText"

	// Request body
	body := map[string]interface{}{
		"textQuery": query,
	}
	bodyBytes, err := json.Marshal(body)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

	req, err := http.NewRequest("POST", url, bytes.NewReader(bodyBytes))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-Goog-Api-Key", c.APIKey)
	req.Header.Set("X-Goog-FieldMask", "places.displayName,places.formattedAddress,places.rating,places.userRatingCount,places.types,places.priceLevel")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to make request: %w", err)
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	// Check if response is HTML (error page) instead of JSON
	if len(respBody) > 0 && respBody[0] == '<' {
		return nil, fmt.Errorf("API returned HTML error page: %s", string(respBody[:min(200, len(respBody))]))
	}

	var apiResp struct {
		Places []struct {
			DisplayName DisplayName `json:"displayName"`
			Address     string      `json:"formattedAddress"`
			Rating      float64     `json:"rating"`
			UserRatings int         `json:"userRatingCount"`
			Types       []string    `json:"types"`
			PriceLevel  string      `json:"priceLevel"`
		} `json:"places"`
	}
	if err := json.Unmarshal(respBody, &apiResp); err != nil {
		return nil, fmt.Errorf("failed to parse response: %w - raw response: %s", err, string(respBody[:min(200, len(respBody))]))
	}

	// Transform response to our format
	results := make([]SearchResult, 0, len(apiResp.Places))
	for _, place := range apiResp.Places {
		results = append(results, SearchResult{
			DisplayName: place.DisplayName,
			Address:     place.Address,
			Rating:      place.Rating,
			UserRatings: place.UserRatings,
			Types:       place.Types,
			PriceLevel:  place.PriceLevel,
		})
	}

	return results, nil
}

// SearchNearby searches for places near a location using the new Google Places API (v1)
func (c *GooglePlacesClient) SearchNearby(location string, radius int, placeType string) ([]SearchResult, error) {
	url := "https://places.googleapis.com/v1/places:searchNearby"

	// Parse location
	var lat, lng float64
	_, err := fmt.Sscanf(location, "%f,%f", &lat, &lng)
	if err != nil {
		return nil, fmt.Errorf("invalid location format, expected 'lat,lng': %w", err)
	}

	// Request body
	body := map[string]interface{}{
		"locationRestriction": map[string]interface{}{
			"circle": map[string]interface{}{
				"center": map[string]interface{}{
					"latitude":  lat,
					"longitude": lng,
				},
				"radius": radius,
			},
		},
	}

	if placeType != "" {
		body["includedType"] = placeType
	}

	bodyBytes, err := json.Marshal(body)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

	req, err := http.NewRequest("POST", url, bytes.NewReader(bodyBytes))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-Goog-Api-Key", c.APIKey)
	req.Header.Set("X-Goog-FieldMask", "places.displayName,places.formattedAddress,places.rating,places.userRatingCount,places.types,places.priceLevel")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to make request: %w", err)
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	// Check if response is HTML (error page) instead of JSON
	if len(respBody) > 0 && respBody[0] == '<' {
		return nil, fmt.Errorf("API returned HTML error page: %s", string(respBody[:min(200, len(respBody))]))
	}

	var apiResp struct {
		Places []struct {
			DisplayName DisplayName `json:"displayName"`
			Address     string      `json:"formattedAddress"`
			Rating      float64     `json:"rating"`
			UserRatings int         `json:"userRatingCount"`
			Types       []string    `json:"types"`
			PriceLevel  string      `json:"priceLevel"`
		} `json:"places"`
	}
	if err := json.Unmarshal(respBody, &apiResp); err != nil {
		return nil, fmt.Errorf("failed to parse response: %w - raw response: %s", err, string(respBody[:min(200, len(respBody))]))
	}

	// Transform response to our format
	results := make([]SearchResult, 0, len(apiResp.Places))
	for _, place := range apiResp.Places {
		results = append(results, SearchResult{
			DisplayName: place.DisplayName,
			Address:     place.Address,
			Rating:      place.Rating,
			UserRatings: place.UserRatings,
			Types:       place.Types,
			PriceLevel:  place.PriceLevel,
		})
	}

	return results, nil
}

// min returns the minimum of two integers
func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// MCPServer creates and configures the MCP server
func MCPServer(configPath string) *server.MCPServer {
	s := server.NewMCPServer(
		"mcp-google-places",
		"1.0.0",
	)

	// Define input schema as raw JSON
	inputSchema := json.RawMessage(`{
		"type": "object",
		"properties": {
			"query": {
				"type": "string",
				"description": "Text search query (e.g., 'Italian restaurant in New York')"
			},
			"location": {
				"type": "string",
				"description": "Location for nearby search in format 'latitude,longitude' (e.g., '40.7128,-74.0060')"
			},
			"radius": {
				"type": "integer",
				"description": "Radius for nearby search in meters (default: 1000)",
				"default": 1000
			},
			"place_type": {
				"type": "string",
				"description": "Type of place to search for (e.g., 'restaurant', 'cafe', 'hospital')",
				"default": "restaurant"
			}
		},
		"required": ["query"]
	}`)

	// Add Google Places Search tool
	tool := mcp.Tool{
		Name: "google_places_search",
		Description: `Search for places using Google Places API.
You can search by:
- Text query (e.g., "restaurants in San Francisco")
- Nearby search with location coordinates

Returns place details including name, address, rating, and location.`,
		RawInputSchema: inputSchema,
	}

	s.AddTool(tool, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		// Try to get API key from config first, then fall back to environment variable
		apiKey, apiErr := GetAPIKey(configPath)
		if apiErr != nil {
			return &mcp.CallToolResult{
				Content: []mcp.Content{
					mcp.NewTextContent(fmt.Sprintf("Error: %v\n\nTo resolve:\n  1. Set GOOGLE_API_KEY environment variable\n  2. Or create a config file at ~/.mcp-google-places/config.yaml", apiErr)),
				},
			}, nil
		}

		client := NewGooglePlacesClient(apiKey)

		args := request.GetArguments()
		query, _ := args["query"].(string)
		location, _ := args["location"].(string)
		radius := 1000
		placeType := "restaurant"

		if r, ok := args["radius"].(float64); ok {
			radius = int(r)
		}
		if pt, ok := args["place_type"].(string); ok {
			placeType = pt
		}

		var results []SearchResult
		var searchErr error

		// Use nearby search if location is provided, otherwise use text search
		if location != "" {
			results, searchErr = client.SearchNearby(location, radius, placeType)
		} else {
			results, searchErr = client.SearchText(query)
		}

		if searchErr != nil {
			return &mcp.CallToolResult{
				Content: []mcp.Content{
					mcp.NewTextContent(fmt.Sprintf("Error: %v", searchErr)),
				},
			}, nil
		}

		if len(results) == 0 {
			return &mcp.CallToolResult{
				Content: []mcp.Content{
					mcp.NewTextContent("No results found"),
				},
			}, nil
		}

		// Format results
		var output strings.Builder
		output.WriteString(fmt.Sprintf("Found %d results:\n\n", len(results)))

		for _, r := range results {
			output.WriteString(fmt.Sprintf("Name  %s\n", r.DisplayName.Text))
			output.WriteString(fmt.Sprintf("   Address: %s\n", r.Address))
			if r.Rating > 0 {
				output.WriteString(fmt.Sprintf("   Rating: %.1f (%d reviews)\n", r.Rating, r.UserRatings))
			}
			if r.PriceLevel != "" {
				output.WriteString(fmt.Sprintf("   Price Level: %s\n", r.PriceLevel))
			}
			output.WriteString("\n")
		}

		return &mcp.CallToolResult{
			Content: []mcp.Content{
				mcp.NewTextContent(output.String()),
			},
		}, nil
	})

	return s
}
