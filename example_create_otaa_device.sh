#!/bin/bash

# Beispiel-Skript für die Erstellung eines OTAA-Devices
# Dieses Skript zeigt, wie man ein vollständig konfiguriertes OTAA-Device erstellt

echo "Things Stack - OTAA Device Erstellen"
echo "====================================="
echo ""
echo "Dieses Skript demonstriert die Verwendung des create_otaa_device Tools."
echo "Das Device wird in allen benötigten Servern registriert:"
echo "  - Identity Server (Metadaten)"
echo "  - Join Server (Root Keys)"
echo "  - Network Server (MAC Settings)"
echo "  - Application Server (Session Config)"
echo ""

# Umgebungsvariablen überprüfen
if [ -z "$TTS_BASE_URL" ]; then
    echo "TTS_BASE_URL nicht gesetzt. Verwende Standard: https://eu1.cloud.thethings.network"
    export TTS_BASE_URL="https://eu1.cloud.thethings.network"
fi

if [ -z "$TTS_API_KEY" ]; then
    echo "Fehler: TTS_API_KEY muss gesetzt sein!"
    echo "Beispiel: export TTS_API_KEY=NNSXS.XXX..."
    exit 1
fi

# Parameter
APPLICATION_ID="${1:-my-test-app}"
DEVICE_ID="${2:-my-otaa-device-01}"
DEV_EUI="${3:-70B3D57ED0000001}"
JOIN_EUI="${4:-0000000000000000}"
APP_KEY="${5:-00112233445566778899AABBCCDDEEFF}"

echo "Parameter:"
echo "  Application ID: $APPLICATION_ID"
echo "  Device ID:      $DEVICE_ID"
echo "  DevEUI:         $DEV_EUI"
echo "  JoinEUI:        $JOIN_EUI"
echo "  AppKey:         $APP_KEY"
echo ""
echo "Erstelle OTAA-Device..."
echo ""

# JSON Payload für MCP Tool
PAYLOAD=$(cat <<EOF
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "create_otaa_device",
    "arguments": {
      "application_id": "$APPLICATION_ID",
      "device_id": "$DEVICE_ID",
      "name": "OTAA Test Device",
      "description": "Vollständig konfiguriertes OTAA-Device für Tests",
      "dev_eui": "$DEV_EUI",
      "join_eui": "$JOIN_EUI",
      "app_key": "$APP_KEY",
      "lorawan_version": "MAC_V1_0_3",
      "lorawan_phy_version": "PHY_V1_0_3_REV_A",
      "frequency_plan_id": "EU_863_870",
      "supports_class_c": false
    }
  },
  "id": 1
}
EOF
)

# Device erstellen
echo "$PAYLOAD" | docker run --rm -i \
  -e TTS_BASE_URL="$TTS_BASE_URL" \
  -e TTS_API_KEY="$TTS_API_KEY" \
  things-stack-mcp

echo ""
echo "====================================="
echo "Fertig!"
echo ""
echo "Das Device sollte jetzt in allen Servern registriert sein und ist bereit"
echo "für OTAA-Joins. Du kannst es in der Things Stack Console überprüfen."
