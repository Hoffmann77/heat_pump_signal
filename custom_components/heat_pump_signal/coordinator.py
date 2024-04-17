"""Data update coordinator for the Heat pump signal integration."""

import logging
from datetime import datetime, timedelta, timezone

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
# from homeassistant.helpers.storage import Store
from homeassistant.const import CONF_NAME
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    # UpdateFailed,
)

from .signals import SIGNALS
from .const import CONF_LOCK_INTERVAL

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(seconds=60)
# STORAGE_VERSION = 1
# STORAGE_KEY = "heat_pump_signal"


# class HeatPumpSignal:
#     """Class representing a Heat pump signal."""

#     def __init__(self, lock_interval) -> None:
#         """Initialize the instance."""
#         self.state = False
#         self.lock_interval = lock_interval
#         self.last_change = datetime.now(timezone.utc)

#     @property
#     def is_locked(self):
#         """Return whether the signal is locked."""
#         now = datetime.now(timezone.utc)
#         if now >= self.last_change + self.lock_interval:
#             return False

#         return True

#     def get_state(self, new_state):
#         """Return the state of the signal."""
#         if self.state != new_state and not self.is_locked:
#             self.state = new_state
#             self.last_change = datetime.now(timezone.utc)

#         return self.state


class SignalUpdateCoordinator(DataUpdateCoordinator):
    """Data update coordinator."""

    key = "heat_pump_signal"

    def __init__(
            self,
            hass: HomeAssistant,
            entry: ConfigEntry
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=entry.data[CONF_NAME],
            update_interval=UPDATE_INTERVAL,
        )
        self.config_entry = entry
        self.sub_signals = self._get_sub_signals()
        self.signal_curr_state = False
        self.signal_last_change = datetime.now(timezone.utc)
        self.signal_lock_interval = timedelta(**entry.data[CONF_LOCK_INTERVAL])

        # self._store = Store(
        #     hass,
        #     STORAGE_VERSION,
        #     f"{STORAGE_KEY}.{self.config_entry.entry_id}"
        # )
        # self._store_data = None
        # self._store_update_pending = False

    @property
    def signal_locked(self) -> bool:
        """Return whether the signal is locked."""
        now = datetime.now(timezone.utc)
        if now >= self.last_change + self.lock_interval:
            return False

        return True

    async def _async_update_data(self) -> dict:
        """Update the data and the signal."""
        data = await self._update_sub_signals()
        signal = await self._update_signal(data)

        # Return the current signal if the signal is locked
        if self.signal_locked:
            data[self.key] = self.signal_curr_state
            return data

        # Change the signal to the new signal
        if signal != self.signal_curr_state:
            self.signal_curr_state = signal
            self.signal_last_change = datetime.now(timezone.utc)

        data[self.key] = self.signal_curr_state
        return data

        # await self._async_sync_store(load=True)
        # signals_data = self._store_data.get("signals") or {}

        # for key, state in signal_states:
        #     if key in signals_data:
        #         curr_state = signals_data[key]["curr_state"]
        #         is_locked = await self._async_is_locked(
        #             signals_data[key]["last_change"], now
        #         )
        #         if (state != curr_state) and not is_locked:
        #             signals_data[key]["curr_state"] = state
        #             signals_data[key]["last_change"] = now
        #             self._store_update_pending = True

        #     else:
        #         signals_data[key] = {
        #             "curr_state": state,
        #             "last_change": now,
        #         }
        #         self._store_update_pending = True

        #     signal_results[key] = signals_data[key]["curr_state"]

        # self._store_data["signals"] = signals_data
        # await self._async_sync_store()

        # return {**signal_results, **extra_attributes}

    async def _update_sub_signals(self) -> dict:
        """Update the sub-signals and return the data."""
        data = {}
        for signal in self.sub_signals:
            response = signal.update()
            data.update(**response.to_dict())

        return data

    async def _update_signal(self, data) -> bool:
        """Update the signal."""
        keys = [signal.key for signal in self.sub_signals]
        signal = False
        for key in keys:
            state = data.get(key)
            if state:
                signal = True

        return signal

    def _get_sub_signals(self) -> list:
        """Return the enabled sub-signals."""
        sub_signals = []
        for signal in SIGNALS:
            if self.config_entry.data.get(signal.key):
                config = self.config_entry.options.get(signal.key)
                sub_signals.append(signal(self.hass, config))

        return sub_signals

    # async def _async_sync_store(self, load: bool = False) -> None:
    #     """Sync the hass store."""
    #     if (self._store and not self._store_data) or load:
    #         self._store_data = await self._store.async_load() or {}

    #     if self._store and self._store_update_pending:
    #         await self._store.async_save(self._store_data)
    #         self._store_update_pending = False
