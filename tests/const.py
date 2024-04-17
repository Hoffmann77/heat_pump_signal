"""Constants for Heat pump signal tests."""


# TODO: use const names

MOCK_CONFIG = {
    "name": "My test signal",
    "lock_interval": {
        "hours": 0,
        "minutes": 15,
        "seconds": 0,
    },
    "pv_signal": True,
    "electicity_price_signal": False,
    "co2_signal": False,
}


MOCK_CONFIG_PV_SIGNAL = {
    "grid_power_sensor": "sensor.gateway_grid_power",
    "static_threshold": 2000.0,
    "dynamic_threshold": False,
    "buffer_power": 200.0,
    "battery_min_soc": 25.0,
    "battery_min_power": 400.0,
    "hysteresis": 200.0,
    "heat_pump_power_sensor": "sensor.heat_pump_power",
    "battery_power_sensor": "sensor.gateway_battery_power",
    "battery_soc_sensor": "sensor.gateway_battery_soc"
}
