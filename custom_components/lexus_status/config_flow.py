"""Config flow for the Lexus UX300e integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

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
    UPDATE_MODE_PERIODIC,
)

_LOGGER = logging.getLogger(__name__)


async def _lexus_login_and_list(
    username: str, password: str
) -> list[dict[str, str]]:
    """Authenticate against Lexus Connected Services (EU) and list vehicles."""
    from pytoyoda.client import MyT  # noqa: PLC0415

    client = MyT(
        username=username,
        password=password,
        use_metric=True,
        brand=LEXUS_BRAND,
    )
    await client.login()
    vehicles = await client.get_vehicles()
    return [
        {"vin": v.vin, "alias": v.alias or v.vin}
        for v in vehicles
    ]


# ---------------------------------------------------------------------------
# Config flow
# ---------------------------------------------------------------------------


class LexusTibberConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Multi-step config flow: Lexus credentials → vehicle → options."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialise flow state."""
        self._lexus_data: dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Step 1 – Lexus credentials
    # ------------------------------------------------------------------

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Enter Lexus Connected Services credentials."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                vehicles = await _lexus_login_and_list(
                    user_input[CONF_LEXUS_USERNAME],
                    user_input[CONF_LEXUS_PASSWORD],
                )
            except ImportError:
                errors["base"] = "missing_library"
            except Exception as err:  # noqa: BLE001
                err_msg = str(err).lower()
                if "login" in err_msg or "auth" in err_msg or "password" in err_msg:
                    errors["base"] = "invalid_auth"
                else:
                    _LOGGER.exception("Unexpected Lexus auth error")
                    errors["base"] = "cannot_connect"
            else:
                self._lexus_data = dict(user_input)
                self._lexus_data["_vehicles"] = vehicles

                if len(vehicles) == 1:
                    self._lexus_data[CONF_LEXUS_VIN] = vehicles[0]["vin"]
                    return await self.async_step_options()

                return await self.async_step_lexus_vehicle()

        schema = vol.Schema(
            {
                vol.Required(CONF_LEXUS_USERNAME): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.EMAIL, autocomplete="username")
                ),
                vol.Required(CONF_LEXUS_PASSWORD): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.PASSWORD, autocomplete="current-password")
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    # ------------------------------------------------------------------
    # Step 2 – Pick the Lexus vehicle (only shown if >1 vehicle)
    # ------------------------------------------------------------------

    async def async_step_lexus_vehicle(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Select which vehicle to track."""
        vehicles: list[dict[str, str]] = self._lexus_data.pop("_vehicles", [])

        if user_input is not None:
            self._lexus_data[CONF_LEXUS_VIN] = user_input[CONF_LEXUS_VIN]
            return await self.async_step_options()

        options = {v["vin"]: f"{v['alias']}  ({v['vin']})" for v in vehicles}

        schema = vol.Schema(
            {vol.Required(CONF_LEXUS_VIN): vol.In(options)}
        )

        return self.async_show_form(
            step_id="lexus_vehicle",
            data_schema=schema,
        )

    # ------------------------------------------------------------------
    # Step 3 – Choose update mode
    # ------------------------------------------------------------------

    async def async_step_options(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Choose periodic or manual update mode."""
        if user_input is not None:
            self._lexus_data[CONF_UPDATE_MODE] = user_input[CONF_UPDATE_MODE]
            if user_input[CONF_UPDATE_MODE] == UPDATE_MODE_PERIODIC:
                return await self.async_step_scan_interval()
            return self._finalize_entry(
                update_mode=UPDATE_MODE_MANUAL,
                scan_interval=DEFAULT_SCAN_INTERVAL,
            )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_UPDATE_MODE, default=DEFAULT_UPDATE_MODE
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            {"value": UPDATE_MODE_PERIODIC, "label": "Periodic (automatic polling)"},
                            {"value": UPDATE_MODE_MANUAL, "label": "Manual (triggered by automation)"},
                        ]
                    )
                ),
            }
        )

        return self.async_show_form(step_id="options", data_schema=schema)

    # ------------------------------------------------------------------
    # Step 4 – Scan interval (only when periodic mode chosen)
    # ------------------------------------------------------------------

    async def async_step_scan_interval(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure the polling interval (periodic mode only)."""
        if user_input is not None:
            return self._finalize_entry(
                update_mode=self._lexus_data[CONF_UPDATE_MODE],
                scan_interval=user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): vol.All(int, vol.Range(min=5, max=240)),
            }
        )

        return self.async_show_form(step_id="scan_interval", data_schema=schema)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _finalize_entry(self, scan_interval: int, update_mode: str = DEFAULT_UPDATE_MODE) -> FlowResult:
        """Write the config entry."""
        data = {
            CONF_LEXUS_USERNAME: self._lexus_data[CONF_LEXUS_USERNAME],
            CONF_LEXUS_PASSWORD: self._lexus_data[CONF_LEXUS_PASSWORD],
            CONF_LEXUS_VIN: self._lexus_data[CONF_LEXUS_VIN],
            CONF_SCAN_INTERVAL: scan_interval,
            CONF_UPDATE_MODE: update_mode,
        }

        return self.async_create_entry(
            title=f"Lexus UX300e ({self._lexus_data[CONF_LEXUS_VIN]})",
            data=data,
        )

    # ------------------------------------------------------------------
    # Options flow (edit an existing entry)
    # ------------------------------------------------------------------

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Return the options flow handler."""
        return LexusTibberOptionsFlow(config_entry)


# ---------------------------------------------------------------------------
# Options flow – lets the user change the polling interval after setup
# ---------------------------------------------------------------------------


class LexusTibberOptionsFlow(config_entries.OptionsFlow):
    """Options flow: change update mode and polling interval."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialise."""
        self.config_entry = config_entry
        self._update_mode: str = DEFAULT_UPDATE_MODE

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Choose periodic or manual update mode."""
        if user_input is not None:
            self._update_mode = user_input[CONF_UPDATE_MODE]
            if self._update_mode == UPDATE_MODE_PERIODIC:
                return await self.async_step_scan_interval()
            # Manual: keep existing interval value so data stays consistent
            existing_interval: int = self.config_entry.options.get(
                CONF_SCAN_INTERVAL,
                self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            )
            return self.async_create_entry(
                title="",
                data={CONF_UPDATE_MODE: UPDATE_MODE_MANUAL, CONF_SCAN_INTERVAL: existing_interval},
            )

        current_mode: str = self.config_entry.options.get(
            CONF_UPDATE_MODE,
            self.config_entry.data.get(CONF_UPDATE_MODE, DEFAULT_UPDATE_MODE),
        )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_UPDATE_MODE, default=current_mode
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            {"value": UPDATE_MODE_PERIODIC, "label": "Periodic (automatic polling)"},
                            {"value": UPDATE_MODE_MANUAL, "label": "Manual (triggered by automation)"},
                        ]
                    )
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)

    async def async_step_scan_interval(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure the polling interval (periodic mode only)."""
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data={
                    CONF_UPDATE_MODE: self._update_mode,
                    CONF_SCAN_INTERVAL: user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                },
            )

        current_interval: int = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_SCAN_INTERVAL, default=current_interval
                ): vol.All(int, vol.Range(min=5, max=240)),
            }
        )

        return self.async_show_form(step_id="scan_interval", data_schema=schema)
