"""Test the config flow."""

from unittest.mock import AsyncMock, patch

import pytest

from homeassistant.core import HomeAssistant
from homeassistant import config_entries, data_entry_flow
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.const import CONF_API_KEY

from custom_components.heat_pump_signal.const import DOMAIN
from custom_components.heat_pump_signal.const import config_flow


#@pytest.mark.usefixtures("")
async def test_form(hass: HomeAssistant) -> None:
    
    # Initialize a config flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    # Check that the config flow shows the user form as the first step
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] is None
    


# @pytest.mark.usefixtures("electricity_maps")
# async def test_form_home(hass: HomeAssistant) -> None:
#     """Test we get the form."""

#     result = await hass.config_entries.flow.async_init(
#         DOMAIN, context={"source": config_entries.SOURCE_USER}
#     )
#     assert result["type"] is FlowResultType.FORM
#     assert result["errors"] is None

#     with patch(
#         "homeassistant.components.co2signal.async_setup_entry",
#         return_value=True,
#     ) as mock_setup_entry:
#         result2 = await hass.config_entries.flow.async_configure(
#             result["flow_id"],
#             {
#                 "location": config_flow.TYPE_USE_HOME,
#                 "api_key": "api_key",
#             },
#         )
#         await hass.async_block_till_done()

#     assert result2["type"] is FlowResultType.CREATE_ENTRY
#     assert result2["title"] == "CO2 Signal"
#     assert result2["data"] == {
#         "api_key": "api_key",
#     }
#     assert len(mock_setup_entry.mock_calls) == 1