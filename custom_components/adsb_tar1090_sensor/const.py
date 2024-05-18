"""Constants for the OpenAI Service integration."""
DOMAIN = "adsb_tar1090_sensor"

"""Custom config parameters for this service"""
CONF_URL = "url"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_DISTANCE_THRESHOLD = "distance_threshold"
CONF_EMERGENCY_SQUAWK = "emergency_squawk"
CONF_SPECIAL_SQUAWK = "special_squawk"
CONF_SENSORS = "sensors"

#"""Default Config values"""
#DEFAULT_URL = str("http://adsbexchange.local/tar1090/data/aircraft.json")

"""Default Option values"""
DEFAULT_UPDATE_INTERVAL_SECONDS = 60
DEFAULT_DISTANCE_THRESHOLD_KM = 10
DEFAULT_EMERGENCY_SQUAWK = [7500,7600,7700]
DEFAULT_SPECIAL_SQUAWK = [7100]
