"""Home assistant sensors for the Heat pump Signal integration."""

from __future__ import annotations

import logging
from typing import Any
from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
# from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfPower
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)

from .const import DOMAIN  # , ICON
from .coordinator import HepucoUpdateCoordinator
from .entity import HepucoBaseEntity


_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class HeatPumpSignalSensorEntityDescription(SensorEntityDescription):
    """Provide a description of a Heat pump Signal sensor."""

    exists_fn: Callable[[Any], bool] = lambda _: True
    value_fn: Callable[[Any], float | None]


# Sensor descriptions

SENSORS = (
    HeatPumpSignalSensorEntityDescription(
        key="battery_surplus",
        name="Battery surplus",
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        value_fn=lambda data: data.get("battery_surplus"),
        exists_fn=lambda device: bool(device.max_power),
    ),
    HeatPumpSignalSensorEntityDescription(
        key="combined_surplus",
        #name="Excess power",
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        value_fn=lambda data: data.get("combined_surplus"),
        exists_fn=lambda device: bool(device.max_power),
    ),
)


# Set up binary sensor platform

async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Heat pump Signal sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    data = coordinator.data
    entities: list[SensorEntity] = []
    assert data is not None

    entities.extend(
        HepucoSensorEntity(coordinator, description)
        for description in SENSORS
    )
    async_add_entities(entities)


# Define Entities

class HepucoBaseSensorEntity(HepucoBaseEntity, SensorEntity):
    """Defines a base hepuco binary_sensor entity."""


class HepucoSensorEntity(HepucoBaseSensorEntity):
    """Defines a hepuco binary_sensor entity."""

    def __init__(
            self,
            coordinator: HepucoUpdateCoordinator,
            description: HeatPumpSignalSensorEntityDescription,
    ) -> None:
        """Init the hepuco entity."""
        super().__init__(coordinator, description)

        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name="Heat pump Signal",
        )
        self._attr_unique_id = self.entity_description.key

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.data)
        #data = self.data.get(self.entity_description.key)
        #assert data is not None
        #return data

    # @property
    # def native_value(self) -> int | None:
    #     """Return the state of the sensor."""
    #     system_production = self.data.system_production
    #     assert system_production is not None
    #     return self.entity_description.value_fn(system_production)

    # @property
    # def device_info(self) -> DeviceInfo:
    #     """Return device info."""
    #     return DeviceInfo(
    #         identifiers={(DOMAIN, str(self.gateway_serial_num))},
    #         name=self.coordinator.name,
    #         manufacturer="Enphase",
    #         model=self.coordinator.gateway_reader.name,
    #         sw_version=str(self.coordinator.gateway_reader.firmware_version),
    #     )

    # @property
    # def extra_state_attributes(self):
    #     """Return the state attributes."""
    #     data = self.data.get("inverters_production")
    #     if data is not None:
    #         inv = data.get(self._serial_number)
    #         if last_reported := inv.get("lastReportDate"):
    #             dt = dt_util.utc_from_timestamp(last_reported)
    #             return {"last_reported": dt}

    #     return None
