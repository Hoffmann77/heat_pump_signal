"""Home assistant base entities."""

from __future__ import annotations


from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import HepucoUpdateCoordinator


class HepucoBaseEntity(CoordinatorEntity[HepucoUpdateCoordinator]):
    """Defines a hepuco coordinator entity."""

    _attr_has_entity_name = True

    def __init__(
            self,
            coordinator: HepucoUpdateCoordinator,
            description: EntityDescription,
    ) -> None:
        """Init the hepuco base entity."""
        self.entity_description = description
        # self.gateway_serial_num = coordinator.gateway_reader.serial_number
        super().__init__(coordinator)

    @property
    def data(self) -> dict:
        """Return hepuco data."""
        data = self.coordinator.data
        assert data is not None
        return data
