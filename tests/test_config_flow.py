"""Test the Heat pump signal config flow."""

from unittest.mock import AsyncMock, patch

import pytest

from homeassistant.core import HomeAssistant
from homeassistant import config_entries, data_entry_flow
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.const import CONF_API_KEY

from custom_components.heat_pump_signal.const import DOMAIN
#from custom_components.heat_pump_signal.const import config_flow


from .const import MOCK_CONFIG, MOCK_CONFIG_PV_SIGNAL




# This fixture bypasses the actual setup of the integration
# since we only want to test the config flow. We test the
# actual functionality of the integration in other test modules.
# @pytest.fixture(autouse=True)
# def bypass_setup_fixture():
#     """Prevent setup."""
#     with patch(
#         "custom_components.intex_spa.async_setup",
#         return_value=True,
#     ), patch(
#         "custom_components.intex_spa.async_setup_entry",
#         return_value=True,
#     ):
#         yield







#@pytest.mark.usefixtures("")
async def test_form(hass: HomeAssistant) -> None:
    
    # Initialize a config flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    # Validate that the config flow returns the form for the user step
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {}





    with patch(
            "custom_components.heat_pump_signal.async_setup_entry",
            return_value=True,
    ) as mock_setup:
        result_2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=MOCK_CONFIG, # infuse input data here
        )
        await hass.async_block_till_done()
    

    assert result_2["type"] is FlowResultType.FORM # CREATE_ENTRY
    # assert result_2["title"] == MOCK_CONFIG["name"]
    # assert result_2["data"] == MOCK_CONFIG
    
    
    with patch(
            "custom_components.heat_pump_signal.async_setup_entry",
            return_value=True,
    ) as mock_setup:
        result_3 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=MOCK_CONFIG_PV_SIGNAL, # infuse input data here
        )
        await hass.async_block_till_done()
    
    assert result_3["type"] is FlowResultType.CREATE_ENTRY
    
    # assert result_2["title"] == MOCK_CONFIG["name"]
    # assert result_2["data"] == MOCK_CONFIG

    
    
    
    
    
    # # If a user were to enter `test_username` for username and `test_password`
    # # for password, it would result in this function call
    # result = await hass.config_entries.flow.async_configure(
    #     result["flow_id"], user_input=MOCK_CONFIG
    # )
    
    # result2 = await hass.config_entries.flow.async_configure(
    #         result["flow_id"],
    #         {
    #             "location": config_flow.TYPE_USE_HOME,
    #             "api_key": "api_key",
    #         },
    
    
    
    
    

    

    


# HINT: https://github.com/jwillemsen/daikin_onecta/blob/master/tests/test_config_flow.py
# HINT: https://github.com/mathieu-mp/homeassistant-intex-spa/blob/main/tests/test_config_flow.py

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