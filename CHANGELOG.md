# Changelog

## Version 1.3.2 - Verbesserte Tool-Beschreibungen für bessere KI-Nutzung

### 🎯 Improvements

#### Detaillierte Tool-Beschreibungen
Alle wichtigen Tools haben jetzt **ausführliche Beschreibungen**, damit die KI (Claude, etc.) besser versteht, wann sie welches Tool nutzen soll.

**Verbesserte Tools:**
- `list_applications` - Klar wann zu nutzen, was zurückgegeben wird
- `get_application` - Use-Cases explizit genannt
- `list_devices` - Zweck und Return-Werte detailliert
- `get_device` - Alle 6 Use-Cases aufgelistet
- `get_device_uplinks` - Monitoring/Debugging Use-Cases
- `create_otaa_device` - EMPFOHLEN-Tag, 4 API-Calls erklärt, alle Parameter dokumentiert
- `generate_formatter_command` - Klarer Hinweis dass es Commands generiert (nicht ausführt)

**Format der Beschreibungen:**
- Was das Tool macht
- Wann man es nutzen sollte (konkrete Use-Cases)
- Was benötigt wird (Required Parameters)
- Was zurückgegeben wird (Return Values)
- Besondere Hinweise (EMPFOHLEN, Warnings, etc.)

**Vorher:**
```
"List all applications accessible with the API key"
```

**Nachher:**
```
"List all LoRaWAN applications. Use this to: (1) See all applications a user owns,
(2) Find application IDs for further operations, (3) Get overview of existing applications.
Returns: application_id, name, description, creation date. Optional: filter by user_id."
```

### Warum wichtig?
Die KI sieht nur die `description` Felder der Tools. Bessere Beschreibungen = KI wählt das richtige Tool zur richtigen Zeit.

---

## Version 1.3.1 - gRPC Command Generator (Fix)

### 🔧 Fixes & Improvements

#### `generate_formatter_command` - Neues Helper Tool
Da die direkten gRPC-API-Calls nicht auf allen TTS-Installationen funktionieren, gibt es jetzt ein **Command-Generator-Tool**:

**Features:**
- Generiert fertige cURL Commands
- Generiert TTS CLI Commands
- Generiert Python Scripts
- Ersetzt fehleranfällige direkte API-Calls

**Verwendung:**
```json
{
  "name": "generate_formatter_command",
  "arguments": {
    "application_id": "my-app",
    "device_id": "my-sensor",
    "formatter_type": "FORMATTER_JAVASCRIPT",
    "formatter_code": "function decodeUplink(input) {...}",
    "command_type": "curl"
  }
}
```

**Output:** Ready-to-use Commands zum Kopieren & Ausführen!

#### gRPC Tools als "Experimental" markiert
- `set_device_formatters` - Funktioniert möglicherweise nicht überall
- `downlink_queue_*` - Experimentell
- `simulate_uplink` - Experimentell
- `decode_uplink` - Experimentell
- `encode_downlink` - Experimentell

**Empfehlung:** Nutze `generate_formatter_command` für Formatter-Setup!

### Dokumentation
- README mit generate_formatter_command Beispiel
- Hinweise auf experimentelle Tools
- Erklärung warum Command-Generator besser ist

---

## Version 1.3.0 - gRPC Features via HTTP/gRPC Gateway

### 🎉 Neue Features

#### Payload Formatters
- **set_device_formatters** - Setze Payload Formatter für Devices
  - JavaScript (max 64KB Code)
  - CayenneLPP
  - Repository (vordefiniert)
  - gRPC Service
  - Uplink & Downlink Formatter unabhängig konfigurierbar

- **decode_uplink** - Teste Uplink Payload Formatter
  - Dekodiere rohe Payloads (base64)
  - Device- oder Application-Level Formatter
  - FPort-Support

- **encode_downlink** - Teste Downlink Payload Formatter
  - Enkodiere JSON zu rohen Payloads
  - Device- oder Application-Level Formatter
  - Automatische FPort-Zuordnung

#### Downlink Queue Management
- **downlink_queue_push** - Füge Downlink-Nachricht zur Queue hinzu
  - FPort & Payload
  - Priority (LOWEST bis HIGHEST)
  - Confirmed Downlinks

- **downlink_queue_list** - Liste pending Downlinks
  - Zeigt komplette Queue
  - Mit Metadaten

