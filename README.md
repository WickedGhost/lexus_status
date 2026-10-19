# HA Lexus Status

Monitor your Lexus EV from [Home Assistant](https://www.home-assistant.io/) using Lexus Connected Services. The integration supports the UX300e and other Toyota/Lexus electric vehicles on the **European platform**.

It provides battery level, electric range, charging status, remaining charge time, and the time of the last successful update. Choose automatic polling or refresh the data on demand.

## Release notes

### v1.0.3
- Load `pytoyoda` through Home Assistant's integration import path to avoid blocking the event loop during setup and updates

### v1.0.2
- Cleaned up the remaining stale Tibber naming and documentation references
- Updated compatibility wording and validation checklist for Home Assistant Core 2026.9.1
- Standardized the remaining charge time sensor unit to Home Assistant's official minutes unit

---

## Features

```
Lexus Connected Services  ->  HA Lexus Status  ->  Home Assistant sensors
```

- Battery charge level and estimated electric range
- Charging state and estimated time remaining to full charge
- Timestamp of the most recent successful data fetch
- Periodic polling or manual refresh, configured per entry

---

## Prerequisites

| Requirement | Details |
|---|---|
| Home Assistant | Core 2024.1 or newer |
| Lexus account | European Toyota Connected Services account; use your MyLexus / Lexus Link credentials |
| Vehicle | Lexus UX300e or another supported Toyota/Lexus EV on the EU platform, with connected services enabled |

---

## Installation

### HACS (recommended)

1. In HACS, open **Integrations** and choose **Custom repositories** from the menu.
2. Add `https://github.com/WickedGhost/lexus_status` with the **Integration** category.
3. Find **HA Lexus Status**, install it, then restart Home Assistant.

### Manual

1. Copy `custom_components/lexus_status` into `config/custom_components/`.
2. Restart Home Assistant.

---

## Configuration

Go to **Settings → Devices & Services → Add Integration**, then search for **HA Lexus Status**. Enter your Lexus account credentials and select a vehicle if more than one is found.

Choose an update mode. Periodic mode also asks for an interval between 5 and 240 minutes (default: 30 minutes).

## Updates

**Periodic:** Polls Lexus Connected Services at the selected interval. The default is 30 minutes.

**Manual:** Disables scheduled polling. Call `lexus_status.refresh` from an automation or the Home Assistant UI when you want to request an update. This is useful when you want to control when Lexus Connected Services is contacted.

```yaml
# Example: refresh after the charging sensor reports that charging has started
automation:
  trigger:
    - platform: state
      entity_id: sensor.lexus_ux300e_charging_status
      to: "charging"
  action:
    - action: lexus_status.refresh
```

---

## Services

### `lexus_status.refresh`

Fetches the latest status for every configured Lexus Status entry, regardless of its update mode. The service has no target fields.

---

## Entities created

| Sensor | Value |
|---|---|
| Battery level | State of charge (%) |
| Electric range | Estimated remaining range (km) |
| Charging status | Status reported by Lexus (for example, `charging` or `connected`) |
| Remaining charge time | Estimated minutes until fully charged |
| Last synced from Lexus | Timestamp of the last successful data fetch |

The battery-level sensor also exposes the vehicle `vin` and `last_lexus_update` as state attributes.

---

## Options

After setup you can change the update mode and polling interval via **Settings → Devices & Services → HA Lexus Status → Configure**.

---

## Compatibility

The integration targets Home Assistant Core **2024.1 and newer**. Its config-flow, coordinator, and platform setup APIs were checked against Core **2026.10.2**. That was a source/API compatibility review, not an end-to-end run inside a 2026.10.2 Home Assistant instance.

Home Assistant resolves the `pytoyoda>=5.0.0` dependency declared in the integration manifest. The import is at module scope so Home Assistant can load it through its integration import executor rather than blocking the event loop.

---

## Troubleshooting

| Symptom | What to check |
|---|---|
| `cannot_connect` during setup | Confirm the credentials work in the MyLexus / Lexus Link app and that Home Assistant has internet access. |
| `missing_library` | Restart Home Assistant after installation and check the logs for dependency installation errors. |
| Account is unsupported | Only Toyota Connected Europe accounts are supported; North American and Asian accounts are not supported by `pytoyoda`. |
| Sensor values look stale | Lexus may only refresh vehicle data while the car is awake or charging. In Manual mode, call `lexus_status.refresh` when the vehicle is available. |

---

## Architecture

```
custom_components/lexus_status/
├── __init__.py          # Integration setup / teardown
├── config_flow.py       # Multi-step UI configuration
├── const.py             # Domain constants and options
├── coordinator.py        # DataUpdateCoordinator and Lexus refresh logic
├── manifest.json        # HA integration manifest
├── sensor.py            # Sensor platform entities
├── strings.json         # UI string keys
└── translations/
    └── en.json          # English translations
```

---

## License

MIT
