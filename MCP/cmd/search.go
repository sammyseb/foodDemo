package cmd

import (
	"fmt"
	"os"

	"mcp-google-places/internal"

	"github.com/spf13/cobra"
)

var (
	searchLocation  string
	searchRadius    int
	searchPlaceType string
)

var searchCmd = &cobra.Command{
	Use:   "search [query]",
	Short: "Search for places using Google Places API",
	Long: `Search for places using Google Places API.
Provide a text query to search for places.

Examples:
  mcp-google-places search "restaurants in San Francisco"
  mcp-google-places search "coffee shop" --location "37.7749,-122.4194" --radius 5000`,
	Args: cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		// Get API key from config or environment
		apiKey, err := internal.GetAPIKey(configPath)
		if err != nil {
			fmt.Fprintln(os.Stderr, "Error:", err)
			fmt.Fprintln(os.Stderr, "\nTo resolve:")
			fmt.Fprintln(os.Stderr, "  1. Set GOOGLE_API_KEY environment variable:")
			fmt.Fprintln(os.Stderr, "     export GOOGLE_API_KEY=your_api_key")
			fmt.Fprintln(os.Stderr, "  2. Or create a config file at ~/.mcp-google-places/config.yaml with:")
			fmt.Fprintln(os.Stderr, "     google_api_key: your_api_key")
			os.Exit(1)
		}

		client := internal.NewGooglePlacesClient(apiKey)
		query := args[0]

		var results []internal.SearchResult
		var searchErr error

		if searchLocation != "" {
			results, searchErr = client.SearchNearby(searchLocation, searchRadius, searchPlaceType)
		} else {
			results, searchErr = client.SearchText(query)
		}

		if searchErr != nil {
			fmt.Fprintf(os.Stderr, "Error: %v\n", searchErr)
			os.Exit(1)
		}

		if len(results) == 0 {
			fmt.Println("No results found")
			return
		}

		fmt.Printf("Found %d results:\n\n", len(results))

		for _, r := range results {
			fmt.Printf("Name: %s\n", r.DisplayName.Text)
			fmt.Printf("   Address: %s\n", r.Address)
			if r.Rating > 0 {
				fmt.Printf("   Rating: %.1f (%d reviews)\n", r.Rating, r.UserRatings)
			}
			if r.PriceLevel != "" {
				fmt.Printf("   Price Level: %s\n", r.PriceLevel)
			}
		}
	},
}

func init() {
	searchCmd.Flags().StringVarP(&searchLocation, "location", "l", "", "Location in 'lat,lng' format for nearby search")
	searchCmd.Flags().IntVarP(&searchRadius, "radius", "r", 1000, "Radius in meters for nearby search")
	searchCmd.Flags().StringVarP(&searchPlaceType, "type", "t", "restaurant", "Place type for nearby search")
	RootCmd.AddCommand(searchCmd)
}
