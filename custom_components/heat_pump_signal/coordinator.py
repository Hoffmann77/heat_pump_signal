"""GatewayReader update coordinator."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.storage import Store
import homeassistant.util.dt as dt_util
from homeassistant.const import CONF_NAME
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.components.sensor import (
    SensorDeviceClass
)

# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
#     from homeassistant.core import State
from homeassistant.core import State

from homeassistant.const import (
    CONF_NAME,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)

from .const import (
    CONF_TRESHOLD, CONF_HYSTERESIS, CONF_BAT_MIN_POWER, CONF_BAT_MIN_SOC,
    CONF_BUFFER_POWER, CONF_GRID, CONF_PV_PRODUCTION, CONF_BATTERY,
    CONF_BATTERY_SOC, CONF_HEATPUMP, CONF_GRID_INVERTED, CONF_BATTERY_INVERTED,
    CONF_HEATPUMP_INVERTED,
)


UPDATE_INTERVAL = timedelta(seconds=60)

STORAGE_KEY = "heat_pump_signal"
STORAGE_VERSION = 1

_LOGGER = logging.getLogger(__name__)


class HepucoUpdateCoordinator(DataUpdateCoordinator):
    """DataUpdateCoordinator for gateway reader."""

    def __init__(
            self,
            hass: HomeAssistant,
            entry: ConfigEntry
    ) -> None:
        """Initialize DataUpdateCoordinator for the gateway."""
        super().__init__(
            hass,
            _LOGGER,
            name=entry.data[CONF_NAME],
            update_interval=UPDATE_INTERVAL,
        )
        self.config_entry = entry

        self.grid_entity_id = entry.data.get(CONF_GRID)
        self.prod_entity_id = entry.data.get(CONF_PV_PRODUCTION)
        # self.cons_entity_id = entry.data.get(CONF_CONSUMPTION)
        self.bat_entity_id = entry.data.get(CONF_BATTERY)
        self.bat_soc_entity_id = entry.data.get(CONF_BATTERY_SOC)
        self.heatpump_entity_id = entry.data.get(CONF_HEATPUMP)
        self.grid_inverted = entry.data.get(CONF_GRID_INVERTED)
        self.battery_inverted = entry.data.get(CONF_BATTERY_INVERTED)
        self.heatpump_inverted = entry.data.get(CONF_HEATPUMP_INVERTED)

        self._store = Store(
            hass,
            STORAGE_VERSION,
            f"{STORAGE_KEY}.{self.config_entry.entry_id}"
        )
        self._store_data = None
        self._store_update_pending = False

    async def _async_update_data(self) -> dict[str, Any]:
        """Pre-process data.

        Pre-process the data to lookup tables
        so entities can quickly look up their data.

        """
        now = datetime.now(timezone.utc)
        test_data = {
            "partial_excess": True,
            "full_excess": False,
            "combined_surplus": self.calc_excess_power(now),
            "battery_surplus": self.calc_battery_sacrifice(self.bat_entity_id, now),
        }
        return test_data
        
        await self.async_setup_store()

        if self.is_locked():
            return False

        now = datetime.now(timezone.utc)
        treshold = self.config_entry.options.get(CONF_TRESHOLD)
        hysteresis = self.config_entry.options.get(CONF_HYSTERESIS)
        
        
        for key in ("custom_excess", "full_excess"):
            data = self._store_data["binary_sensors"][key]
            curr_state = bool(data["curr_state"])
            if not self.is_locked(key, now):
                if curr_state:
                    treshold = treshold - hysteresis
                
                excess_power = self.calc_excess_power(now)
                state = excess_power >= treshold
                
        
        
        
        
        # calculate state of the custom binary sensor
        is_locked = self.is_locked("custom")
        #curr_state = 
        
        
      

    async def async_setup_store_data(self):
        """Load the data from the store."""
        await self._async_sync_store(load=True)
        if not self._store_data:
            data = {
                "binary_sensors": {
                    "custom_excess": {
                        "last_change": None,
                        "curr_state": False,
                    },
                    "full_excess": {
                        "last_change": None,
                        "curr_state": False,
                    },
                },
            }
            self._store_data = data
            self._store_update_pending = True

    def calc_excess_power(self, now=None) -> float | None:
        """Calculate the excess power that is available.

        Calculates the excess power based on the entities
        configured in the config_entry.

        Notes
        -----
        - grid_power: Negative values mean that power is exported to the grid.

        """
        now = now or datetime.now(timezone.utc)
        buffer = self.config_entry.options.get(CONF_BUFFER_POWER, 0)
        
        # Grid export is negative
        
        if self.prod_entity_id and not self.grid_entity_id:
            prod = self._get_state(self.prod_entity_id, now=now)
            if prod is not None:
                prod = self._state_to_float(prod) - buffer

            return prod

        elif self.grid_entity_id:
            power = self._get_state(self.grid_entity_id, now=now)
            if power is None:
                return power

            power = self._state_to_float(power)
            if self.config_entry.options.get(CONF_GRID_INVERTED):
                power = power * -1

            if self.bat_entity_id:
                power += self.calc_battery_sacrifice(self.bat_entity_id, now)

            hp_power = self._get_state(self.heatpump_entity_id, now=now)
            if hp_power is not None:
                hp_power = self._state_to_float(hp_power)
                if self.config_entry.options.get(CONF_HEATPUMP_INVERTED):
                    hp_power = hp_power * -1
                power -= hp_power

            return power * -1
            #excess = power - buffer + battery_excess + hp_power
            #return excess if excess >= 0 else 0

    def calc_battery_sacrifice(
            self,
            battery_power_entity,
            now: datetime,
    ) -> float | None:
        """Return the amount of power the battery can sacrifice.

        Calculates how much power the battery can sacrifice of
        it's charging power while staying within the limits
        specified in the config_entry.

        Parameters
        ----------
        now : datetime
            Current UTC date and time.

        Returns
        -------
        float
            Power available.

        """
        state = self._get_state(battery_power_entity, now=now)
        if state is None:
            return 0

        power = self._state_to_float(state)
        if self.config_entry.options.get(CONF_BATTERY_INVERTED):
            power = power * -1
        
        if power < 0:
            bat_soc = self._get_state(self.bat_soc_entity_id, now=now)
            min_power = self.config_entry.options.get(CONF_BAT_MIN_POWER, 0)
            if bat_soc is None:
                if (power - min_power) <= 0:
                    # Dont return negative power if the power is positive.
                    power = power * 0.95 + min_power
                else:
                    power = 0
            else:
                bat_soc = self._state_to_float(bat_soc)
                min_soc = self.config_entry.options.get(CONF_BAT_MIN_SOC, 0)
                if bat_soc > min_soc:
                    # If the SOC is available and larger than the minimum SOC,
                    # the excess power is 95% of the battery charging power
                    # minus the minimum charging power.
                    if (power - min_power) <= 0:
                        # Dont return negative power if the power is positive.
                        power = power * 0.95 + min_power
                    else:
                        power = 0
                else:
                    # Return 0 if the SOC is lower than the minimum SOC.
                    power = 0
        else:
            return power
        
        
        
        # if (power := self._get_state(self.bat_entity_id, now=now)) is None:
        #     # Return 0 if the battery power entity is not available
        #     return 0

        # # Convert bat_power into a float and invert the value if required.
        # power = self._state_to_float(power)
        # if self.config_entry.options.get(CONF_BATTERY_INVERTED):
        #     power = power * -1

        # # Return power if the battery is charging.
        # if power <= 0:
        #     return power
        # else:
        #     bat_soc = self._get_state(self.bat_soc_entity_id, now=now)
        #     min_power = self.config_entry.options.get(CONF_BAT_MIN_POWER, 0)

        #     if bat_soc is None:
        #         # If the SOC is not available, the excess power is 95% of
        #         # the battery charging power minus the minimum charging power.
        #         excess = power * 0.95 - min_power
        #     else:
        #         bat_soc = self._state_to_float(bat_soc)
        #         min_soc = self.config_entry.options.get(CONF_BAT_MIN_SOC, 0)
        #         if bat_soc > min_soc:
        #             # If the SOC is available and larger than the minimum SOC,
        #             # the excess power is 95% of the battery charging power
        #             # minus the minimum charging power.
        #             excess = power * 0.95 - min_power
        #         else:
        #             # Return 0 if the SOC is lower than the minimum SOC.
        #             excess = 0

        #     return excess




        
        
        
        
        
        
    
    # def calculate_state(self, treshold, now=None):
        
    #     now = datetime.now(timezone.utc) if now is None else now
        
    #     grid_export = 1200
        
    #     curr_state = False  # used
        
    #     excess_power = 1200  # used. calculated 
        
    #     if not self.has_battery:
    #         excess_power = grid_export
        
    #     else:
            
    #         excess = export + charging_power
            
            
            
    #         cons = prod - export
        
        

        
    #     if curr_state:
    #         treshold = treshold - hysteresis
        
    #     return excess_power >= treshold
        
    
    
    
    
    #     if curr_state:
    #         # binary_sensor's state is True.
    #         # Keep state if the rebound interval has elapsed and the 
    #         # excess_power is larger than excess_power - hysteresis.
    #         if excess_power >= treshold - hysteresis:
    #             return True
            
    #     else:
    #         # binary_sensor's state is True.
    #         if excess_power >= treshold:
    #             pass
            
        
        
    #     if not self.has_battery:
    #         pass
        
    #     return False
        
        
    #     production = 1400
    


    def _get_state(
            self,
            entity_id: str,
            default: Any = None,
            now: datetime = None,
            max_age: timedelta = timedelta(minutes=10)
    ) -> State:
        """Return the State of a entity.

        Parameters
        ----------
        entity_id : str
            Unique id of the enity.
        default : Any, optional
            Default value. The default is None.
        now : datetime, optional
            Current UTC date and time. The default is None.
        max_age : timedelta, optional
            The maximum age of the state. The default is timedelta(minutes=10).

        Returns
        -------
        State or default.

        """
        now = datetime.now(timezone.utc) if now is None else now
        if entity_id is None:
            return default

        state_obj = self.hass.states.get(entity_id)
        if state_obj is None:
            _LOGGER.debug(f"Could not access the state of {entity_id}.")
            return default

        if now > (state_obj.last_changed + max_age):
            _LOGGER.debug(f"State '{entity_id}' is too old.")
            return default
        elif state_obj.state in (STATE_UNAVAILABLE, STATE_UNKNOWN, None):
            return default
        else:
            _LOGGER.debug(f"State of {entity_id}: {state_obj.state}")
            return state_obj

    def _state_to_float(self, state_obj: State) -> float:
        """Convert the given State into a float."""
        unit = state_obj.attributes.get("unit_of_measurement")
        if unit == "kw":
            return float(state_obj.state) * 10**3

        return float(state_obj.state)

    def is_locked(self, key, now):
        """Return weather the sensor is locked."""
        last_change = self._store_data["binary_sensors"][key]["last_change"]
        if last_change is None:
            return False
        elif last_change:
            timestamp = datetime.fromisoformat(last_change)
            release = timestamp + timedelta(minutes=10)
            if now >= release:
                return True

    async def _async_load_cached_token(self) -> str:
        await self._async_sync_store(load=True)
        return self._store_data.get("token")

    async def _async_update_cached_token(self) -> None:
        """Update saved token in config entry."""
        _LOGGER.debug(f"{self.name}: Updating token in config entry from auth")
        if token := self.gateway_reader.auth.token:
            self._store_data["token"] = token
            self._store_update_pending = True
            await self._async_sync_store()

    async def _async_sync_store(self, load: bool = False) -> None:
        """Sync the hass store."""
        if (self._store and not self._store_data) or load:
            self._store_data = await self._store.async_load() or {}

        if self._store and self._store_update_pending:
            await self._store.async_save(self._store_data)
            self._store_update_pending = False
