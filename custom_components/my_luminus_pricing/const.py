"""Constants for our integration."""

DOMAIN = "my_luminus_pricing"

# Scan interval in seconds (DEFAULT ~22h, MIN 12h)
DEFAULT_SCAN_INTERVAL = 80000
MIN_SCAN_INTERVAL = 43200

HTTP_TIMEOUT = 60
LOGIN_TIMEOUT = 30
USE_MOCK_DATA = False

# Device dict keys that are meta, not price sensors
DEVICE_META_KEYS = ("device_id", "device_name", "device_type", "product_name")