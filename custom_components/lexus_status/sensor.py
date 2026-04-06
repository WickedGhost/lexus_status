"""Sensor platform for the Lexus Tibber integration."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfLength
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LexusTibberCoordinator

_LOGGER = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Entity descriptions
# ---------------------------------------------------------------------------


@dataclass(frozen=True, kw_only=True)
class LexusTibberSensorDescription(SensorEntityDescription):
    """Extended description that carries the coordinator data-key."""

    value_key: str = ""


SENSOR_DESCRIPTIONS: tuple[LexusTibberSensorDescription, ...] = (
    LexusTibberSensorDescription(
        key="battery_level",
        value_key="battery_level",
        name="Battery Level",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-electric-vehicle",
        suggested_display_precision=0,
    ),
    LexusTibberSensorDescription(
        key="range_km",
        value_key="range_km",
        name="Electric Range",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:map-marker-distance",
        suggested_display_precision=0,
    ),
    LexusTibberSensorDescription(
        key="charging_status",
        value_key="charging_status",
        name="Charging Status",
        icon="mdi:ev-station",
    ),
    LexusTibberSensorDescription(
        key="remaining_charge_time",
        value_key="remaining_charge_time",
        name="Remaining Charge Time",
        native_unit_of_measurement="min",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:timer-outline",
        suggested_display_precision=0,
    ),
    LexusTibberSensorDescription(
        key="last_lexus_update",
        value_key="last_lexus_update",
        name="Last Synced from Lexus",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock-check-outline",
    ),
)


# ---------------------------------------------------------------------------
# Platform setup
# ---------------------------------------------------------------------------


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up all Lexus Tibber sensors from the config entry."""
    coordinator: LexusTibberCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        LexusTibberSensorEntity(coordinator, description)
        for description in SENSOR_DESCRIPTIONS
    )


# ---------------------------------------------------------------------------
# Sensor entity
# ---------------------------------------------------------------------------


class LexusTibberSensorEntity(
    CoordinatorEntity[LexusTibberCoordinator], SensorEntity
):
    """Represents a single Lexus Tibber sensor."""

    entity_description: LexusTibberSensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: LexusTibberCoordinator,
        description: LexusTibberSensorDescription,
    ) -> None:
        """Initialise the sensor."""
        super().__init__(coordinator)
        self.entity_description = description

        vin: str = (
            (coordinator.data or {}).get("vin") or "unknown"
        )
        alias: str = (
            (coordinator.data or {}).get("alias") or "Lexus UX300e"
        )

        self._attr_unique_id = f"{DOMAIN}_{vin}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, vin)},
            name=alias,
            manufacturer="Lexus",
            model="UX300e",
        )

    @property
    def native_value(self) -> Any:
        """Return the sensor's current value."""
        if self.coordinator.data is None:
            return None

        raw = self.coordinator.data.get(self.entity_description.value_key)

        # charging_status is a plain string from pytoyoda (e.g. "charging", "connected", "disconnected")
        # Pass through directly; None is handled by the base class as unavailable.
        return raw

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional state attributes on the battery level sensor."""
        if (
            self.entity_description.key != "battery_level"
            or self.coordinator.data is None
        ):
            return None

        data = self.coordinator.data
        return {
            "vin": data.get("vin"),
            "last_lexus_update": data.get("last_lexus_update"),
        }
