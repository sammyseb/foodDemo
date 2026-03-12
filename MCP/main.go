package main

import (
	"os"

	"mcp-google-places/cmd"
)

func main() {
	cmd.Execute()
}

func init() {
	// Ensure config directory exists
	homeDir, _ := os.UserHomeDir()
	configDir := homeDir + "/.mcp-google-places"
	os.MkdirAll(configDir, 0755)
}
