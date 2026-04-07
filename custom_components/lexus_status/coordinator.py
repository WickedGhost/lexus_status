"""DataUpdateCoordinator for the Lexus UX300e – polls Lexus Connected Services."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_LEXUS_PASSWORD,
    CONF_LEXUS_USERNAME,
    CONF_LEXUS_VIN,
    CONF_SCAN_INTERVAL,
    CONF_UPDATE_MODE,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_UPDATE_MODE,
    DOMAIN,
    LEXUS_BRAND,
    UPDATE_MODE_MANUAL,
)

_LOGGER = logging.getLogger(__name__)


class LexusTibberCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Poll Lexus Connected Services for EV status data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialise coordinator."""
        self.entry = entry

        update_mode: str = entry.options.get(
            CONF_UPDATE_MODE,
            entry.data.get(CONF_UPDATE_MODE, DEFAULT_UPDATE_MODE),
        )

        if update_mode == UPDATE_MODE_MANUAL:
            interval = None
        else:
            scan_interval: int = entry.options.get(
                CONF_SCAN_INTERVAL,
                entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            )
            interval = timedelta(minutes=scan_interval)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=interval,
        )

        _LOGGER.debug(
            "Update mode: %s | interval: %s",
            update_mode,
            interval,
        )

        self._lexus_client: Any | None = None
        self._lexus_vin: str | None = entry.data.get(CONF_LEXUS_VIN)

    # ------------------------------------------------------------------
    # Lexus helpers
    # ------------------------------------------------------------------

    async def _get_lexus_client(self) -> Any:
        """Return an authenticated MyT client, (re-)creating it if needed."""
        if self._lexus_client is not None:
            return self._lexus_client

        try:
            from pytoyoda.client import MyT  # noqa: PLC0415
        except ImportError as err:
            raise UpdateFailed(
                "pytoyoda library is not installed. "
                "Add pytoyoda>=5.0.0 to your requirements."
            ) from err

        client = MyT(
            username=self.entry.data[CONF_LEXUS_USERNAME],
            password=self.entry.data[CONF_LEXUS_PASSWORD],
            use_metric=True,
            brand=LEXUS_BRAND,
        )
        await client.login()
        self._lexus_client = client
        return client

    async def _fetch_lexus_data(self) -> dict[str, Any]:
        """Fetch EV status from Lexus Connected Services via pytoyoda."""
        client = await self._get_lexus_client()
        vehicles = await client.get_vehicles()

        if not vehicles:
            raise UpdateFailed("No vehicles found in Lexus account.")

        # Prefer the VIN the user selected during config; fall back to first
        vehicle = None
        if self._lexus_vin:
            vehicle = next(
                (v for v in vehicles if v.vin == self._lexus_vin), None
            )
        if vehicle is None:
            vehicle = vehicles[0]

        await vehicle.update()

        ev = vehicle.electric_status

        return {
            "vin": vehicle.vin,
            "alias": vehicle.alias or "Lexus UX300e",
            "battery_level": ev.battery_level if ev else None,
            "charging_status": ev.charging_status if ev else None,
            "range_km": ev.ev_range if ev else None,
            "remaining_charge_time": ev.remaining_charge_time if ev else None,
            "last_lexus_update": datetime.now(timezone.utc),
        }

    # ------------------------------------------------------------------
    # Core update loop
    # ------------------------------------------------------------------

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Lexus Connected Services."""
        try:
            return await self._fetch_lexus_data()
        except UpdateFailed:
            raise
        except Exception:
            # Invalidate client so next attempt re-authenticates
            self._lexus_client = None
            try:
                return await self._fetch_lexus_data()
            except Exception as err:
                raise UpdateFailed(f"Failed to read Lexus data: {err}") from err

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    async def async_shutdown(self) -> None:
        """Release resources."""
        self._lexus_client = None
