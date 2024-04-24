"""Pv signal."""

import logging

from ..utils import get_state_as_float
from ..const import (
    CONF_OPTIONAL_THRESHOLDS, 
    CONF_STATIC_THRESHOLD, CONF_DYNAMIC_THRESHOLD,
    
    CONF_PV_SIGNAL,
    
    
    CONF_GRID, CONF_BATTERY, CONF_BATTERY_SOC, CONF_HEATPUMP, CONF_THRESHOLD,
    CONF_GRID_INVERTED, CONF_BATTERY_INVERTED, CONF_HEATPUMP_INVERTED,
    CONF_BAT_MIN_POWER, CONF_BAT_MIN_SOC, CONF_BUFFER_POWER,
    CONF_HYSTERESIS
)

_LOGGER = logging.getLogger(__name__)


class PvSignal:
    """Signal class representing a Pv Signal."""

    key = CONF_PV_SIGNAL

    def __init__(self, hass, config):
        """Initialize instance."""
        self.hass = hass
        self.config = config
        self.grid_entity = config.get(CONF_GRID)
        self.battery_entity = config.get(CONF_BATTERY)
        self.battery_soc_entity = config.get(CONF_BATTERY_SOC)
        self.heat_pump_entity = config.get(CONF_HEATPUMP)
        self.static_threshold = config.get(CONF_STATIC_THRESHOLD)
        self.curr_state = False

    def update(self) -> dict:
        """Update the signal and return the SignalResponse obj.

        Returns
        -------
        SignalResponse
            Signal response.

        """
        power_dict = self.get_power_dict()
        threshold = self.get_threshold()
        self.curr_state = self.calc_state(
            power_dict["total_power"], threshold, self.curr_state
        )
        return {
            self.key: self.curr_state,
            f"{self.key}_threshold": threshold,
            f"{self.key}_total_power": power_dict["total_power"],
            f"{self.key}_grid_power": power_dict["grid_power"] * -1,
            f"{self.key}_battery_power": power_dict["battery_power"] * -1,
            f"{self.key}_heat_pump_power": power_dict["heat_pump_power"] * -1,
        }

    def get_power_dict(self) -> dict:
        """Return the power dict."""
        power_dict = {
            "grid_power": self.get_grid_power(),
            "battery_power": self.get_battery_power(),
            "heat_pump_power": self.get_heat_pump_power(),
        }
        try:
            total_power = power_dict["grid_power"]
            total_power += power_dict["battery_power"]
            total_power -= power_dict["heat_pump_power"]
        except TypeError:
            total_power = None

        return power_dict["total_power": total_power]

    def calc_state(self, total_power, threshold, curr_state):
        """Calculate the state with the given arguments."""
        if total_power is None:
            return None

        if curr_state:
            hysteresis = self.config.get(CONF_HYSTERESIS)
        else:
            hysteresis = 0

        buffer_power = self.config.get(CONF_BUFFER_POWER)
        surplus = (threshold + buffer_power - hysteresis) - total_power
        if surplus >= 0:
            return True
        else:
            return False

    def get_grid_power(self):
        """Return the grid power.

        Negative values indicate that power is exported to the grid.

        Returns
        -------
        power : float, str or None
            State of the grid power entity or None if the state does not exist.

        """
        # power = self.grid_power
        power = self._get_state_as_float(self.grid_entity)
        if power is None or isinstance(power, str):
            return power

        if self.config.get(CONF_GRID_INVERTED, False):
            power = power * -1

        return power

    def get_battery_power(self):
        """Return the power the battery can relinquish from charging.

        Negative values indicate that the battery is charging.
        If the battery is discharging the value 0 is returned.

        Returns
        -------
        int, str or None
            Charging power the battery can relinquish or the state of the
            battery power entity if the state is `unknown` or `unavailable`.

        """
        power = self._get_state_as_float(self.battery_entity, default=0)
        if power is None or isinstance(power, str):
            return power

        if self.config.get(CONF_BATTERY_INVERTED, False):
            power = power * -1

        if power >= 0:
            return power

        min_power = self.config.get(CONF_BAT_MIN_POWER, 0)
        min_soc = self.config.get(CONF_BAT_MIN_SOC, 0)
        bat_soc = self._get_state_as_float(self.battery_soc_entity, default=0)
        if bat_soc > min_soc:
            # Dont return negative power if the power is positive.
            if (_power := power + min_power) < 0:
                return _power

        return power

    def get_heat_pump_power(self):
        """Return the current power consumption of the heat pump."""
        entity = self.config.get(CONF_GRID)
        if entity is None:
            return

        power = self._get_state_as_float(self.heat_pump_entity, default=0)
        if power is None or isinstance(power, str):
            return power

        if self.config.get(CONF_HEATPUMP_INVERTED, False):
            power = power * -1

        return power

    def get_threshold(self) -> dict:
        """Return the thresholds from the config entry.

        The dynamic threshold is preferred over the static threshold.
        Uses the static threshold if the dynamic threshold is not usable.

        """
        entity = self.config.get(CONF_DYNAMIC_THRESHOLD)
        if entity is not None:
            threshold = self._get_state_as_float(entity)
            if threshold is None:
                threshold = self.static_threshold
        else:
            threshold = self.static_threshold

        return {self.key: threshold}

    def _get_state_as_float(self, entity_id: str, default=None):
        """Return the state of the given entity.

        If the state obj does exists and the state is not `unknow` or
        `unavailable`, the state is converted into a float.
        Otherwise the default is returned.
        """
        return get_state_as_float(self.hass.states, entity_id, default)
