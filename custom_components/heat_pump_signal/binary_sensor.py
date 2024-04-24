"""Binary sensor entities for the Heat pump Signal integration."""

import logging
from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntityDescription
)

from .const import DOMAIN
from .coordinator import SignalUpdateCoordinator
from .entity import SignalCoordinatorEntity


_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class SignalBinarySensorDescription(BinarySensorEntityDescription):
    """A class that describes binary sensor entities.

    Adds the keyword arguments 'exist_fn' and 'value_fn' to the dataclass.
    """

    value_fn: Callable[[dict], bool]
    exists_fn: Callable[[dict], bool] = lambda _: True


BINARY_SENSORS = (
    SignalBinarySensorDescription(
        key="pv_signal",
        name="PV Signal",
        device_class=BinarySensorDeviceClass.POWER,
        value_fn=lambda data: data.get("pv_signal"),
        exists_fn=lambda entry: bool(entry.options.get("pv_signal")),
    ),
    SignalBinarySensorDescription(
        key="price_signal",
        name="Price Signal",
        # device_class=BinarySensorDeviceClass.POWER,
        value_fn=lambda data: data.get("price_signal"),
        exists_fn=lambda entry: bool(entry.options.get("price_signal")),
    ),
    SignalBinarySensorDescription(
        key="co2_signal",
        name="Renewable energy Signal",
        # device_class=BinarySensorDeviceClass.POWER,
        value_fn=lambda data: data.get("co2_signal"),
        exists_fn=lambda entry: bool(entry.options.get("co2_signal")),
    ),
    SignalBinarySensorDescription(
        key="heat_pump_signal",
        name="Heat pump Signal",
        # device_class=BinarySensorDeviceClass.POWER,
        value_fn=lambda data: data.get("heat_pump_signal"),
        exists_fn=lambda entry: bool(entry.options.get("heat_pump_signal")),  # TODO: how to check if value exist in data dict
    ),
)


async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the binary sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        SignalBinarySensor(coordinator, description)
        for description in BINARY_SENSORS
        if description.exists_fn(entry)
    )


class SignalBinarySensor(SignalCoordinatorEntity, BinarySensorEntity):
    """Defines a hepuco binary_sensor entity."""

    entity_description: SignalBinarySensorDescription

    def __init__(
            self,
            coordinator: SignalUpdateCoordinator,
            description: SignalBinarySensorDescription,
    ) -> None:
        """Initialize the binary sensor entity."""
        super().__init__(coordinator, description)

        self._attr_unique_id = self.entity_description.key

    @property
    def is_on(self) -> bool:
        """Return the binary state of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data)
