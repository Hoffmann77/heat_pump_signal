"""Fixtures for Heat pump signal integration tests."""

# from typing import Any
from unittest.mock import AsyncMock
# from unittest.mock import patch

import pytest

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from homeassistant.setup import async_setup_component

from custom_components.heat_pump_signal.const import DOMAIN

pytest_plugins = "pytest_homeassistant_custom_component"


# This fixture enables loading custom integrations in all tests.
# Remove to enable selective use of this fixture
@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable loading custom integrations."""
    yield


@pytest.fixture(name="config_entry")
async def mock_config_entry(hass: HomeAssistant) -> MockConfigEntry:
    """Return a MockConfigEntry for testing."""
    return MockConfigEntry(
        domain=DOMAIN,
        data={"CONF_API_KEY": "api_key", "location": ""},
        entry_id="904a74160aa6f335526706bee85dfb83",
    )


@pytest.fixture(name="setup_integration")
async def mock_setup_integration(
    hass: HomeAssistant, config_entry: MockConfigEntry
) -> None:
    """Fixture for setting up the component."""
    config_entry.add_to_hass(hass)

    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()



# @pytest.fixture(name="config_entry")
# def mock_config_entry_fixture(hass: HomeAssistant) -> MockConfigEntry:
#     """Mock a config entry."""
#     mock_entry = MockConfigEntry(
#         domain="daikin_onecta",
#         data={
#             "auth_implementation": "cloud",
#             "token": {
#                 "refresh_token": "mock-refresh-token",
#                 "access_token": "mock-access-token",
#                 "type": "Bearer",
#                 "expires_in": 60,
#                 "expires_at": 1000,
#                 "scope": 1,
#             },
#         },
#     )
#     mock_entry.add_to_hass(hass)

#     return mock_entry


