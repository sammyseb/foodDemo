package cmd

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
)

var RootCmd = &cobra.Command{
	Use:   "mcp-google-places",
	Short: "MCP Google Places Search - A CLI tool with MCP integration for Google Places API",
	Long: `MCP Google Places Search application that provides:
- A CLI interface for Google Places API
- MCP (Model Context Protocol) tool integration
- Google Places search capabilities`,
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("MCP Google Places Search CLI")
		fmt.Println("Use --help for more information")
	},
}

var (
	configPath string
)

func Execute() {
	if err := RootCmd.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

func init() {
	RootCmd.PersistentFlags().StringVarP(&configPath, "config", "c", "", "Config file path (default is $HOME/.mcp-google-places/config.yaml)")
}
