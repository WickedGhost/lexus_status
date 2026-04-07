"""Lexus Tibber Integration – Home Assistant entry point."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall

from .const import DOMAIN
from .coordinator import LexusTibberCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]
SERVICE_REFRESH = "refresh"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Lexus Tibber from a config entry."""
    coordinator = LexusTibberCoordinator(hass, entry)

    # Perform initial refresh – raises ConfigEntryNotReady on failure
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Reload when options change (e.g. scan_interval)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    # Register a service so automations can trigger an immediate refresh
    if not hass.services.has_service(DOMAIN, SERVICE_REFRESH):
        async def _handle_refresh(call: ServiceCall) -> None:  # noqa: ARG001
            for coord in hass.data.get(DOMAIN, {}).values():
                await coord.async_request_refresh()

        hass.services.async_register(DOMAIN, SERVICE_REFRESH, _handle_refresh)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator: LexusTibberCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_shutdown()

        # Remove the service when the last entry is unloaded
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, SERVICE_REFRESH)

    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the config entry when options are changed."""
    await hass.config_entries.async_reload(entry.entry_id)
