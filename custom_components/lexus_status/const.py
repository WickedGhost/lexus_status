"""Constants for the Lexus UX300e integration."""

DOMAIN = "lexus_status"

# Lexus Connected Services credentials
# pytoyoda only supports the Toyota Connected Europe platform (EU accounts only)
CONF_LEXUS_USERNAME = "lexus_username"
CONF_LEXUS_PASSWORD = "lexus_password"
CONF_LEXUS_VIN = "lexus_vin"

# Lexus brand code used by pytoyoda ("L" = Lexus, "T" = Toyota)
LEXUS_BRAND = "L"

# Polling
CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_SCAN_INTERVAL = 30  # minutes

# Update mode
CONF_UPDATE_MODE = "update_mode"
UPDATE_MODE_PERIODIC = "periodic"
UPDATE_MODE_MANUAL = "manual"
DEFAULT_UPDATE_MODE = UPDATE_MODE_PERIODIC
