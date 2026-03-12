package cmd

import (
	"context"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"

	"mcp-google-places/internal"

	"github.com/mark3labs/mcp-go/server"
	"github.com/spf13/cobra"
)

var (
	mcpTransport string
	mcpPort      int
)

var mcpCmd = &cobra.Command{
	Use:   "mcp",
	Short: "Start the MCP server",
	Long:  `Start the Model Context Protocol (MCP) server for Google Places Search`,
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

		_ = apiKey // API key is validated but server uses env var internally

		fmt.Println("Starting MCP Google Places Server...")
		fmt.Printf("Transport: %s\n", mcpTransport)

		mcpServer := internal.MCPServer(configPath)

		switch mcpTransport {
		case "stdio":
			// Stdio transport
			fmt.Println("Server running on stdio...")
			stdioServer := server.NewStdioServer(mcpServer)
			stdioServer.Listen(context.Background(), os.Stdin, os.Stdout)

		case "http", "streamable-http":
			// Streamable HTTP transport
			addr := fmt.Sprintf(":%d", mcpPort)
			fmt.Printf("Server running on http://localhost%s/mcp\n", addr)

			httpServer := server.NewStreamableHTTPServer(mcpServer)

			// Start server with graceful shutdown
			go func() {
				if err := http.ListenAndServe(addr, httpServer); err != nil && err != http.ErrServerClosed {
					fmt.Fprintf(os.Stderr, "HTTP server error: %v\n", err)
					os.Exit(1)
				}
			}()

			// Wait for interrupt signal
			quit := make(chan os.Signal, 1)
			signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
			<-quit

			fmt.Println("\nShutting down server...")

		default:
			fmt.Fprintf(os.Stderr, "Unknown transport: %s\n", mcpTransport)
			fmt.Fprintln(os.Stderr, "Available transports: stdio, http, streamable-http")
			os.Exit(1)
		}
	},
}

func init() {
	mcpCmd.Flags().StringVarP(&mcpTransport, "transport", "t", "stdio", "Transport type (stdio, http, streamable-http)")
	mcpCmd.Flags().IntVarP(&mcpPort, "port", "p", 8080, "Port for HTTP/streamable-http transport")
	RootCmd.AddCommand(mcpCmd)
}
