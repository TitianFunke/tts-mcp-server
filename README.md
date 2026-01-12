# The Things Stack MCP Server

MCP (Model Context Protocol) Server for the [The Things Stack](https://www.thethingsindustries.com/) HTTP API. This server enables interaction with The Things Industries LoRaWAN platform via standardized MCP tools.

## Features

The MCP server offers a wide range of tools for managing your LoRaWAN infrastructure:

*   **Application Management**: Create, list, delete, and inspect applications.
*   **Device Management**: Comprehensive device lifecycle management including `create_otaa_device` which handles registration across Identity, Join, Network, and Application servers in one go.
*   **Gateway Management**: List, inspect, create and delete gateways.
*   **User Management**: Retrieve user details.
*   **Webhook Integrations**: Manage webhooks for applications to integrate with external systems.
*   **Messaging**: View historical uplinks, simulate uplinks, and manage downlink queues.
*   **Payload Formatters**: Generate commands to configure formatters or test them directly.

## Prerequisites

- Docker and Docker Compose installed
- An account on [The Things Stack](https://www.thethingsindustries.com/) or a private instance
- An API Key with appropriate permissions

## Creating an API Key

1. Log in to the [Things Stack Console](https://console.cloud.thethings.network/)
2. Go to your User Settings (Profile)
3. Navigate to **API Keys**
4. Click **Add API Key**
5. Give it a name (e.g., "MCP Server")
6. Select the following permissions:
   - Applications: Read & Write
   - Devices: Read & Write
   - Gateways: Read & Write
   - Users: Read
7. Copy the generated API Key (Format: `NNSXS.XXX...`)

## Quick Start

```bash
# 1. Build Docker Image
docker build -t things-stack-mcp .

# 2. Test (replace placeholder values!)
export TTS_BASE_URL=https://eu1.cloud.thethings.network
export TTS_API_KEY=NNSXS.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
./test_server.sh
```

## Installation & Setup

### 1. Clone Repository / Create Files

Ensure all files are present in the project directory:
```
├── server.py                            # MCP Server Implementation
├── requirements.txt                     # Python Dependencies
├── Dockerfile                           # Docker Image Definition
├── docker-compose.yml                   # Docker Compose Configuration
├── claude_desktop_config.example.json   # Claude Desktop Example Config
├── test_server.sh                       # Test Script
├── run_example.sh                       # Interactive Start Script
└── README.md                            # This file
```

### 2. Build Docker Image

```bash
docker build -t things-stack-mcp .
```

### 3. Configuration

**Available Regions:**
- Europe: `https://eu1.cloud.thethings.network`
- North America: `https://nam1.cloud.thethings.network`
- Australia: `https://au1.cloud.thethings.network`
- Private Instance: `https://your-instance.example.com`

Environment variables are passed directly in the Docker run command (see next section).

## Usage

### With MCP-compatible Clients

The server can be used with any MCP-compatible client (e.g., Claude Desktop App).

#### Claude Desktop Configuration

Add the following to your Claude Desktop configuration:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**Linux:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "things-stack": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-e",
        "TTS_BASE_URL=https://eu1.cloud.thethings.network",
        "-e",
        "TTS_API_KEY=NNSXS.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "things-stack-mcp"
      ]
    }
  }
}
```

**Important:** Replace `NNSXS.XXX...` with your actual API key and adjust the region if necessary.

**Tip:** You can use `claude_desktop_config.example.json` as a template.

### Interactive Start

Use the interactive script for easy configuration:

```bash
./run_example.sh
```

The script will ask for your region and API key, then start the server.

### Direct Test with Docker

```bash
# Start server interactively
docker run --rm -i \
  -e TTS_BASE_URL=https://eu1.cloud.thethings.network \
  -e TTS_API_KEY=NNSXS.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX \
  things-stack-mcp

# Example: List Applications
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"list_applications","arguments":{}},"id":1}' | \
docker run --rm -i \
  -e TTS_BASE_URL=https://eu1.cloud.thethings.network \
  -e TTS_API_KEY=NNSXS.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX \
  things-stack-mcp
