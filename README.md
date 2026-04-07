# HA Lexus Status

A [Home Assistant](https://www.home-assistant.io/) custom component that reads battery status from a **Lexus UX300e** (or any other Toyota/Lexus EV on the EU platform) via Lexus Connected Services and exposes it as Home Assistant sensor entities.

---

## How it works

```
Lexus Connected Services API  ──►  Home Assistant sensors
       (battery, range, charging)
```

The integration authenticates against Toyota / Lexus Connected Services and reads:

- Battery state of charge (%)
- Estimated electric range (km)
- Charging status
- Remaining charge time (min)
- Timestamp of the last successful data fetch

Data can be fetched **automatically** on a configurable interval or **on demand** via an automation or the Home Assistant service call `lexus_status.refresh`.

---

## Prerequisites

| Requirement | Notes |
|---|---|
| Home Assistant ≥ 2024.1 | Core integration APIs used |
| Lexus Connected Services account | EU accounts only — same credentials as the MyLexus / Lexus Link app |
| Lexus UX300e (or other Toyota/Lexus EV on the EU platform) | Must have a connected-services subscription |

---

## Installation

### Via HACS (recommended)

1. Open HACS → **Integrations** → ⋮ → **Custom repositories**.
2. Add `https://github.com/WickedGhost/lexus_status` with category **Integration**.
3. Search for **HA Lexus Status** and install it.
4. Restart Home Assistant.

### Manual

1. Copy the `custom_components/lexus_status` folder into your HA `config/custom_components/` directory.
2. Restart Home Assistant.

---

## Configuration

Go to **Settings → Devices & Services → Add Integration** and search for **HA Lexus Status**.

The setup wizard walks you through up to four steps:

| Step | What you enter |
|---|---|
| 1 | Lexus email and password |
| 2 | Select your vehicle (skipped if you only have one) |
| 3 | Update mode — **Periodic** or **Manual** |
| 4 | Polling interval in minutes (5 – 240, default 30) — only shown when Periodic is selected |

---

## Update modes

### Periodic (automatic polling)

The integration polls Lexus Connected Services every _N_ minutes (configurable, default 30). Useful when you want the sensors to stay current without any extra automation work.

### Manual (triggered by automation)

No automatic polling. The sensors only update when you explicitly call the `lexus_status.refresh` service. Use this when you want full control over when the car is woken up, for example only after you know the car has been driven or plugged in.

```yaml
# Example automation: refresh whenever the car is plugged in
automation:
  trigger:
    - platform: state
      entity_id: sensor.lexus_ux300e_charging_status
      to: "charging"
  action:
    - service: lexus_status.refresh
```

---

## Services

### `lexus_status.refresh`

Immediately fetches the latest status from Lexus Connected Services for all configured vehicles, regardless of the configured update mode.

| Field | Value |
|---|---|
| Service | `lexus_status.refresh` |
| Target | _(none — applies to all configured vehicles)_ |

---

## Entities created

| Entity | Description |
|---|---|
| `sensor.<name>_battery_level` | State of charge in % |
| `sensor.<name>_electric_range` | Remaining electric range in km |
| `sensor.<name>_charging_status` | Raw charging status string from the Lexus API (e.g. `charging`, `connected`, `disconnected`) |
| `sensor.<name>_remaining_charge_time` | Minutes until fully charged |
| `sensor.<name>_last_synced_from_lexus` | Timestamp of the last successful data fetch from the Lexus API |

The `battery_level` sensor also exposes `vin` and `last_lexus_update` as extra state attributes.

---

## Options

After setup you can change the update mode and polling interval via **Settings → Devices & Services → HA Lexus Status → Configure**.

---

## Troubleshooting

* **`cannot_connect`** during setup – Check that your Lexus credentials work in the MyLexus mobile app and that your HA instance has internet access.
* **`missing_library`** – Make sure `pytoyoda>=5.0.0` is listed in the integration manifest and that HA has installed it (check HA logs on startup).
* **EU accounts only** – `pytoyoda` only supports Toyota Connected Europe. North American / Asian Toyota/Lexus accounts are not supported.
* **Battery level not updating** – The Lexus Connected Services API only refreshes the car's data when the car is awake (ignition on, or actively charging). Values can be stale for parked vehicles. In Manual mode, call `lexus_status.refresh` after you know the car is awake.

* **`cannot_connect`** during setup – Check that your Lexus credentials work in the MyLexus mobile app and that your HA instance has internet access.
* **`missing_library`** – Make sure `pytoyoda>=5.0.0` is listed in the integration manifest and that HA has installed it (check HA logs on startup).
* **EU accounts only** – `pytoyoda` only supports Toyota Connected Europe. North American / Asian Toyota/Lexus accounts are not supported.
* **Tibber sync always `Failed`** – Check the HA logs for the exact GraphQL error. Ensure the vehicle ID is correct (run `{ viewer { homes { electricVehicles { id name } } } }` in the [Tibber Explorer](https://developer.tibber.com/explorer) to find it).
* **Battery level not updating** – The Lexus Connected Services API only refreshes the car's data when the car is awake (ignition on, or actively charging). Values can be stale for parked vehicles.

---

## Architecture

```
custom_components/lexus_status/
├── __init__.py          # Integration setup / teardown
├── config_flow.py       # Multi-step UI configuration
├── const.py             # Domain constants and options
├── coordinator.py       # DataUpdateCoordinator (polling + Tibber push)
├── manifest.json        # HA integration manifest
├── sensor.py            # Sensor platform entities
├── strings.json         # UI string keys
└── translations/
    └── en.json          # English translations
```

---

## License

MIT
