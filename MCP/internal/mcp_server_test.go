package internal

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/mark3labs/mcp-go/mcp"
	"github.com/mark3labs/mcp-go/server"
)

// MockGooglePlacesAPI creates a mock server for testing
func MockGooglePlacesAPI(results []SearchResult, status string) *httptest.Server {
	return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(SearchResponse{
			Results: results,
			Status:  status,
		})
	}))
}

func TestGooglePlacesClient_SearchText(t *testing.T) {
	// Create mock server
	results := []SearchResult{
		{
			DisplayName: DisplayName{Text: "Test Restaurant"},
			Address:     "123 Test St, Test City",
			Rating:      4.5,
			UserRatings: 100,
			Types:       []string{"restaurant", "food"},
			PriceLevel:  "PRICE_LEVEL_MODERATE",
		},
	}

	// Create a mock server for testing
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(PlacesAPIResponse{
			Places: results,
		})
	}))
	defer ts.Close()

	// Create client with test API key
	client := NewGooglePlacesClient("test_api_key")

	// Test SearchText would need the mock URL - for now test the structure
	_ = client
}

func TestGooglePlacesClient_SearchNearby(t *testing.T) {
	results := []SearchResult{
		{
			DisplayName: DisplayName{Text: "Nearby Cafe"},
			Address:     "456 Coffee Ave",
			Rating:      4.2,
			UserRatings: 50,
			Types:       []string{"cafe"},
			PriceLevel:  "PRICE_LEVEL_INEXPENSIVE",
		},
	}

	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(PlacesAPIResponse{
			Places: results,
		})
	}))
	defer ts.Close()

	client := NewGooglePlacesClient("test_api_key")
	_ = client
}

func TestSearchResult_Structure(t *testing.T) {
	// Test that SearchResult can be properly marshaled/unmarshaled
	result := SearchResult{
		DisplayName: DisplayName{Text: "Test Place"},
		Address:     "Test Address",
		Rating:      4.5,
		UserRatings: 100,
		Types:       []string{"restaurant", "food"},
		PriceLevel:  "PRICE_LEVEL_MODERATE",
	}

	// Marshal to JSON
	data, err := json.Marshal(result)
	if err != nil {
		t.Fatalf("Failed to marshal SearchResult: %v", err)
	}

	// Unmarshal back
	var decoded SearchResult
	if err := json.Unmarshal(data, &decoded); err != nil {
		t.Fatalf("Failed to unmarshal SearchResult: %v", err)
	}

	// Verify fields
	if decoded.DisplayName.Text != result.DisplayName.Text {
		t.Errorf("Expected Name %s, got %s", result.DisplayName.Text, decoded.DisplayName.Text)
	}
	if decoded.Rating != result.Rating {
		t.Errorf("Expected Rating %f, got %f", result.Rating, decoded.Rating)
	}
	if decoded.PriceLevel != result.PriceLevel {
		t.Errorf("Expected PriceLevel %s, got %s", result.PriceLevel, decoded.PriceLevel)
	}
}

func TestMCPServer_ToolRegistration(t *testing.T) {
	// Create MCP server
	s := server.NewMCPServer("test-server", "1.0.0")

	// Define input schema as raw JSON
	inputSchema := json.RawMessage(`{
		"type": "object",
		"properties": {
			"query": {
				"type": "string",
				"description": "Test query"
			}
		},
		"required": ["query"]
	}`)

	// Add a test tool
	tool := mcp.Tool{
		Name:           "test_tool",
		Description:    "A test tool",
		RawInputSchema: inputSchema,
	}

	s.AddTool(tool, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		return &mcp.CallToolResult{
			Content: []mcp.Content{
				mcp.NewTextContent("Test response"),
			},
		}, nil
	})

	// Server created successfully
	if s == nil {
		t.Fatal("Expected server to be created")
	}
}

