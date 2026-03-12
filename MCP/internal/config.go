package internal

import (
	"fmt"
	"os"

	"github.com/spf13/viper"
)

// Config represents the application configuration
type Config struct {
	GoogleAPIKey string `mapstructure:"google_api_key"`
}

// LoadConfig loads configuration from file and environment variables
// Priority: CLI flag > Environment variable > Config file > Default
func LoadConfig(configPath string) (*Config, error) {
	v := viper.New()

	// Set default values
	v.SetDefault("google_api_key", "")

	// If config path is provided, use it
	if configPath != "" {
		v.SetConfigFile(configPath)
	} else {
		// Use default config file locations
		v.SetConfigName("mcp-google-places")
		v.SetConfigType("yaml")

		// Search in current directory and home directory
		v.AddConfigPath(".")
		v.AddConfigPath("$HOME/.mcp-google-places")
		v.AddConfigPath("$HOME/.config/mcp-google-places")
	}

	// Set environment variable prefix
	v.SetEnvPrefix("MCP_GOOGLE_PLACES")

	// Automatically bind environment variables
	v.BindEnv("google_api_key")

	// Read config file if it exists
	err := v.ReadInConfig()
	if err != nil {
		// Config file is optional, so we don't fail if it's not found
		if _, ok := err.(viper.ConfigFileNotFoundError); !ok {
			return nil, fmt.Errorf("error reading config file: %w", err)
		}
	}

	// Unmarshal configuration
	var config Config
	if err := v.Unmarshal(&config); err != nil {
		return nil, fmt.Errorf("error unmarshaling config: %w", err)
	}

	// Priority: Environment variable > Config file
	// If GOOGLE_API_KEY env var is set, it takes precedence
	if apiKey := os.Getenv("GOOGLE_API_KEY"); apiKey != "" {
		config.GoogleAPIKey = apiKey
	}

	return &config, nil
}

// GetAPIKey returns the Google API key, checking environment first, then config
func GetAPIKey(configPath string) (string, error) {
	// First check environment variable (highest priority)
	if apiKey := os.Getenv("GOOGLE_API_KEY"); apiKey != "" {
		return apiKey, nil
	}

	// Then check config file
	config, err := LoadConfig(configPath)
	if err != nil {
		return "", err
	}

	if config.GoogleAPIKey == "" {
		return "", fmt.Errorf("Google API key not found. Set GOOGLE_API_KEY environment variable or provide it in config file")
	}

	return config.GoogleAPIKey, nil
}
