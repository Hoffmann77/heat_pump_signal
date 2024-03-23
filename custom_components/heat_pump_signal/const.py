"""The enphase_envoy component."""

from homeassistant.const import Platform


DOMAIN = "heat_pump_signal"

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]

ICON = "mdi:flash"

COORDINATOR = "coordinator"

NAME = "name"


# user step

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

CONF_HEATPUMP_TYP_CONS = "heat_pump_power"
CONF_TRESHOLD = "treshold_power"
CONF_BUFFER_POWER = "buffer_power"
CONF_BAT_MIN_SOC = "battery_min_soc"
CONF_BAT_MIN_POWER = "battery_min_power"
CONF_HYSTERESIS = "hysteresis"
CONF_LOCK_INTERVAL = "lock_interval"
CONF_REBOUND_INTERVAL = "rebound_interval"
