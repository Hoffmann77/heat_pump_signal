"""The enphase_envoy component."""

from homeassistant.const import Platform


DOMAIN = "heat_pump_signal"

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]

# user step new

CONF_LOCK_INTERVAL = "lock_interval"

CONF_PV_SIGNAL = "pv_signal"
CONF_PRICE_SIGNAL = "electicity_price_signal"
CONF_CO2_SIGNAL = "co2_signal"


# general

CONF_STATIC_THRESHOLD = "static_threshold"
CONF_DYNAMIC_THRESHOLD = "dynamic_threshold"

# pv_signal step new

CONF_OPTIONAL_THRESHOLDS = "thresholds_optional"



# user step old

CONF_GRID = "grid_power_sensor"
CONF_GRID_INVERTED = "grid_power_sensor_inverted"
CONF_PV_PRODUCTION = "pv_production_sensor"
CONF_CONSUMPTION = "consumption_sensor"
CONF_CONSUMPTION_INVERTED = "consumption_sensor_inverted"
CONF_BATTERY = "battery_power_sensor"
CONF_BATTERY_INVERTED = "battery_power_sensor_inverted"
CONF_BATTERY_SOC = "battery_soc_sensor"
CONF_HEATPUMP = "heat_pump_power_sensor"
CONF_HEATPUMP_INVERTED = "heat_pump_power_sensor_inverted"

# config step

CONF_THRESHOLD = "threshold"
CONF_THRESHOLD_OPTIONAL = "threshold_optional"
CONF_BUFFER_POWER = "buffer_power"
CONF_BAT_MIN_SOC = "battery_min_soc"
CONF_BAT_MIN_POWER = "battery_min_power"
CONF_HYSTERESIS = "hysteresis"
CONF_LOCK_INTERVAL = "lock_interval"
CONF_REBOUND_INTERVAL = "rebound_interval"