```

## Examples

### Create Application

```json
{
  "name": "create_application",
  "arguments": {
    "user_id": "your-user-id",
    "application_id": "my-app",
    "name": "My Application",
    "description": "Test Application"
  }
}
```

### Create OTAA Device (Recommended)

```json
{
  "name": "create_otaa_device",
  "arguments": {
    "application_id": "my-app",
    "device_id": "my-device-01",
    "name": "Sensor 01",
    "description": "Temperature sensor in office",
    "dev_eui": "70B3D57ED0000001",
    "join_eui": "0000000000000000",
    "app_key": "00112233445566778899AABBCCDDEEFF",
    "lorawan_version": "MAC_V1_0_3",
    "frequency_plan_id": "EU_863_870_TTN",
    "supports_class_c": false
  }
}
```

This tool executes **4 separate API calls** to register the device across all required servers:

1.  **POST** `/api/v3/applications/{app_id}/devices` - Identity Server
    - Metadata (Name, IDs, Description)
    - Server addresses

2.  **PUT** `/api/v3/js/applications/{app_id}/devices/{device_id}` - Join Server
    - Root Keys (AppKey for OTAA)
    - Authentication

3.  **PUT** `/api/v3/ns/applications/{app_id}/devices/{device_id}` - Network Server
    - MAC Settings
    - LoRaWAN Version & PHY Version
    - Frequency Plan
    - Class B/C Support

4.  **PUT** `/api/v3/as/applications/{app_id}/devices/{device_id}` - Application Server
    - Device IDs
    - Session Configuration

**Important Parameters:**
- `app_key`: 32-digit hex string (128-bit key)
- `dev_eui` & `join_eui`: 16-digit hex strings (64-bit)
- `frequency_plan_id`: Common values:
  - `EU_863_870_TTN` - Europe (Default)
  - `US_902_928` - USA
  - `AU_915_928` - Australia
  - `AS_923` - Asia
- `lorawan_version`: `MAC_V1_0_2`, `MAC_V1_0_3`, `MAC_V1_0_4`, `MAC_V1_1`

### Create Webhook

```json
{
  "name": "set_webhook",
  "arguments": {
    "application_id": "my-app",
    "webhook_id": "my-integration",
    "base_url": "https://myserver.com/webhook",
    "format": "json",
    "uplink_message": {
      "path": "/up"
    },
    "join_accept": {
      "path": "/join"
    }
  }
}
```

### Set Payload Formatter (Command Generator)

```json
{
  "name": "generate_formatter_command",
  "arguments": {
    "application_id": "my-app",
    "device_id": "my-device-01",
    "formatter_type": "FORMATTER_JAVASCRIPT",
    "formatter_code": "function decodeUplink(input) { return {data: {temp: input.bytes[0]}}; }",
    "command_type": "curl"
  }
}
```

**Output:** Ready-to-use cURL command to copy & execute.

**Available Command Types:**
- `curl` - cURL Command (Default)
- `cli` - The Things Stack CLI Command
- `python` - Python Script

The tool generates **ready-to-use commands** that you can execute directly, as direct API calls might not work on all TTS installations.

### Retrieve Uplink Data

```json
{
  "name": "get_device_uplinks",
  "arguments": {
    "application_id": "my-app",
    "device_id": "my-device-01",
    "limit": 20
  }
}
```

## Development

### Local Development without Docker

```bash
# Create Virtual Environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Dependencies
pip install -r requirements.txt

# Set Environment Variables
export TTS_BASE_URL=https://eu1.cloud.thethings.network
export TTS_API_KEY=NNSXS.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Start Server
python server.py
```

## Troubleshooting

### Authentication Errors (401)
- Verify your API Key is correct
- Ensure the API Key has the required permissions
- Check if the API Key is still valid
- The API Key should start with `NNSXS.`

### Connection Errors
- Check `TTS_BASE_URL` (must start with `https://`)
- Ensure you are using the correct region
- Check your network connection
- For self-hosted instances: Check Firewall and SSL certificates

### Device Creation Failed
- `dev_eui` and `join_eui` must be valid 64-bit hex strings (16 characters)
- `device_id` must only contain lowercase letters, numbers, and dashes
- The Application must already exist

### MCP Server Not Starting in Claude Desktop
- Check JSON syntax in Claude Desktop configuration
- Ensure Docker image is built: `docker build -t things-stack-mcp .`
- Check Docker logs: `docker logs <container-id>`

## API References

- [The Things Stack HTTP API Documentation](https://www.thethingsindustries.com/docs/api/reference/http/)
- [Authentication](https://www.thethingsindustries.com/docs/api/concepts/auth/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

## License

MIT

## Author

Created with Claude Code