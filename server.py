#!/usr/bin/env python3
"""
MCP Server for The Things Stack HTTP API
Provides tools to interact with The Things Industries LoRaWAN platform
"""

import os
import json
import asyncio
from typing import Any, Optional
from urllib.parse import urljoin

import httpx
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
TTS_BASE_URL = os.getenv("TTS_BASE_URL", "https://eu1.cloud.thethings.network")
TTS_API_KEY = os.getenv("TTS_API_KEY", "")
API_VERSION = "/api/v3"


class ThingsStackClient:
    """Client for The Things Stack HTTP API"""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        )

    def _build_url(self, path: str) -> str:
        """Build full API URL"""
        path = path.lstrip("/")
        return f"{self.base_url}{API_VERSION}/{path}"

    async def get(self, path: str, params: Optional[dict] = None) -> dict:
        """Execute GET request"""
        url = self._build_url(path)
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def post(self, path: str, data: dict) -> dict:
        """Execute POST request"""
        url = self._build_url(path)
        response = await self.client.post(url, json=data)
        response.raise_for_status()
        return response.json()

    async def put(self, path: str, data: dict) -> dict:
        """Execute PUT request"""
        url = self._build_url(path)
        response = await self.client.put(url, json=data)
        response.raise_for_status()
        return response.json()

    async def delete(self, path: str) -> dict:
        """Execute DELETE request"""
        url = self._build_url(path)
        response = await self.client.delete(url)
        response.raise_for_status()
        return response.json() if response.text else {"status": "deleted"}

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Initialize MCP Server
app = Server("things-stack-mcp")
tts_client = ThingsStackClient(TTS_BASE_URL, TTS_API_KEY)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="list_applications",
            description="List all LoRaWAN applications. Use this to: (1) See all applications a user owns, (2) Find application IDs for further operations, (3) Get overview of existing applications. Returns: application_id, name, description, creation date. Optional: filter by user_id.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID to list applications for (optional)"
                    }
                }
            }
        ),
        Tool(
            name="get_application",
            description="Get detailed information about a specific LoRaWAN application. Use when you need: (1) Full application metadata, (2) Server addresses, (3) API key information, (4) Application attributes. Requires: application_id. Returns: Complete application object with all settings.",
            inputSchema={
                "type": "object",
                "properties": {
                    "application_id": {
                        "type": "string",
                        "description": "The application ID"
                    }
                },
                "required": ["application_id"]
            }
        ),
        Tool(
            name="create_application",
            description="Create a new application in The Things Stack",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID who owns the application (required if organization_id is not set)"
                    },
                    "organization_id": {
                        "type": "string",
                        "description": "Organization ID who owns the application (required if user_id is not set)"
                    },
                    "application_id": {
                        "type": "string",
                        "description": "Unique application identifier (lowercase, alphanumeric with dashes)"
                    },
                    "name": {
                        "type": "string",
                        "description": "Human-readable application name"
                    },
                    "description": {
                        "type": "string",
                        "description": "Application description (optional)"
                    }
                },
                "required": ["application_id", "name"]
            }
        ),
        Tool(
            name="delete_application",
            description="Delete an application from The Things Stack",
            inputSchema={
                "type": "object",
                "properties": {
                    "application_id": {
                        "type": "string",
                        "description": "The application ID to delete"
                    }
                },
                "required": ["application_id"]
            }
        ),
        Tool(
            name="list_organizations",
            description="List all organizations the user is a member of",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="list_devices",
            description="List all LoRaWAN end devices (sensors/nodes) in an application. Use this to: (1) See all devices in an application, (2) Find device IDs, (3) Get device overview with DevEUI, JoinEUI, status. Requires: application_id. Returns: Array of devices with IDs, names, descriptions, creation dates, and EUIs.",
            inputSchema={
                "type": "object",
                "properties": {
                    "application_id": {
                        "type": "string",
                        "description": "The application ID"
                    }
                },
                "required": ["application_id"]
            }
        ),
        Tool(
            name="get_device",
            description="Get complete details about a specific LoRaWAN device. Use when you need: (1) Full device configuration, (2) Device EUIs and IDs, (3) LoRaWAN settings (version, frequency plan), (4) MAC state, (5) Server registrations, (6) Last activity time. Requires: application_id and device_id. Returns: Complete device object with all registration details across Identity/Join/Network/Application servers.",
            inputSchema={
                "type": "object",
                "properties": {
                    "application_id": {
                        "type": "string",
                        "description": "The application ID"
                    },
                    "device_id": {
                        "type": "string",
                        "description": "The device ID"
                    }
                },
                "required": ["application_id", "device_id"]
            }
        ),
        Tool(
            name="create_device",
            description="Register a new end device in an application (basic registration, use create_otaa_device for complete OTAA setup)",
            inputSchema={
                "type": "object",
                "properties": {
                    "application_id": {
                        "type": "string",
                        "description": "The application ID"
                    },
                    "device_id": {
                        "type": "string",
                        "description": "Unique device identifier"
                    },
                    "name": {
                        "type": "string",
                        "description": "Human-readable device name"
                    },
                    "description": {
                        "type": "string",
                        "description": "Device description (optional)"
                    },
                    "dev_eui": {
                        "type": "string",
                        "description": "Device EUI (64-bit hex string)"
                    },
                    "join_eui": {
                        "type": "string",
                        "description": "Join EUI / App EUI (64-bit hex string)"
                    }
                },
                "required": ["application_id", "device_id", "name", "dev_eui", "join_eui"]
            }
        ),
        Tool(
            name="create_otaa_device",
            description="RECOMMENDED for new devices: Create a complete OTAA LoRaWAN device ready for use. This tool performs 4 separate API calls to register the device in ALL required servers: (1) Identity Server (metadata), (2) Join Server (AppKey for OTAA), (3) Network Server (LoRaWAN version, frequency plan, MAC settings), (4) Application Server (session config). Use this instead of create_device for production devices. Requires: application_id, device_id, name, dev_eui (16-char hex), join_eui (16-char hex), app_key (32-char hex). Optional: lorawan_version (default: MAC_V1_0_3), frequency_plan_id (default: EU_863_870_TTN), supports_class_c. After successful creation, device is immediately ready for OTAA joins.",
            inputSchema={
                "type": "object",
                "properties": {
                    "application_id": {
                        "type": "string",
                        "description": "The application ID"
                    },
                    "device_id": {
                        "type": "string",
                        "description": "Unique device identifier (lowercase, alphanumeric with dashes)"
                    },
                    "name": {
                        "type": "string",
                        "description": "Human-readable device name"
                    },
                    "description": {
                        "type": "string",
                        "description": "Device description (optional)"
                    },
                    "dev_eui": {
                        "type": "string",
                        "description": "Device EUI (16-character hex string, e.g., '70B3D57ED0000001')"
                    },
                    "join_eui": {
                        "type": "string",
                        "description": "Join EUI / App EUI (16-character hex string, e.g., '0000000000000000')"
                    },
                    "app_key": {
                        "type": "string",
                        "description": "Application Key for LoRaWAN 1.0.x (32-character hex string)"
                    },
                    "lorawan_version": {
                        "type": "string",
                        "description": "LoRaWAN version (default: MAC_V1_0_3). Options: MAC_V1_0_2, MAC_V1_0_3, MAC_V1_0_4, MAC_V1_1"
                    },
                    "lorawan_phy_version": {
                        "type": "string",
                        "description": "LoRaWAN PHY version (default: PHY_V1_0_3_REV_A). Options: PHY_V1_0_2_REV_B, PHY_V1_0_3_REV_A, PHY_V1_1_REV_B"
                    },
                    "frequency_plan_id": {
                        "type": "string",
                        "description": "Frequency plan ID (default: EU_863_870_TTN). Common: EU_863_870_TTN, US_902_928, AU_915_928, AS_923"
                    },
                    "supports_class_c": {
                        "type": "boolean",
                        "description": "Enable Class C support (default: false)"
                    }
                },
                "required": ["application_id", "device_id", "name", "dev_eui", "join_eui", "app_key"]
            }
        ),
        Tool(
            name="delete_device",
            description="Delete an end device from an application",
            inputSchema={
                "type": "object",
                "properties": {
                    "application_id": {
                        "type": "string",
                        "description": "The application ID"
                    },
                    "device_id": {
                        "type": "string",
                        "description": "The device ID to delete"
                    }
                },
                "required": ["application_id", "device_id"]
            }
        ),
        Tool(
            name="get_device_uplinks",
            description="Retrieve recent uplink messages (data transmissions) from a device. Use this for: (1) Monitoring device activity, (2) Checking sensor data, (3) Debugging payload issues, (4) Viewing decoded payloads (if formatter is configured), (5) Seeing message metadata (RSSI, SNR, timestamp). Requires: application_id, device_id. Optional: limit (default 10, max depends on server). Returns: Array of uplink messages with raw payload, decoded payload (if formatter exists), FPort, timestamp, RX metadata (signal strength, gateway info).",
            inputSchema={
                "type": "object",
                "properties": {
                    "application_id": {
                        "type": "string",
                        "description": "The application ID"
                    },
                    "device_id": {
                        "type": "string",
                        "description": "The device ID"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of messages to retrieve (default: 10)"
                    }
                },
                "required": ["application_id", "device_id"]
            }
        ),
        Tool(
            name="list_gateways",
            description="List all gateways accessible with the API key",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID to list gateways for (optional)"
                    }
                }
            }
        ),
        Tool(
            name="get_gateway",
            description="Get detailed information about a specific gateway",
            inputSchema={
                "type": "object",
                "properties": {
                    "gateway_id": {
                        "type": "string",
                        "description": "The gateway ID"
                    }
                },
                "required": ["gateway_id"]
            }
        ),
        Tool(
            name="get_gateway_status",
            description="Get connection status and statistics for a gateway (from Gateway Server)",
            inputSchema={
                "type": "object",
                "properties": {
                    "gateway_id": {
                        "type": "string",
                        "description": "The gateway ID"
                    }
                },
                "required": ["gateway_id"]
            }
        ),
        Tool(
            name="create_gateway",
            description="Create a new gateway in The Things Stack",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID who owns the gateway (required if organization_id is not set)"
                    },
                    "organization_id": {
                        "type": "string",
                        "description": "Organization ID who owns the gateway (required if user_id is not set)"
                    },
                    "gateway_id": {
                        "type": "string",
                        "description": "Unique gateway identifier"
                    },
                    "name": {
                        "type": "string",
                        "description": "Human-readable gateway name"
                    },
                    "frequency_plan_id": {
                        "type": "string",
                        "description": "Frequency plan ID (e.g., EU_863_870_TTN)"
                    },
                    "gateway_eui": {
                        "type": "string",
                        "description": "Gateway EUI (optional)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Gateway description (optional)"
                    }
                },
                "required": ["gateway_id", "name", "frequency_plan_id"]
            }
        ),
        Tool(
            name="delete_gateway",
            description="Delete a gateway from The Things Stack",
            inputSchema={
                "type": "object",
                "properties": {
                    "gateway_id": {
                        "type": "string",
                        "description": "The gateway ID to delete"
                    }
                },
                "required": ["gateway_id"]
            }
        ),
        Tool(
            name="get_user",
            description="Get information about a specific user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The user ID"
                    }
                },
                "required": ["user_id"]
            }
        ),
        Tool(
            name="list_webhooks",
            description="List all webhooks for an application",
            inputSchema={
                "type": "object",
                "properties": {
                    "application_id": {
                        "type": "string",
                        "description": "The application ID"
                    }
                },
                "required": ["application_id"]
            }
        ),
        Tool(
            name="get_webhook",
            description="Get details of a specific webhook",
            inputSchema={
                "type": "object",
                "properties": {
                    "application_id": {
                        "type": "string",
                        "description": "The application ID"
                    },
                    "webhook_id": {
                        "type": "string",
                        "description": "The webhook ID"
                    }
                },
                "required": ["application_id", "webhook_id"]
            }
        ),
        Tool(
            name="set_webhook",
            description="Create or update a webhook for an application",
            inputSchema={
                "type": "object",
                "properties": {
                    "application_id": {
                        "type": "string",
                        "description": "The application ID"
                    },
                    "webhook_id": {
                        "type": "string",
                        "description": "The webhook ID"
                    },
                    "base_url": {
                        "type": "string",
                        "description": "The base URL for the webhook"
                    },
                    "format": {
                        "type": "string",
                        "description": "Payload format (json, protobuf) - default: json"
                    },
                    "uplink_message": {
                        "type": "object",
                        "description": "Configuration for uplink messages (e.g., {'path': '/up'})"
                    },
                    "join_accept": {
                        "type": "object",
                        "description": "Configuration for join-accept messages"
                    },
                    "downlink_ack": {
                        "type": "object",
                        "description": "Configuration for downlink acks"
                    },
                    "downlink_nack": {
                        "type": "object",
                        "description": "Configuration for downlink nacks"
                    },
                    "downlink_sent": {
                        "type": "object",
                        "description": "Configuration for downlink sent"
                    },
                    "downlink_failed": {
                        "type": "object",
                        "description": "Configuration for downlink failed"
                    },
                    "downlink_queued": {
                        "type": "object",
                        "description": "Configuration for downlink queued"
                    },
                    "location_solved": {
                        "type": "object",
                        "description": "Configuration for location solved"
                    },
                    "service_data": {
                        "type": "object",
                        "description": "Configuration for service data"
                    }
                },
                "required": ["application_id", "webhook_id", "base_url"]
            }
        ),
        Tool(
            name="delete_webhook",
            description="Delete a webhook from an application",
            inputSchema={
                "type": "object",
                "properties": {
                    "application_id": {
                        "type": "string",
                        "description": "The application ID"
                    },
                    "webhook_id": {
                        "type": "string",
                        "description": "The webhook ID"
                    }
                },
                "required": ["application_id", "webhook_id"]
            }
        ),
        # Helper tools for gRPC operations (generates commands)
        Tool(
            name="generate_formatter_command",
            description="PAYLOAD FORMATTER SETUP TOOL: Generates ready-to-use commands to set JavaScript/CayenneLPP/Repository payload formatters on devices. Use this when user wants to: (1) Set a payload formatter/decoder, (2) Configure uplink/downlink formatting, (3) Add custom JavaScript decoder code. This tool DOES NOT execute the command - it generates it for the user to run manually (more reliable than direct API). Outputs: cURL command (default), TTS CLI command, or Python script based on command_type. Supports FORMATTER_JAVASCRIPT (with code up to 64KB), FORMATTER_CAYENNELPP, FORMATTER_REPOSITORY. The generated command is ready to copy and execute.",
            inputSchema={
                "type": "object",
                "properties": {
                    "application_id": {
                        "type": "string",
                        "description": "The application ID"
                    },
                    "device_id": {
                        "type": "string",
                        "description": "The device ID"
                    },
                    "formatter_type": {
                        "type": "string",
                        "description": "Formatter type: FORMATTER_JAVASCRIPT, FORMATTER_CAYENNELPP, FORMATTER_REPOSITORY"
                    },
                    "formatter_code": {
                        "type": "string",
                        "description": "JavaScript code for the formatter (if FORMATTER_JAVASCRIPT)"
                    },
                    "command_type": {
                        "type": "string",
                        "description": "Type of command to generate: curl, cli, python (default: curl)"
                    }
                },
                "required": ["application_id", "device_id", "formatter_type"]
            }
        ),
        Tool(
            name="downlink_queue_push",
            description="Add a downlink message to the device's queue",
            inputSchema={
                "type": "object",
                "properties": {
                    "application_id": {
                        "type": "string",
                        "description": "The application ID"
                    },
                    "device_id": {
                        "type": "string",
                        "description": "The device ID"
                    },
                    "frm_payload": {
                        "type": "string",
                        "description": "Payload in base64 or hex format"
                    },
                    "f_port": {
                        "type": "integer",
                        "description": "FPort (1-223)"
                    },
                    "priority": {
                        "type": "string",
                        "description": "Priority: LOWEST, LOW, BELOW_NORMAL, NORMAL, ABOVE_NORMAL, HIGH, HIGHEST (default: NORMAL)"
                    },
                    "confirmed": {
                        "type": "boolean",
                        "description": "Request confirmation from device (default: false)"
                    }
                },
                "required": ["application_id", "device_id", "frm_payload", "f_port"]
            }
        ),
        Tool(
            name="downlink_queue_list",
            description="List pending downlink messages in the device's queue",
            inputSchema={
                "type": "object",
                "properties": {
                    "application_id": {
                        "type": "string",
                        "description": "The application ID"
                    },
                    "device_id": {
                        "type": "string",
                        "description": "The device ID"
                    }
                },
                "required": ["application_id", "device_id"]
            }
        ),
        Tool(
            name="downlink_queue_replace",
            description="Replace the entire downlink queue with new messages",
            inputSchema={
                "type": "object",
                "properties": {
                    "application_id": {
                        "type": "string",
                        "description": "The application ID"
                    },
                    "device_id": {
                        "type": "string",
                        "description": "The device ID"
                    },
                    "downlinks": {
                        "type": "array",
                        "description": "Array of downlink messages (each with frm_payload, f_port, priority, confirmed)"
                    }
                },
                "required": ["application_id", "device_id", "downlinks"]
            }
        ),
        Tool(
            name="simulate_uplink",
            description="Simulate an uplink message for testing (triggers formatters and integrations)",
            inputSchema={
                "type": "object",
                "properties": {
                    "application_id": {
                        "type": "string",
                        "description": "The application ID"
                    },
                    "device_id": {
                        "type": "string",
                        "description": "The device ID"
                    },
                    "frm_payload": {
                        "type": "string",
                        "description": "Payload in base64 or hex format"
                    },
                    "f_port": {
                        "type": "integer",
                        "description": "FPort (1-223)"
                    },
                    "confirmed": {
                        "type": "boolean",
                        "description": "Confirmed uplink (default: false)"
                    }
                },
                "required": ["application_id", "device_id", "frm_payload", "f_port"]
            }
        ),
        Tool(
            name="decode_uplink",
            description="Test uplink payload formatter (decode a raw payload)",
            inputSchema={
                "type": "object",
                "properties": {
                    "application_id": {
                        "type": "string",
                        "description": "The application ID"
                    },
                    "device_id": {
                        "type": "string",
                        "description": "The device ID (optional, uses application-level formatter if omitted)"
                    },
                    "frm_payload": {
                        "type": "string",
                        "description": "Raw payload in base64 format"
                    },
                    "f_port": {
                        "type": "integer",
                        "description": "FPort"
                    }
                },
                "required": ["application_id", "frm_payload", "f_port"]
            }
        ),
        Tool(
            name="encode_downlink",
            description="Test downlink payload formatter (encode JSON to raw payload)",
            inputSchema={
                "type": "object",
                "properties": {
                    "application_id": {
                        "type": "string",
                        "description": "The application ID"
                    },
                    "device_id": {
                        "type": "string",
                        "description": "The device ID (optional, uses application-level formatter if omitted)"
                    },
                    "decoded_payload": {
                        "type": "object",
                        "description": "JSON object to encode"
                    },
                    "f_port": {
                        "type": "integer",
                        "description": "FPort"
                    }
                },
                "required": ["application_id", "decoded_payload"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""

    try:
        if name == "list_applications":
            user_id = arguments.get("user_id")
            if user_id:
                path = f"users/{user_id}/applications"
            else:
                path = "applications"

            result = await tts_client.get(path)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "get_application":
            app_id = arguments["application_id"]
            path = f"applications/{app_id}"
            result = await tts_client.get(path)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "create_application":
            app_id = arguments["application_id"]
            user_id = arguments.get("user_id")
            org_id = arguments.get("organization_id")
            
            if not user_id and not org_id:
                raise ValueError("Either user_id or organization_id must be provided")

            data = {
                "application": {
                    "ids": {
                        "application_id": app_id
                    },
                    "name": arguments["name"]
                }
            }

            if "description" in arguments:
                data["application"]["description"] = arguments["description"]

            if user_id:
                path = f"users/{user_id}/applications"
            else:
                path = f"organizations/{org_id}/applications"

            result = await tts_client.post(path, data)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "delete_application":
            app_id = arguments["application_id"]
            path = f"applications/{app_id}"
            result = await tts_client.delete(path)
            return [TextContent(
                type="text",
                text=f"Application {app_id} deleted successfully"
            )]

        elif name == "list_organizations":
            path = "organizations"
            result = await tts_client.get(path)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        elif name == "list_devices":
            app_id = arguments["application_id"]
            path = f"applications/{app_id}/devices"
            result = await tts_client.get(path)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "get_device":
            app_id = arguments["application_id"]
            dev_id = arguments["device_id"]
            path = f"applications/{app_id}/devices/{dev_id}"
            result = await tts_client.get(path)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "create_device":
            app_id = arguments["application_id"]
            dev_id = arguments["device_id"]

            data = {
                "end_device": {
                    "ids": {
                        "device_id": dev_id,
                        "application_ids": {
                            "application_id": app_id
                        },
                        "dev_eui": arguments["dev_eui"],
                        "join_eui": arguments["join_eui"]
                    },
                    "name": arguments["name"]
                }
            }

            if "description" in arguments:
                data["end_device"]["description"] = arguments["description"]

            path = f"applications/{app_id}/devices"
            result = await tts_client.post(path, data)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "create_otaa_device":
            app_id = arguments["application_id"]
            dev_id = arguments["device_id"]
            dev_eui = arguments["dev_eui"]
            join_eui = arguments["join_eui"]
            app_key = arguments["app_key"]

            # Defaults
            lorawan_version = arguments.get("lorawan_version", "MAC_V1_0_3")
            lorawan_phy_version = arguments.get("lorawan_phy_version", "PHY_V1_0_3_REV_A")
            frequency_plan_id = arguments.get("frequency_plan_id", "EU_863_870_TTN")
            supports_class_c = arguments.get("supports_class_c", False)

            # Server address (without protocol)
            server_address = TTS_BASE_URL.replace("https://", "").replace("http://", "")

            results = {
                "identity_server": None,
                "join_server": None,
                "network_server": None,
                "application_server": None
            }

            try:
                # Step 1: Register in Identity Server
                identity_payload = {
                    "end_device": {
                        "ids": {
                            "dev_eui": dev_eui,
                            "join_eui": join_eui,
                            "device_id": dev_id
                        },
                        "join_server_address": server_address,
                        "network_server_address": server_address,
                        "application_server_address": server_address
                    },
                    "field_mask": {
                        "paths": [
                            "network_server_address",
                            "application_server_address",
                            "join_server_address",
                            "ids.dev_eui",
                            "ids.join_eui"
                        ]
                    }
                }

                if "name" in arguments:
                    identity_payload["end_device"]["name"] = arguments["name"]
                    identity_payload["field_mask"]["paths"].append("name")

                if "description" in arguments:
                    identity_payload["end_device"]["description"] = arguments["description"]
                    identity_payload["field_mask"]["paths"].append("description")

                path = f"applications/{app_id}/devices"
                results["identity_server"] = await tts_client.post(path, identity_payload)

                # Step 2: Register in Join Server (root keys)
                join_payload = {
                    "end_device": {
                        "ids": {
                            "dev_eui": dev_eui,
                            "join_eui": join_eui,
                            "device_id": dev_id
                        },
                        "network_server_address": server_address,
                        "application_server_address": server_address,
                        "root_keys": {
                            "app_key": {
                                "key": app_key
                            }
                        }
                    },
                    "field_mask": {
                        "paths": [
                            "network_server_address",
                            "application_server_address",
                            "ids.dev_eui",
                            "ids.join_eui",
                            "ids.device_id",
                            "root_keys.app_key.key"
                        ]
                    }
                }

                path = f"js/applications/{app_id}/devices/{dev_id}"
                results["join_server"] = await tts_client.put(path, join_payload)

                # Step 3: Register in Network Server (MAC settings)
                net_payload = {
                    "end_device": {
                        "frequency_plan_id": frequency_plan_id,
                        "lorawan_phy_version": lorawan_phy_version,
                        "multicast": False,
                        "supports_join": True,
                        "lorawan_version": lorawan_version,
                        "ids": {
                            "dev_eui": dev_eui,
                            "join_eui": join_eui,
                            "device_id": dev_id
                        },
                        "supports_class_c": supports_class_c,
                        "supports_class_b": False,
                        "mac_settings": {
                            "rx2_data_rate_index": 0,
                            "rx2_frequency": 869525000
                        }
                    },
                    "field_mask": {
                        "paths": [
                            "frequency_plan_id",
                            "lorawan_phy_version",
                            "multicast",
                            "supports_join",
                            "lorawan_version",
                            "ids.dev_eui",
                            "ids.join_eui",
                            "ids.device_id",
                            "supports_class_c",
                            "supports_class_b",
                            "mac_settings.rx2_data_rate_index",
                            "mac_settings.rx2_frequency"
                        ]
                    }
                }

                path = f"ns/applications/{app_id}/devices/{dev_id}"
                results["network_server"] = await tts_client.put(path, net_payload)

                # Step 4: Register in Application Server
                app_payload = {
                    "end_device": {
                        "ids": {
                            "dev_eui": dev_eui,
                            "join_eui": join_eui,
                            "device_id": dev_id
                        }
                    },
                    "field_mask": {
                        "paths": [
                            "ids.dev_eui",
                            "ids.join_eui",
                            "ids.device_id"
                        ]
                    }
                }

                path = f"as/applications/{app_id}/devices/{dev_id}"
                results["application_server"] = await tts_client.put(path, app_payload)

                # Success message
                return [TextContent(
                    type="text",
                    text=f"✅ OTAA Device '{dev_id}' successfully registered in all servers:\n\n" +
                         f"✓ Identity Server\n" +
                         f"✓ Join Server (AppKey configured)\n" +
                         f"✓ Network Server (LoRaWAN {lorawan_version}, {frequency_plan_id})\n" +
                         f"✓ Application Server\n\n" +
                         f"Device is ready for OTAA joins!\n\n" +
                         f"Full results:\n{json.dumps(results, indent=2)}"
                )]

            except Exception as e:
                # Cleanup on error: try to delete from Identity Server
                error_msg = str(e)
                try:
                    await tts_client.delete(f"applications/{app_id}/devices/{dev_id}")
                    cleanup_msg = "\n\n⚠️ Device was partially created but rolled back due to error."
                except:
                    cleanup_msg = "\n\n⚠️ Device may be partially created. Manual cleanup might be needed."

                return [TextContent(
                    type="text",
                    text=f"❌ Error creating OTAA device:\n{error_msg}\n\n" +
                         f"Results so far:\n{json.dumps(results, indent=2)}" +
                         cleanup_msg
                )]

        elif name == "delete_device":
            app_id = arguments["application_id"]
            dev_id = arguments["device_id"]
            path = f"applications/{app_id}/devices/{dev_id}"
            result = await tts_client.delete(path)
            return [TextContent(
                type="text",
                text=f"Device {dev_id} deleted successfully"
            )]

        elif name == "get_device_uplinks":
            app_id = arguments["application_id"]
            dev_id = arguments["device_id"]
            limit = arguments.get("limit", 10)

            # Note: This endpoint structure may vary depending on TTS configuration
            path = f"applications/{app_id}/devices/{dev_id}/packages/storage/uplink_message"
            params = {"limit": limit, "order": "-received_at"}

            result = await tts_client.get(path, params=params)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "list_gateways":
            user_id = arguments.get("user_id")
            if user_id:
                path = f"users/{user_id}/gateways"
            else:
                path = "gateways"

            result = await tts_client.get(path)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "get_gateway":
            gw_id = arguments["gateway_id"]
            path = f"gateways/{gw_id}"
            result = await tts_client.get(path)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "get_gateway_status":
            gw_id = arguments["gateway_id"]
            # Gateway Server (GS) connection stats
            path = f"gs/gateways/{gw_id}/connection/stats"
            result = await tts_client.get(path)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "create_gateway":
            gw_id = arguments["gateway_id"]
            user_id = arguments.get("user_id")
            org_id = arguments.get("organization_id")
            
            if not user_id and not org_id:
                raise ValueError("Either user_id or organization_id must be provided")
            
            data = {
                "gateway": {
                    "ids": {
                        "gateway_id": gw_id
                    },
                    "name": arguments["name"],
                    "frequency_plan_id": arguments["frequency_plan_id"],
                    "gateway_server_address": TTS_BASE_URL.replace("https://", "").replace("http://", "")
                }
            }

            if "gateway_eui" in arguments:
                data["gateway"]["ids"]["eui"] = arguments["gateway_eui"]
                
            if "description" in arguments:
                data["gateway"]["description"] = arguments["description"]

            if user_id:
                path = f"users/{user_id}/gateways"
            else:
                path = f"organizations/{org_id}/gateways"
                
            result = await tts_client.post(path, data)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "delete_gateway":
            gw_id = arguments["gateway_id"]
            path = f"gateways/{gw_id}"
            result = await tts_client.delete(path)
            return [TextContent(
                type="text",
                text=f"Gateway {gw_id} deleted successfully"
            )]

        elif name == "get_user":
            user_id = arguments["user_id"]
            path = f"users/{user_id}"
            result = await tts_client.get(path)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        elif name == "list_webhooks":
            app_id = arguments["application_id"]
            path = f"as/applications/{app_id}/webhooks"
            result = await tts_client.get(path)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "get_webhook":
            app_id = arguments["application_id"]
            webhook_id = arguments["webhook_id"]
            path = f"as/applications/{app_id}/webhooks/{webhook_id}"
            result = await tts_client.get(path)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "set_webhook":
            app_id = arguments["application_id"]
            webhook_id = arguments["webhook_id"]
            
            webhook_data = {
                "ids": {
                    "webhook_id": webhook_id
                },
                "base_url": arguments["base_url"],
                "format": arguments.get("format", "json")
            }
            
            field_paths = ["base_url", "format"]
            
            # Map optional message types
            message_types = [
                "uplink_message", "join_accept", "downlink_ack", "downlink_nack", 
                "downlink_sent", "downlink_failed", "downlink_queued", 
                "location_solved", "service_data"
            ]
            
            for msg_type in message_types:
                if msg_type in arguments:
                    webhook_data[msg_type] = arguments[msg_type]
                    field_paths.append(msg_type)
            
            data = {
                "webhook": webhook_data,
                "field_mask": {
                    "paths": field_paths
                }
            }
            
            path = f"as/applications/{app_id}/webhooks/{webhook_id}"
            result = await tts_client.put(path, data)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "delete_webhook":
            app_id = arguments["application_id"]
            webhook_id = arguments["webhook_id"]
            path = f"as/applications/{app_id}/webhooks/{webhook_id}"
            result = await tts_client.delete(path)
            return [TextContent(
                type="text",
                text=f"Webhook {webhook_id} deleted successfully"
            )]

        # Helper tools - generate commands for gRPC operations
        elif name == "generate_formatter_command":
            app_id = arguments["application_id"]
            dev_id = arguments["device_id"]
            formatter_type = arguments["formatter_type"]
            formatter_code = arguments.get("formatter_code", "")
            command_type = arguments.get("command_type", "curl")

            base_url = TTS_BASE_URL.rstrip("/")

            if command_type == "curl":
                # Generate cURL command
                if formatter_code:
                    # Escape single quotes in formatter code for shell
                    escaped_code = formatter_code.replace("'", "'\\''")

                    curl_cmd = f'''curl -X PUT \\
  -H "Authorization: Bearer $TTS_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "end_device": {{
      "ids": {{
        "device_id": "{dev_id}",
        "application_ids": {{
          "application_id": "{app_id}"
        }}
      }},
      "formatters": {{
        "up_formatter": "{formatter_type}",
        "up_formatter_parameter": {json.dumps(formatter_code)}
      }}
    }},
    "field_mask": {{
      "paths": ["formatters"]
    }}
  }}' \\
  "{base_url}/api/v3/as/applications/{app_id}/devices/{dev_id}"'''
                else:
                    curl_cmd = f'''curl -X PUT \\
  -H "Authorization: Bearer $TTS_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "end_device": {{
      "ids": {{
        "device_id": "{dev_id}",
        "application_ids": {{
          "application_id": "{app_id}"
        }}
      }},
      "formatters": {{
        "up_formatter": "{formatter_type}"
      }}
    }},
    "field_mask": {{
      "paths": ["formatters"]
    }}
  }}' \\
  "{base_url}/api/v3/as/applications/{app_id}/devices/{dev_id}"'''

                return [TextContent(
                    type="text",
                    text=f"📋 cURL Command zum Setzen des Formatters:\n\n```bash\n{curl_cmd}\n```\n\n" +
                         f"💡 Hinweise:\n" +
                         f"- Setze TTS_API_KEY als Environment Variable: export TTS_API_KEY=your-api-key\n" +
                         f"- Oder ersetze $TTS_API_KEY direkt im Command\n" +
                         f"- Formatter Type: {formatter_type}\n" +
                         f"- Code Größe: {len(formatter_code)} Zeichen"
                )]

            elif command_type == "cli":
                # Generate TTS CLI command
                if formatter_code:
                    cli_cmd = f'''# Speichere den Formatter Code in einer Datei
cat > formatter.js << 'EOF'
{formatter_code}
EOF

# Setze den Formatter mit TTS CLI
ttn-lw-cli end-devices set {dev_id} \\
  --application-id {app_id} \\
  --formatters.up-formatter {formatter_type} \\
  --formatters.up-formatter-parameter ./formatter.js'''
                else:
                    cli_cmd = f'''ttn-lw-cli end-devices set {dev_id} \\
  --application-id {app_id} \\
  --formatters.up-formatter {formatter_type}'''

                return [TextContent(
                    type="text",
                    text=f"📋 TTS CLI Command:\n\n```bash\n{cli_cmd}\n```\n\n" +
                         f"💡 CLI Installation:\n" +
                         f"```bash\n" +
                         f"curl -L https://github.com/TheThingsNetwork/lorawan-stack/releases/latest/download/ttn-lw-cli-linux-amd64.zip -o ttn-cli.zip\n" +
                         f"unzip ttn-cli.zip\n" +
                         f"```"
                )]

            elif command_type == "python":
                # Generate Python script
                python_script = f'''import requests
import json

TTS_HOST = "{base_url}"
API_KEY = "your-api-key-here"  # Ersetze mit deinem API Key
APP_ID = "{app_id}"
DEVICE_ID = "{dev_id}"

# Formatter Code
formatter_code = """{formatter_code}"""

# Prepare Payload
payload = {{
    "end_device": {{
        "ids": {{
            "device_id": DEVICE_ID,
            "application_ids": {{
                "application_id": APP_ID
            }}
        }},
        "formatters": {{
            "up_formatter": "{formatter_type}",
            "up_formatter_parameter": formatter_code
        }}
    }},
    "field_mask": {{
        "paths": ["formatters"]
    }}
}}

# Send Request
headers = {{
    "Authorization": f"Bearer {{API_KEY}}",
    "Content-Type": "application/json"
}}

url = f"{{TTS_HOST}}/api/v3/as/applications/{{APP_ID}}/devices/{{DEVICE_ID}}"

response = requests.put(url, json=payload, headers=headers)

if response.status_code == 200:
    print("✅ Formatter erfolgreich gesetzt!")
    print(response.json())
else:
    print(f"❌ Fehler: {{response.status_code}}")
    print(response.text)
'''

                return [TextContent(
                    type="text",
                    text=f"📋 Python Script:\n\n```python\n{python_script}\n```\n\n" +
                         f"💡 Verwendung:\n" +
                         f"1. Speichere als `set_formatter.py`\n" +
                         f"2. Installiere requests: `pip install requests`\n" +
                         f"3. Ersetze API-Key\n" +
                         f"4. Führe aus: `python set_formatter.py`"
                )]

        # gRPC-specific tools (via HTTP/gRPC Gateway)
        # NOTE: These may not work on all TTS installations
        elif name == "set_device_formatters":
            app_id = arguments["application_id"]
            dev_id = arguments["device_id"]

            # Build payload for AsEndDeviceRegistry.Set
            end_device = {
                "ids": {
                    "device_id": dev_id,
                    "application_ids": {
                        "application_id": app_id
                    }
                }
            }

            field_paths = []

            # Set uplink formatter if provided
            if "uplink_formatter" in arguments:
                if "formatters" not in end_device:
                    end_device["formatters"] = {}
                end_device["formatters"]["up_formatter"] = arguments["uplink_formatter"]
                field_paths.append("formatters.up_formatter")

                if "uplink_formatter_parameter" in arguments:
                    end_device["formatters"]["up_formatter_parameter"] = arguments["uplink_formatter_parameter"]
                    field_paths.append("formatters.up_formatter_parameter")

            # Set downlink formatter if provided
            if "downlink_formatter" in arguments:
                if "formatters" not in end_device:
                    end_device["formatters"] = {}
                end_device["formatters"]["down_formatter"] = arguments["downlink_formatter"]
                field_paths.append("formatters.down_formatter")

                if "downlink_formatter_parameter" in arguments:
                    end_device["formatters"]["down_formatter_parameter"] = arguments["downlink_formatter_parameter"]
                    field_paths.append("formatters.down_formatter_parameter")

            data = {
                "end_device": end_device,
                "field_mask": {
                    "paths": field_paths
                }
            }

            path = f"as/applications/{app_id}/devices/{dev_id}"
            result = await tts_client.put(path, data)
            return [TextContent(
                type="text",
                text=f"✅ Payload formatters updated for device '{dev_id}':\n\n{json.dumps(result, indent=2)}"
            )]

        elif name == "downlink_queue_push":
            app_id = arguments["application_id"]
            dev_id = arguments["device_id"]

            downlink = {
                "f_port": arguments["f_port"],
                "frm_payload": arguments["frm_payload"],
                "priority": arguments.get("priority", "NORMAL"),
                "confirmed": arguments.get("confirmed", False)
            }

            data = {
                "downlinks": [downlink]
            }

            path = f"as/applications/{app_id}/devices/{dev_id}/down/push"
            result = await tts_client.post(path, data)
            return [TextContent(
                type="text",
                text=f"✅ Downlink queued successfully:\n\n{json.dumps(result, indent=2)}"
            )]

        elif name == "downlink_queue_list":
            app_id = arguments["application_id"]
            dev_id = arguments["device_id"]

            path = f"as/applications/{app_id}/devices/{dev_id}/down"
            result = await tts_client.get(path)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "downlink_queue_replace":
            app_id = arguments["application_id"]
            dev_id = arguments["device_id"]
            downlinks = arguments["downlinks"]

            data = {
                "downlinks": downlinks
            }

            path = f"as/applications/{app_id}/devices/{dev_id}/down/replace"
            result = await tts_client.post(path, data)
            return [TextContent(
                type="text",
                text=f"✅ Downlink queue replaced with {len(downlinks)} message(s):\n\n{json.dumps(result, indent=2)}"
            )]

        elif name == "simulate_uplink":
            app_id = arguments["application_id"]
            dev_id = arguments["device_id"]

            uplink = {
                "f_port": arguments["f_port"],
                "frm_payload": arguments["frm_payload"],
                "confirmed": arguments.get("confirmed", False),
                "rx_metadata": arguments.get("rx_metadata", [])
            }

            data = {
                "end_device_ids": {
                    "device_id": dev_id,
                    "application_ids": {
                        "application_id": app_id
                    }
                },
                "uplink_message": uplink
            }

            path = f"as/applications/{app_id}/devices/{dev_id}/up/simulate"
            result = await tts_client.post(path, data)
            return [TextContent(
                type="text",
                text=f"✅ Uplink simulated successfully:\n\n{json.dumps(result, indent=2)}"
            )]

        elif name == "decode_uplink":
            app_id = arguments["application_id"]
            dev_id = arguments.get("device_id")

            data = {
                "f_port": arguments["f_port"],
                "frm_payload": arguments["frm_payload"]
            }

            if dev_id:
                # Use device-specific formatter
                path = f"as/applications/{app_id}/devices/{dev_id}/up/decode"
            else:
                # Use application-level formatter
                path = f"as/applications/{app_id}/up/decode"

            result = await tts_client.post(path, data)
            return [TextContent(
                type="text",
                text=f"✅ Uplink decoded:\n\n{json.dumps(result, indent=2)}"
            )]

        elif name == "encode_downlink":
            app_id = arguments["application_id"]
            dev_id = arguments.get("device_id")

            data = {
                "decoded_payload": arguments["decoded_payload"]
            }

            if "f_port" in arguments:
                data["f_port"] = arguments["f_port"]

            if dev_id:
                # Use device-specific formatter
                path = f"as/applications/{app_id}/devices/{dev_id}/down/encode"
            else:
                # Use application-level formatter
                path = f"as/applications/{app_id}/down/encode"

            result = await tts_client.post(path, data)
            return [TextContent(
                type="text",
                text=f"✅ Downlink encoded:\n\n{json.dumps(result, indent=2)}"
            )]

        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP Error {e.response.status_code}: {e.response.text}"
        return [TextContent(
            type="text",
            text=error_msg
        )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def main():
    """Run the MCP server"""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
