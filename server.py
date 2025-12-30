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
            description="List all applications accessible with the API key. Returns application IDs, names, and descriptions.",
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
            description="Get detailed information about a specific application by its ID",
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
                        "description": "User ID who owns the application"
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
                "required": ["user_id", "application_id", "name"]
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
            name="list_devices",
            description="List all end devices in an application",
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
            description="Get detailed information about a specific end device",
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
            description="Create a fully configured OTAA device with registration in Identity Server, Join Server, Network Server, and Application Server",
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
            description="Get uplink messages from a device (recent data sent by the device)",
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
            user_id = arguments["user_id"]
            app_id = arguments["application_id"]

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

            path = f"users/{user_id}/applications"
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
