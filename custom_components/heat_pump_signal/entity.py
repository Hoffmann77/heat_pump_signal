"""Home assistant base entities."""

from __future__ import annotations

from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo

from .const import DOMAIN
from .coordinator import SignalUpdateCoordinator



class HepucoBaseEntity(CoordinatorEntity[SignalUpdateCoordinator]):
    """Defines a hepuco coordinator entity."""

    _attr_has_entity_name = True

    def __init__(
            self,
            coordinator: SignalUpdateCoordinator,
            description: EntityDescription,
    ) -> None:
        """Init the hepuco base entity."""
        super().__init__(coordinator)
        self.entity_description = description
        

    @property
    def data(self) -> dict:
        """Return hepuco data."""
        data = self.coordinator.data
        assert data is not None
        return data


class SignalCoordinatorEntity(CoordinatorEntity[SignalUpdateCoordinator]):
    """Coordinator entity."""

    entity_description: EntityDescription
    _attr_has_entity_name = True
 
    def __init__(
            self,
            coordinator: SignalUpdateCoordinator,
            description: EntityDescription,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)

        self.entity_description = description
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name="Heat pump Signal",
        )
        