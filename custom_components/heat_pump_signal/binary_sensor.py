"""Home assistant binary sensors for the hepuco integration."""

import logging
from collections.abc import Callable
from dataclasses import dataclass

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntityDescription
)

from .const import DOMAIN, ICON
from .coordinator import HepucoUpdateCoordinator
from .entity import HepucoBaseEntity


_LOGGER = logging.getLogger(__name__)
# This is the key identifier for this entity
    # key: str

    # device_class: str | None = None
    # entity_category: EntityCategory | None = None
    # entity_registry_enabled_default: bool = True
    # entity_registry_visible_default: bool = True
    # force_update: bool = False
    # icon: str | None = None
    # has_entity_name: bool = False
    # name: str | UndefinedType | None = UNDEFINED
    # translation_key: str | None = None
    # translation_placeholders: Mapping[str, str] | None = None
    # unit_of_measurement: str | None = None


@dataclass(frozen=True, kw_only=True)
class HepucoBinarySensorEntityDescription(BinarySensorEntityDescription):
    """A class that describes binary sensor entities.

    Adds the keyword arguments 'exist_fn' and 'value_fn' to the dataclass.
    """

    exists_fn: Callable[[Any], bool] = lambda _: True
    value_fn: Callable[[Any], bool]


# Binary sensor descriptions

BINARY_SENSORS = (
    HepucoBinarySensorEntityDescription(
        key="partial_excess",
        name="Grid Status",
        device_class=BinarySensorDeviceClass.RUNNING,
        value_fn=lambda device: device.power,
        exists_fn=lambda device: bool(device.max_power),
    ),
    HepucoBinarySensorEntityDescription(
        key="full_excess",
        name="Grid Status",
        device_class=BinarySensorDeviceClass.RUNNING,
        value_fn=lambda device: device.power,
        exists_fn=lambda device: bool(device.max_power),
    ),
)


# Set up binary sensor platform

async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the hepuco binary sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    data = coordinator.data
    entities: list[BinarySensorEntity] = []
    assert data is not None

    entities.extend(
        HepucoBinarySensorEntity(coordinator, description)
        for description in BINARY_SENSORS
    )
    async_add_entities(entities)


# Define Entities

class HepucoBaseBinarySensorEntity(HepucoBaseEntity, BinarySensorEntity):
    """Defines a base hepuco binary_sensor entity."""


class HepucoBinarySensorEntity(HepucoBaseBinarySensorEntity):
    """Defines a hepuco binary_sensor entity."""

    def __init__(
            self,
            coordinator: HepucoUpdateCoordinator,
            description: HepucoBinarySensorEntityDescription,
    ) -> None:
        """Init the hepuco entity."""
        super().__init__(coordinator, description)
        # self._attr_unique_id = f"{self.gateway_serial_num}_{description.key}"

    @property
    def unique_id(self) -> str:
        """Return the unique identifier."""
        return self.entity_description.key

    @property
    def is_on(self) -> bool:
        """Return the status of the requested attribute."""
        # return self.coordinator.data.get("grid_status") == "closed"
        return False
