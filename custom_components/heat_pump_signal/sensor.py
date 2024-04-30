"""Sensor entities for the Heat pump Signal integration."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfPower
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)

from .const import DOMAIN, CONF_PV_SIGNAL
from .coordinator import SignalUpdateCoordinator
from .entity import SignalCoordinatorEntity


_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class SignalSensorEntityDescription(SensorEntityDescription):
    """Provide a description of a Heat pump Signal sensor."""

    value_fn: Callable[[dict], float | None]
    exists_fn: Callable[[dict], bool] = lambda _: True


PV_SIGNAL_SENSORS = (
    SignalSensorEntityDescription(
        key=f"{CONF_PV_SIGNAL}_threshold",
        name="Excess power threshold",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get(f"{CONF_PV_SIGNAL}_threshold"),
        exists_fn=lambda entry: bool(entry.options.get("pv_signal")),
    ),
    SignalSensorEntityDescription(
        key=f"{CONF_PV_SIGNAL}_total_power",
        name="Total power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get(f"{CONF_PV_SIGNAL}_total_power"),
        exists_fn=lambda entry: bool(entry.options.get("pv_signal")),
    ),
    SignalSensorEntityDescription(
        key=f"{CONF_PV_SIGNAL}_grid_power",
        name="Grid power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get(f"{CONF_PV_SIGNAL}l_grid_power"),
        exists_fn=lambda entry: bool(entry.options.get("pv_signal")),
    ),
    SignalSensorEntityDescription(
        key=f"{CONF_PV_SIGNAL}_battery_power",
        name="Battery power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get(f"{CONF_PV_SIGNAL}_battery_power"),
        exists_fn=lambda entry: bool(entry.options.get("pv_signal")),
    ),
    SignalSensorEntityDescription(
        key=f"{CONF_PV_SIGNAL}_heat_pump_power",
        name="Heat pump power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get(f"{CONF_PV_SIGNAL}_heat_pump_power"),
        exists_fn=lambda entry: bool(entry.options.get("pv_signal")),
    ),
)

# PRICE_SIGNAL_SENSORS = (
# )

# RENEWABLE_SIGNAL_SENSORS = (
# )

SENSORS = PV_SIGNAL_SENSORS


async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        SignalSensorEntity(coordinator, description)
        for description in SENSORS
        if description.exists_fn(entry)
    )


class SignalSensorEntity(SignalCoordinatorEntity, SensorEntity):
    """Implementation of a Heat pump signal sensor."""

    def __init__(
            self,
            coordinator: SignalUpdateCoordinator,
            description: SignalSensorEntityDescription,
    ) -> None:
        """Initialize the sensor entity."""
        super().__init__(coordinator, description)

        self._attr_unique_id = self.entity_description.key

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data)
    






