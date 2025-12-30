# The Things Stack MCP Server

MCP (Model Context Protocol) Server für die [The Things Stack](https://www.thethingsindustries.com/) HTTP API. Dieser Server ermöglicht die Interaktion mit The Things Industries LoRaWAN-Plattform über standardisierte MCP-Tools.

## Features

Der MCP-Server bietet folgende Tools:

### Applications
- `list_applications` - Liste alle Applications
- `get_application` - Details einer Application abrufen
- `create_application` - Neue Application erstellen
- `delete_application` - Application löschen

### Devices
- `list_devices` - Liste alle Devices einer Application
- `get_device` - Details eines Devices abrufen
- `create_device` - Neues Device registrieren (basis)
- `create_otaa_device` - OTAA-Device vollständig registrieren (Identity Server, Join Server, Network Server, Application Server)
- `delete_device` - Device löschen
- `get_device_uplinks` - Uplink-Nachrichten eines Devices abrufen

### Gateways
- `list_gateways` - Liste alle Gateways
- `get_gateway` - Details eines Gateways abrufen

## Voraussetzungen

- Docker und Docker Compose installiert
- Ein Account bei [The Things Stack](https://www.thethingsindustries.com/) oder einer eigenen Instanz
- Ein API-Key mit entsprechenden Berechtigungen

## API-Key erstellen

1. Melde dich in der [Things Stack Console](https://console.cloud.thethings.network/) an
2. Gehe zu deinem Benutzerprofil (User Settings)
3. Navigiere zu **API Keys**
4. Klicke auf **Add API Key**
5. Vergib einen Namen (z.B. "MCP Server")
6. Wähle folgende Berechtigungen:
   - Applications: Read & Write
   - Devices: Read & Write
   - Gateways: Read & Write
7. Kopiere den generierten API-Key (Format: `NNSXS.XXX...`)

## Quick Start

```bash
# 1. Docker Image bauen
docker build -t things-stack-mcp .

# 2. Testen (ersetze die Placeholder-Werte!)
export TTS_BASE_URL=https://eu1.cloud.thethings.network
export TTS_API_KEY=NNSXS.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
./test_server.sh
```

## Installation & Setup

### 1. Repository klonen / Dateien erstellen

Stelle sicher, dass alle Dateien im Projektverzeichnis vorhanden sind:
```
├── server.py                            # MCP-Server Implementation
├── requirements.txt                     # Python-Abhängigkeiten
├── Dockerfile                           # Docker Image Definition
├── docker-compose.yml                   # Docker Compose Konfiguration
├── claude_desktop_config.example.json   # Claude Desktop Beispielkonfiguration
├── test_server.sh                       # Test-Skript
├── run_example.sh                       # Interaktives Start-Skript
└── README.md                            # Diese Datei
```

### 2. Docker Image bauen

```bash
docker build -t things-stack-mcp .
```

### 3. Konfiguration

**Verfügbare Regions:**
- Europa: `https://eu1.cloud.thethings.network`
- Nordamerika: `https://nam1.cloud.thethings.network`
- Australien: `https://au1.cloud.thethings.network`
- Eigene Instanz: `https://your-instance.example.com`

Die Umgebungsvariablen werden direkt im Docker-Aufruf angegeben (siehe nächster Abschnitt).

## Verwendung

### Mit MCP-kompatiblen Clients

Der Server kann mit jedem MCP-kompatiblen Client verwendet werden (z.B. Claude Desktop App).

#### Konfiguration für Claude Desktop

Füge in der Claude Desktop Konfiguration folgendes hinzu:

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

**Wichtig:** Ersetze `NNSXS.XXX...` mit deinem echten API-Key und passe die Region an.

**Tipp:** Du kannst die Datei `claude_desktop_config.example.json` als Vorlage verwenden.

### Interaktiver Start

Nutze das interaktive Skript für einfache Konfiguration:

```bash
./run_example.sh
```

Das Skript fragt nach deiner Region und dem API-Key und startet den Server.

### Direkter Test mit Docker

```bash
# Server interaktiv starten
docker run --rm -i \
  -e TTS_BASE_URL=https://eu1.cloud.thethings.network \
  -e TTS_API_KEY=NNSXS.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX \
  things-stack-mcp

# Beispiel: Applications auflisten
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"list_applications","arguments":{}},"id":1}' | \
docker run --rm -i \
  -e TTS_BASE_URL=https://eu1.cloud.thethings.network \
  -e TTS_API_KEY=NNSXS.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX \
  things-stack-mcp
```

## Beispiele

### Application erstellen

```json
{
  "name": "create_application",
  "arguments": {
    "user_id": "dein-user-id",
    "application_id": "my-app",
    "name": "Meine Application",
    "description": "Test Application"
  }
}
```

### OTAA-Device vollständig registrieren (empfohlen)

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

Dieses Tool führt **4 separate API-Calls** aus, um das Device in allen benötigten Servern zu registrieren:

1. **POST** `/api/v3/applications/{app_id}/devices` - Identity Server
   - Metadaten (Name, IDs, Description)
   - Server-Adressen

2. **PUT** `/api/v3/js/applications/{app_id}/devices/{device_id}` - Join Server
   - Root Keys (AppKey für OTAA)
   - Authentifizierung

3. **PUT** `/api/v3/ns/applications/{app_id}/devices/{device_id}` - Network Server
   - MAC-Settings
   - LoRaWAN-Version & PHY-Version
   - Frequency Plan
   - Class B/C Support

4. **PUT** `/api/v3/as/applications/{app_id}/devices/{device_id}` - Application Server
   - Device-IDs
   - Session-Konfiguration

**Wichtige Parameter:**
- `app_key`: 32-stelliger Hex-String (128-bit Schlüssel)
- `dev_eui` & `join_eui`: 16-stellige Hex-Strings (64-bit)
- `frequency_plan_id`: Gängige Werte:
  - `EU_863_870_TTN` - Europa (Standard)
  - `US_902_928` - USA
  - `AU_915_928` - Australien
  - `AS_923` - Asien
- `lorawan_version`: `MAC_V1_0_2`, `MAC_V1_0_3`, `MAC_V1_0_4`, `MAC_V1_1`

### Device registrieren (basis)

```json
{
  "name": "create_device",
  "arguments": {
    "application_id": "my-app",
    "device_id": "my-device-01",
    "name": "Sensor 01",
    "dev_eui": "70B3D57ED0000001",
    "join_eui": "0000000000000000"
  }
}
```

**Hinweis**: Verwende besser `create_otaa_device` für eine vollständige Registrierung.

### Uplink-Daten abrufen

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

## Entwicklung

### Lokale Entwicklung ohne Docker

```bash
# Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate  # Auf Windows: venv\Scripts\activate

# Dependencies installieren
pip install -r requirements.txt

# Environment-Variablen setzen
export TTS_BASE_URL=https://eu1.cloud.thethings.network
export TTS_API_KEY=NNSXS.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Server starten
python server.py
```

## Troubleshooting

### Authentifizierungsfehler (401)
- Überprüfe, ob dein API-Key korrekt angegeben ist
- Stelle sicher, dass der API-Key die erforderlichen Berechtigungen hat
- Prüfe, ob der API-Key noch gültig ist
- Der API-Key sollte mit `NNSXS.` beginnen

### Verbindungsfehler
- Überprüfe die `TTS_BASE_URL` (muss mit `https://` beginnen)
- Stelle sicher, dass du die richtige Region verwendest
- Prüfe deine Netzwerkverbindung
- Bei selbst-gehosteten Instanzen: Prüfe Firewall und SSL-Zertifikate

### Device kann nicht erstellt werden
- `dev_eui` und `join_eui` müssen gültige 64-bit Hex-Strings sein (16 Zeichen)
- `device_id` darf nur Kleinbuchstaben, Zahlen und Bindestriche enthalten
- Die Application muss bereits existieren

### MCP Server startet nicht in Claude Desktop
- Prüfe die JSON-Syntax in der Claude Desktop Konfiguration
- Stelle sicher, dass das Docker-Image gebaut wurde: `docker build -t things-stack-mcp .`
- Prüfe die Docker-Logs: `docker logs <container-id>`

## API-Referenzen

- [The Things Stack HTTP API Dokumentation](https://www.thethingsindustries.com/docs/api/reference/http/)
- [Authentication](https://www.thethingsindustries.com/docs/api/concepts/auth/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

## Lizenz

MIT

## Autor

Erstellt mit Claude Code