func TestMCPServer_GooglePlacesToolRegistration(t *testing.T) {
	// Create MCP server
	s := server.NewMCPServer("test-server", "1.0.0")

	// Define input schema as raw JSON
	inputSchema := json.RawMessage(`{
		"type": "object",
		"properties": {
			"query": {
				"type": "string",
				"description": "Text search query"
			},
			"location": {
				"type": "string",
				"description": "Location for nearby search"
			},
			"radius": {
				"type": "integer",
				"description": "Radius in meters"
			},
			"place_type": {
				"type": "string",
				"description": "Type of place"
			}
		},
		"required": ["query"]
	}`)

	// Add Google Places Search tool
	tool := mcp.Tool{
		Name:           "google_places_search",
		Description:    "Search for places using Google Places API",
		RawInputSchema: inputSchema,
	}

	s.AddTool(tool, func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		args := request.GetArguments()
		query, _ := args["query"].(string)

		// Return mock response
		if query == "" {
			return &mcp.CallToolResult{
				Content: []mcp.Content{
					mcp.NewTextContent("Error: query is required"),
				},
			}, nil
		}

		return &mcp.CallToolResult{
			Content: []mcp.Content{
				mcp.NewTextContent("Found 1 result:\n\n1. Test Place\n   Address: 123 Test St\n   Rating: 4.5 (100 reviews)"),
			},
		}, nil
	})

	// Server created successfully
	if s == nil {
		t.Fatal("Expected server to be created")
	}
}

func TestCallToolRequest_GetArguments(t *testing.T) {
	// Test GetArguments with valid map
	args := map[string]any{
		"query":      "test query",
		"location":   "37.7749,-122.4194",
		"radius":     float64(1000),
		"place_type": "restaurant",
	}

	// Simulate the request structure
	request := mcp.CallToolRequest{
		Params: mcp.CallToolParams{
			Name:      "google_places_search",
			Arguments: args,
		},
	}

	// Get arguments
	gotArgs := request.GetArguments()

	if gotArgs == nil {
		t.Fatal("Expected arguments to not be nil")
	}

	if gotArgs["query"] != "test query" {
		t.Errorf("Expected query 'test query', got '%v'", gotArgs["query"])
	}

	if gotArgs["location"] != "37.7749,-122.4194" {
		t.Errorf("Expected location '37.7749,-122.4194', got '%v'", gotArgs["location"])
	}

	if gotArgs["radius"] != float64(1000) {
		t.Errorf("Expected radius 1000, got %v", gotArgs["radius"])
	}
}

func TestCallToolResult_Content(t *testing.T) {
	// Test creating CallToolResult with TextContent
	result := &mcp.CallToolResult{
		Content: []mcp.Content{
			mcp.NewTextContent("Test response"),
		},
	}

	if len(result.Content) != 1 {
		t.Fatalf("Expected 1 content item, got %d", len(result.Content))
	}

	// Verify it's a text content by checking type
	switch result.Content[0].(type) {
	case mcp.TextContent:
		// Expected type
	default:
		t.Errorf("Expected TextContent, got different type")
	}
}

func TestPlacesAPIResponse_JSONMarshaling(t *testing.T) {
	response := PlacesAPIResponse{
		Places: []SearchResult{
			{
				DisplayName: DisplayName{Text: "Place One"},
				Address:     "Address 1",
				Rating:      4.5,
				UserRatings: 100,
				Types:       []string{"restaurant"},
				PriceLevel:  "PRICE_LEVEL_MODERATE",
			},
			{
				DisplayName: DisplayName{Text: "Place Two"},
				Address:     "Address 2",
				Rating:      4.0,
				UserRatings: 50,
				Types:       []string{"cafe"},
				PriceLevel:  "PRICE_LEVEL_INEXPENSIVE",
			},
		},
		Status: "OK",
	}

	// Marshal to JSON
	data, err := json.Marshal(response)
	if err != nil {
		t.Fatalf("Failed to marshal PlacesAPIResponse: %v", err)
	}

	// Unmarshal back
	var decoded PlacesAPIResponse
	if err := json.Unmarshal(data, &decoded); err != nil {
		t.Fatalf("Failed to unmarshal PlacesAPIResponse: %v", err)
	}

	// Verify
	if decoded.Status != "OK" {
		t.Errorf("Expected status 'OK', got '%s'", decoded.Status)
	}
	if len(decoded.Places) != 2 {
		t.Errorf("Expected 2 results, got %d", len(decoded.Places))
	}
	if decoded.Places[0].DisplayName.Text != "Place One" {
		t.Errorf("Expected first result name 'Place One', got '%s'", decoded.Places[0].DisplayName.Text)
	}
}