- **downlink_queue_replace** - Ersetze komplette Queue
  - Atomare Operation
  - Batch-Downlinks

#### Testing & Simulation
- **simulate_uplink** - Simuliere Uplink-Nachrichten
  - Triggert Payload Formatter
  - Triggert Integrations (Webhooks, etc.)
  - Optional RX Metadata
  - Perfekt für Testing ohne Hardware

### Implementation
- Alle gRPC-Features über HTTP/gRPC Gateway
- Keine zusätzlichen Dependencies
- Standard HTTP/REST API Client
- Korrekte field_mask Nutzung

### Dokumentation
- README mit allen neuen Tools
- gRPC-Feature-Übersicht
- Beispiele für Payload Formatters
- Beispiele für Downlink Queue Management

---

## Version 1.2.0 - Korrekte Multi-Server Registrierung

### 🔧 Fixes

#### `create_otaa_device` - Vollständige Implementierung
Komplett überarbeitet für korrekte Device-Registrierung mit **4 separaten API-Calls**:

1. **POST** `/api/v3/applications/{app_id}/devices` (Identity Server)
2. **PUT** `/api/v3/js/applications/{app_id}/devices/{device_id}` (Join Server)
3. **PUT** `/api/v3/ns/applications/{app_id}/devices/{device_id}` (Network Server)
4. **PUT** `/api/v3/as/applications/{app_id}/devices/{device_id}` (Application Server)

**Neu:**
- ✅ Korrekte `field_mask` für jeden Server
- ✅ Error Handling mit automatischem Cleanup
- ✅ Detaillierte Success/Error Messages
- ✅ Alle Server werden korrekt konfiguriert

**Geändert:**
- Default Frequency Plan: `EU_863_870_TTN` (statt `EU_863_870`)
- Bessere Fehlerbehandlung bei partiellen Registrierungen

---

## Version 1.1.0 - OTAA Device Support

### Neue Features

#### `create_otaa_device` Tool
Vollständige OTAA-Device-Registrierung mit Konfiguration für alle Server:

**Registrierte Server:**
- ✅ **Identity Server**: Device-Metadaten (Name, Description, IDs)
- ✅ **Join Server**: Root Keys (AppKey für LoRaWAN 1.0.x)
- ✅ **Network Server**: MAC-Settings, LoRaWAN-Version, Frequency Plan
- ✅ **Application Server**: Session-Konfiguration

**Parameter:**
- `application_id` (required): Application ID
- `device_id` (required): Device ID
- `name` (required): Device Name
- `dev_eui` (required): Device EUI (16-char hex)
- `join_eui` (required): Join EUI (16-char hex)
- `app_key` (required): Application Key (32-char hex)
- `description` (optional): Device Description
- `lorawan_version` (optional): Default `MAC_V1_0_3`
- `lorawan_phy_version` (optional): Default `PHY_V1_0_3_REV_A`
- `frequency_plan_id` (optional): Default `EU_863_870`
- `supports_class_c` (optional): Default `false`

**Unterstützte LoRaWAN-Versionen:**
- MAC_V1_0_2
- MAC_V1_0_3 (Standard)
- MAC_V1_0_4
- MAC_V1_1

**Unterstützte Frequency Plans:**
- EU_863_870 (Europa, Standard)
- US_902_928 (USA)
- AU_915_928 (Australien)
- AS_923 (Asien)

### Verbesserungen

#### `create_device` Tool
- Aktualisierte Beschreibung: Weist auf `create_otaa_device` für vollständige Konfiguration hin
- Bleibt für einfache/manuelle Registrierungen verfügbar

### Beispiele

Neue Beispiel-Datei: `example_create_otaa_device.sh`
- Zeigt vollständige OTAA-Device-Erstellung
- Interaktive Nutzung mit Parametern

### Dokumentation

- README.md aktualisiert mit `create_otaa_device` Beispielen
- Hinweise zu allen Server-Registrierungen
- Parameter-Dokumentation für Frequency Plans und LoRaWAN-Versionen

---

## Version 1.0.0 - Initial Release

### Features
- MCP-Server für The Things Stack HTTP API
- Application Management (list, get, create, delete)
- Device Management (list, get, create, delete)
- Gateway Management (list, get)
- Uplink Message Retrieval
- Docker Support mit Environment-Variablen
- Claude Desktop Integration
