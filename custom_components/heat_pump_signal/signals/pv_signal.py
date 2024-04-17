"""Pv Signal module."""

import logging
from dataclasses import dataclass

from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN

from .common import SignalResponse
from ..utils import StateDescriptor, ERROR_STATES, get_state_as_float
from ..const import (
    CONF_THRESHOLD_ENTITY, CONF_OPTIONAL_THRESHOLDS, 
    CONF_STATIC_THRESHOLD, CONF_DYNAMIC_THRESHOLD,
    
    CONF_GRID, CONF_BATTERY, CONF_BATTERY_SOC, CONF_HEATPUMP, CONF_THRESHOLD,
    CONF_GRID_INVERTED, CONF_BATTERY_INVERTED, CONF_HEATPUMP_INVERTED,
    CONF_BAT_MIN_POWER, CONF_BAT_MIN_SOC, CONF_BUFFER_POWER,
    CONF_HYSTERESIS
)

_LOGGER = logging.getLogger(__name__)


class PvSignal:
    """Signal class representing a Pv Signal."""

    key = "pv_signal"

    #grid_power = StateDescriptor(default=0, convert_to=float)
    #battery_power = StateDescriptor(default=0, convert_to=float)
    #battery_soc = StateDescriptor(default=0, convert_to=float)
    #heatpump_power = StateDescriptor(default=0, convert_to=float)

    def __init__(self, hass, config):
        """Initialize instance."""
        self.hass = hass
        self.config = config
        # self.curr_state = self.signal_key
        #self.grid_power_entity = config.get(CONF_GRID)
        #self.battery_power_entity = config.get(CONF_BATTERY)
        #self.battery_soc_entity = config.get(CONF_BATTERY_SOC)
        #self.heatpump_power = config.get(CONF_HEATPUMP)
        
        self.static_threshold = config.get(CONF_STATIC_THRESHOLD)
        self.grid_entity = config.get(CONF_GRID)
        self.battery_entity = config.get(CONF_BATTERY)
        self.battery_soc_entity = config.get(CONF_BATTERY_SOC)
        self.heat_pump_entity = config.get(CONF_HEATPUMP)
        
        # self._thresholds = None
        self._curr_states = {}
        
    
    
    def update(self) -> SignalResponse:
        """Update the signal and return the SignalResponse obj.

        Returns
        -------
        SignalResponse
            Signal response.

        """
        states = {}
        grid_power = self.get_grid_power()
        battery_power = self.get_battery_power()
        heat_pump_power = self.get_heat_pump_power()
        total_power = self.calc_total_power(
            grid_power, battery_power, heat_pump_power
        )
        for name, threshold in self.get_thresholds().items():
            curr_state = self._curr_states.get(name, False)
            state = self.calc_state(total_power, threshold, curr_state)
            states[name] = state

        self._curr_states = states

        return SignalResponse(
            primary_state=states.pop(self.key),
            optional_states=states,
            metadata={
                f"{self.key}_threshold": grid_power,
                f"{self.key}_battery_power": battery_power,
                f"{self.key}_heat_pump_power": heat_pump_power,
            },
        )

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

    def calc_total_power(
            self, grid_power, battery_power, heat_pump_power
    ) -> float | None:
        """Return the total power."""
        try:
            total_power = grid_power
            total_power += battery_power
            total_power -= heat_pump_power
        except TypeError:
            return None
        else:
            return total_power

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
            if (_power := power + min_power) < 0:
                # Dont return negative power if the power is positive.
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

    def get_thresholds(self) -> list[tuple[str, int | float]]:
        """Return the thresholds from the config entry.

        The dynamic threshold is preferred over the static threshold.
        Uses the static threshold if the dynamic threshold is not usable.

        """
        threshold = self.config.get(CONF_DYNAMIC_THRESHOLD)
        if threshold is None:
            threshold = self.static_threshold

        thresholds = {self.key: threshold}

        # can be used for optional thresholds
        # for threshold in self.config.get(CONF_OPTIONAL_THRESHOLDS):
        #     try:
        #         value = float(threshold)
        #         name = threshold
        #     except ValueError:
        #         # threshold seems to be an entity.
        #         value = self._get_state(threshold)
        #         name = threshold.split(".")[-1]

        #     thresholds[f"{self.key}_{name}"] = value
        #     return value

        return thresholds

    def _get_state_as_float(self, entity_id: str, default=None):
        """Return the state of the given entity.

        If the state obj does exists and the state is not `unknow` or
        `unavailable`, the state is converted into a float.
        Otherwise the default is returned.
        """
        return get_state_as_float(self.hass.states, entity_id, default)
