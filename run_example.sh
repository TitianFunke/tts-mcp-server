#!/bin/bash

# Beispiel-Skript zum Starten des MCP-Servers mit verschiedenen Konfigurationen
# Passe die Werte an deine Umgebung an

echo "The Things Stack MCP Server - Run Example"
echo "==========================================="
echo ""
echo "Wähle deine Region:"
echo "1) Europa (eu1.cloud.thethings.network)"
echo "2) Nordamerika (nam1.cloud.thethings.network)"
echo "3) Australien (au1.cloud.thethings.network)"
echo "4) Eigene URL eingeben"
echo ""
read -p "Option [1-4]: " region_choice

case $region_choice in
    1)
        TTS_BASE_URL="https://eu1.cloud.thethings.network"
        ;;
    2)
        TTS_BASE_URL="https://nam1.cloud.thethings.network"
        ;;
    3)
        TTS_BASE_URL="https://au1.cloud.thethings.network"
        ;;
    4)
        read -p "Basis-URL eingeben (z.B. https://your-instance.com): " TTS_BASE_URL
        ;;
    *)
        echo "Ungültige Option, verwende Europa als Standard"
        TTS_BASE_URL="https://eu1.cloud.thethings.network"
        ;;
esac

echo ""
read -p "API-Key eingeben (NNSXS.XXX...): " TTS_API_KEY
echo ""

if [ -z "$TTS_API_KEY" ]; then
    echo "Fehler: API-Key darf nicht leer sein!"
    exit 1
fi

echo "Konfiguration:"
echo "  Base URL: $TTS_BASE_URL"
echo "  API Key: ${TTS_API_KEY:0:10}..."
echo ""
echo "Starte MCP-Server..."
echo ""

docker run --rm -i \
    -e TTS_BASE_URL="$TTS_BASE_URL" \
    -e TTS_API_KEY="$TTS_API_KEY" \
    things-stack-mcp
