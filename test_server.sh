#!/bin/bash

# Test script for The Things Stack MCP Server
# This script tests the basic functionality of the MCP server

set -e

echo "Starting Things Stack MCP Server Test..."
echo "=========================================="
echo ""

# Check if environment variables are set
if [ -z "$TTS_API_KEY" ]; then
    echo "Error: TTS_API_KEY environment variable not set!"
    echo "Please set it with: export TTS_API_KEY=NNSXS.XXX..."
    exit 1
fi

if [ -z "$TTS_BASE_URL" ]; then
    echo "Using default base URL: https://eu1.cloud.thethings.network"
    TTS_BASE_URL="https://eu1.cloud.thethings.network"
fi

# Check if API key is placeholder
if [ "$TTS_API_KEY" = "NNSXS.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" ]; then
    echo "Error: TTS_API_KEY is still the placeholder value!"
    echo "Please set your actual API key."
    exit 1
fi

echo "Configuration:"
echo "  Base URL: $TTS_BASE_URL"
echo "  API Key: ${TTS_API_KEY:0:10}..."
echo ""

# Build the Docker image
echo "Building Docker image..."
docker build -t things-stack-mcp . --quiet
echo "Build completed."
echo ""

# Test 1: List Applications
echo "Test 1: Listing applications..."
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"list_applications","arguments":{}},"id":1}' | \
    docker run --rm -i \
    -e TTS_BASE_URL="$TTS_BASE_URL" \
    -e TTS_API_KEY="$TTS_API_KEY" \
    things-stack-mcp 2>&1 | head -20
echo ""

# Test 2: List Gateways
echo "Test 2: Listing gateways..."
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"list_gateways","arguments":{}},"id":2}' | \
    docker run --rm -i \
    -e TTS_BASE_URL="$TTS_BASE_URL" \
    -e TTS_API_KEY="$TTS_API_KEY" \
    things-stack-mcp 2>&1 | head -20
echo ""

echo "=========================================="
echo "Tests completed!"
echo ""
echo "If you see JSON responses above, the server is working correctly."
echo "You can now use the MCP server with Claude Desktop or other MCP clients."
