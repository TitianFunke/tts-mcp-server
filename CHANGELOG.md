# Changelog

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
