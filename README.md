# Lexus UX300e Integration for Home Assistant

A [Home Assistant](https://www.home-assistant.io/) custom component that reads battery status from a **Lexus UX300e** (or any other Toyota/Lexus EV on the EU platform) via Lexus Connected Services and exposes it as Home Assistant sensor entities.

---

## How it works

```
Lexus Connected Services API  ──►  Home Assistant sensors
       (battery, range, charging)
```

Every _N_ minutes (configurable, default 30 min) the integration authenticates against Toyota / Lexus Connected Services and reads:

- Battery state of charge (%)
- Estimated electric range (km)
- Charging status
- Remaining charge time (min)
- Timestamp of the last successful data fetch

You can then use these sensors in automations — for example, to notify you when the car reaches a target charge level, or to feed the SOC into a smart home energy dashboard.

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
2. Add `https://github.com/your-repo/lexus-tibber-integration` with category **Integration**.
3. Search for **Lexus UX300e** and install it.
4. Restart Home Assistant.

### Manual

1. Copy the `custom_components/lexus_tibber` folder into your HA `config/custom_components/` directory.
2. Restart Home Assistant.

---

## Configuration

Go to **Settings → Devices & Services → Add Integration** and search for **Lexus UX300e**.

The setup wizard walks you through three steps:

| Step | What you enter |
|---|---|
| 1 | Lexus email and password |
| 2 | Select your UX300e (skipped if you only have one vehicle) |
| 3 | Polling interval in minutes (5 – 240, default 30) |

---

## Entities created

| Entity | Description |
|---|---|
| `sensor.<name>_battery_level` | State of charge in % |
| `sensor.<name>_electric_range` | Remaining electric range in km |
| `sensor.<name>_charging_status` | Raw charging status string from Lexus API (e.g. `charging`, `connected`, `disconnected`) |
| `sensor.<name>_remaining_charge_time` | Minutes until fully charged |
| `sensor.<name>_last_synced_from_lexus` | Timestamp of the last successful data fetch from the Lexus API |

The `battery_level` sensor also exposes `vin` and `last_lexus_update` as extra state attributes.

---

## Options

After setup you can change the polling interval via **Settings → Devices & Services → Lexus UX300e → Configure**.

---

## Using with Tibber

The [official Tibber integration](https://www.home-assistant.io/integrations/tibber/) and community add-ons expose real-time electricity prices in Home Assistant. You can build automations that combine the Lexus battery sensors from this integration with Tibber price data to, for example:

- Start charging when the electricity price drops below a threshold **and** the battery is below 80 %.
- Send a push notification when the car is fully charged during a cheap-rate window.

---

## Troubleshooting

* **`cannot_connect`** during setup – Check that your Lexus credentials work in the MyLexus mobile app and that your HA instance has internet access.
* **`missing_library`** – Make sure `pytoyoda>=5.0.0` is listed in the integration manifest and that HA has installed it (check HA logs on startup).
* **EU accounts only** – `pytoyoda` only supports Toyota Connected Europe. North American / Asian Toyota/Lexus accounts are not supported.
* **Battery level not updating** – The Lexus Connected Services API only refreshes the car's data when the car is awake (ignition on, or actively charging). Values can be stale for parked vehicles.

---

## Architecture

```
custom_components/lexus_tibber/
├── __init__.py          # Integration setup / teardown
├── config_flow.py       # Multi-step UI configuration
├── const.py             # Domain constants and options
├── coordinator.py       # DataUpdateCoordinator (polls Lexus API)
├── manifest.json        # HA integration manifest
├── sensor.py            # Sensor platform entities
├── strings.json         # UI string keys
└── translations/
    └── en.json          # English translations
```

---

## License

MIT

       (battery SOC %)                (sensors)          (setStateOfCharge)
```

Every _N_ minutes (configurable, default 30 min) the integration:

1. Authenticates against the Toyota / Lexus Connected Services cloud and reads the current battery SOC, charging status, and electric range of your UX300e.
2. Exposes these values as Home Assistant sensor entities.
3. Calls the Tibber API mutation `setStateOfCharge` to keep your Tibber vehicle profile in sync – ensuring Tibber schedules charging at the right time.

---

## Prerequisites

| Requirement | Notes |
|---|---|
| Home Assistant ≥ 2024.1 | Core integration APIs used |
| Lexus Connected Services account | EU accounts only — same credentials as the MyLexus / Lexus Link app |
| Lexus UX300e (or other Toyota/Lexus EV on the EU platform) | Must have a connected-services subscription |
| Tibber account | Free tier is sufficient |
| Tibber personal access token | Obtain at <https://developer.tibber.com/settings/access-token> |
| Lexus UX300e registered in Tibber | Add it via the Tibber app → **My home → Electric vehicles** |

---

## Installation

### Via HACS (recommended)

1. Open HACS → **Integrations** → ⋮ → **Custom repositories**.
2. Add `https://github.com/your-repo/lexus-tibber-integration` with category **Integration**.
3. Search for **Lexus Tibber Integration** and install it.
4. Restart Home Assistant.

### Manual

1. Copy the `custom_components/lexus_tibber` folder into your HA `config/custom_components/` directory.
2. Restart Home Assistant.

---

## Configuration

Go to **Settings → Devices & Services → Add Integration** and search for **Lexus Tibber Integration**.

The setup wizard walks you through six steps:

| Step | What you enter |
|---|---|
| 1 | Lexus email and password |
| 2 | Select your UX300e (skipped if you only have one vehicle) |
| 3 | Your Tibber personal access token |
| 4 | Select your Tibber home (skipped if you only have one) |
| 5 | Select the EV registered in Tibber (auto-discovered, or entered manually if not found) |
| 6 | Polling interval in minutes (5 – 240, default 30) |

---

## Entities created

| Entity | Description |
|---|---|
| `sensor.<name>_battery_level` | State of charge in % |
| `sensor.<name>_electric_range` | Remaining electric range in km |
| `sensor.<name>_charging_status` | Raw charging status string from Lexus API (e.g. `charging`, `connected`, `disconnected`) |
| `sensor.<name>_remaining_charge_time` | Minutes until fully charged |
| `sensor.<name>_last_synced_from_lexus` | Timestamp of the last successful data fetch from the Lexus API |
| `sensor.<name>_tibber_sync_status` | `Success` / `Failed` / `Pending` |

---

## Options

After setup you can change the polling interval via **Settings → Devices & Services → Lexus Tibber → Configure**.

---

## Troubleshooting

* **`cannot_connect`** during setup – Check that your Lexus credentials work in the MyLexus mobile app and that your HA instance has internet access.
* **`missing_library`** – Make sure `pytoyoda>=5.0.0` is listed in the integration manifest and that HA has installed it (check HA logs on startup).
* **EU accounts only** – `pytoyoda` only supports Toyota Connected Europe. North American / Asian Toyota/Lexus accounts are not supported.
* **Tibber sync always `Failed`** – Check the HA logs for the exact GraphQL error. Ensure the vehicle ID is correct (run `{ viewer { homes { electricVehicles { id name } } } }` in the [Tibber Explorer](https://developer.tibber.com/explorer) to find it).
* **Battery level not updating** – The Lexus Connected Services API only refreshes the car's data when the car is awake (ignition on, or actively charging). Values can be stale for parked vehicles.

---

## Architecture

```
custom_components/lexus_tibber/
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
