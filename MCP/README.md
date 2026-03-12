# MCP Google Places Search

A CLI application with MCP (Model Context Protocol) tool integration for Google Places API, built with spf13/cobra and mark3labs/mcp-go.

## Features

- **CLI Interface**: Search for places using Google Places API directly from the command line
- **MCP Server**: Run as an MCP server to integrate with AI assistants and tools that support the MCP protocol
- **Two Search Modes**:
  - Text search: Search by query string (e.g., "restaurants in San Francisco")
  - Nearby search: Search by location coordinates, radius, and place type
- **Flexible Configuration**: Support for both environment variables and config file

## Prerequisites

- Go 1.21 or later
- Google Places API key (from [Google Cloud Console](https://console.cloud.google.com/))

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mcp-google-places
```

2. Build the application:
```bash
go build -o mcp-google-places .
```

## Configuration

### Option 1: Environment Variable (Recommended)

Set the Google API key as an environment variable:

```bash
export GOOGLE_API_KEY=your_google_api_key_here
```

For convenience, you can add this to your shell profile (`~/.zshrc` or `~/.bashrc`).

### Option 2: Config File

1. Copy the example config file:
```bash
cp config.example.yaml ~/.mcp-google-places/config.yaml
```

2. Edit the config file and add your API key:
```yaml
google_api_key: "YOUR_GOOGLE_API_KEY_HERE"
```

The application will look for the config file in:
- Current directory
- `~/.mcp-google-places/config.yaml`
- `~/.config/mcp-google-places/config.yaml`

### Option 3: Custom Config Path

You can specify a custom config file path using the `--config` or `-c` flag:

```bash
./mcp-google-places search "restaurants" -c /path/to/config.yaml
./mcp-google-places mcp -c /path/to/config.yaml
```

### Configuration Priority

The API key is resolved in the following order (highest to lowest priority):
1. Environment variable: `GOOGLE_API_KEY`
2. Config file: `google_api_key`
3. MCP_GOOGLE_PLACES_GOOGLE_API_KEY (alternative env var)

## Usage

### CLI Search Command

Search for places using a text query:

```bash
./mcp-google-places search "restaurants in San Francisco"
```

Search for places near a location:

```bash
./mcp-google-places search "coffee shop" --location "37.7749,-122.4194" --radius 5000
```

#### Search Command Options

| Flag | Short | Description | Default |
|------|-------|-------------|---------|
| `--config` | `-c` | Path to config file | - |
| `--location` | `-l` | Location in 'lat,lng' format for nearby search | - |
| `--radius` | `-r` | Radius in meters for nearby search | 1000 |
| `--type` | `-t` | Place type for nearby search | restaurant |

#### Available Place Types

- `restaurant`
- `cafe`
- `bar`
- `hospital`
- `pharmacy`
- `bank`
- `gas_station`
- `parking`
- `gym`
- `hotel`
- And many more from [Google Places API types](https://developers.google.com/maps/documentation/places/web-service/supported_types)

### MCP Server

Start the MCP server to integrate with AI assistants:

```bash
# Start with stdio transport (default)
./mcp-google-places mcp

# Start with custom config file
./mcp-google-places mcp -c /path/to/config.yaml
```

#### Transport Types

##### Stdio Transport (Default)
```bash
./mcp-google-places mcp --transport stdio
```

##### HTTP Transport
```bash
# Default port 8080
./mcp-google-places mcp --transport http

# Custom port
./mcp-google-places mcp --transport http --port 3000
```

##### SSE (Server-Sent Events) Transport
```bash
# SSE transport on default port 8080
./mcp-google-places mcp --transport sse

# SSE transport on custom port
./mcp-google-places mcp --transport sse --port 9000
```

The MCP server exposes a `google_places_search` tool with the following parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Text search query (required) |
| `location` | string | Location in 'lat,lng' format for nearby search |
| `radius` | integer | Radius in meters (default: 1000) |
| `place_type` | string | Type of place (default: restaurant) |

#### MCP Command Options

| Flag | Short | Description | Default |
|------|-------|-------------|---------|
| `--config` | `-c` | Path to config file | - |
| `--transport` | `-t` | Transport type (stdio, http, sse) | stdio |
| `--port` | `-p` | Port for HTTP/SSE transport | 8080 |

## Examples

### CLI Examples

```bash
# Search for pizza places in New York
./mcp-google-places search "pizza in New York"

# Find ATMs near a location
./mcp-google-places search "ATM" --location "40.7128,-74.0060" --radius 2000 --type "atm"

# Search for hotels in Los Angeles
./mcp-google-places search "hotels in Los Angeles"
```

### MCP Tool Usage

When connected to an MCP-compatible AI assistant, you can use:

```
Search for Italian restaurants in Chicago using the google_places_search tool
```

Or with location-based search:

```
Find coffee shops within 2km of coordinates 34.0522,-118.2437
```

## Development

### Running Tests

```bash
go test ./...
```

### Project Structure

```
.
├── main.go              # Application entry point
├── cmd/
│   ├── root.go         # Root cobra command
│   ├── search.go       # CLI search subcommand
│   └── mcp.go          # MCP server subcommand
├── internal/
│   ├── config.go       # Configuration loading
│   ├── mcp_server.go  # MCP server implementation and Google Places client
│   └── mcp_server_test.go # Tests
├── config.example.yaml # Example configuration file
├── go.mod              # Go module definition
└── go.sum              # Dependency checksums
```

## API Reference

This tool uses the [Google Places API](https://developers.google.com/maps/documentation/places/web-service/overview):

- **Text Search**: `https://maps.googleapis.com/maps/api/place/textsearch/json`
- **Nearby Search**: `https://maps.googleapis.com/maps/api/place/nearbysearch/json`

## License

MIT License
