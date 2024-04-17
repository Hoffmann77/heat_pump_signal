"""Config flow for Enphase gateway integration."""

from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
from homeassistant.const import CONF_NAME

from .const import (
    DOMAIN, 
    
    CONF_LOCK_INTERVAL, CONF_PV_SIGNAL, CONF_PRICE_SIGNAL, CONF_CO2_SIGNAL,
    
    CONF_THRESHOLD, CONF_STATIC_THRESHOLD, CONF_DYNAMIC_THRESHOLD, 
    CONF_OPTIONAL_THRESHOLDS, 
    
    CONF_GRID, CONF_GRID_INVERTED, CONF_PV_PRODUCTION,
    CONF_CONSUMPTION, CONF_BATTERY, CONF_BATTERY_INVERTED, CONF_BATTERY_SOC,
    CONF_HEATPUMP, CONF_HEATPUMP_INVERTED, 
    CONF_THRESHOLD_OPTIONAL, CONF_BAT_MIN_SOC, CONF_BAT_MIN_POWER,
    CONF_HYSTERESIS, CONF_LOCK_INTERVAL, CONF_REBOUND_INTERVAL,
    CONF_BUFFER_POWER,
)


_LOGGER = logging.getLogger(__name__)

DEFAULT_TITLE = "Heat pump signal"


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the Heat pump coordinator."""

    VERSION = 1
    MINOR_VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self.title = DEFAULT_TITLE
        self.data = {}
        self.options = {}

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the user step.

        Allows the user to specify a name and enable the desired signals.

        """
        errors: dict[str, str] = {}
        placeholders: dict[str, str] = {}

        signals = (CONF_PV_SIGNAL, CONF_PRICE_SIGNAL, CONF_CO2_SIGNAL)

        if user_input is not None:
            title = user_input.pop(CONF_NAME)
            data = user_input

            if not title.lstrip(" "):
                errors["base"] = "name_invalid"

            # Validate that at least one Signal is enbabled.
            found = False
            for signal in signals:
                if user_input.get(signal, False):
                    found = True
                    break

            if not found:
                errors["base"] = "no_signal_enabled"

            if not errors:
                self.title = title
                self.data = data
                return await self.async_step_pv_signal()

        user_input = user_input or {}
        return self.async_show_form(
            step_id="user",
            data_schema=self.get_shema_user_step(user_input),
            description_placeholders=placeholders,
            errors=errors,
        )

    async def async_step_pv_signal(self, user_input=None) -> FlowResult:
        """Handle the pv signal configuration step."""
        errors = {}
        placeholders = {}

        # skip step if the signal is not enabled.
        if not self.data.get(CONF_PV_SIGNAL):
            return await self.async_step_price_signal()

        # validate user input
        if user_input is not None:
            dynamic_threshold = user_input.pop(CONF_DYNAMIC_THRESHOLD)
            data = user_input

            if dynamic_threshold:
                data[CONF_DYNAMIC_THRESHOLD] = None

            self.options["pv_signal"] = data

            if not errors:
                return await self.async_step_price_signal()

        return self.async_show_form(
            step_id="pv_signal",
            data_schema=self.get_shema_pv_signal_step(),
            description_placeholders=placeholders,
            errors=errors,
        )

    async def async_step_price_signal(self, user_input=None) -> FlowResult:
        """Handle the price signal configuration step."""
        errors = {}
        placeholders = {}

        # skip step if the signal is not enabled.
        if not self.data.get(CONF_PRICE_SIGNAL):
            return await self.async_step_co2_signal()

        # validate user input
        if user_input is not None:
            data = user_input
            self.options["price_signal"] = data

            if not errors:
                return await self.async_step_co2_signal()

        return self.async_show_form(
            step_id="price_signal",
            data_schema=self.get_shema_price_signal_step(),
            description_placeholders=placeholders,
            errors=errors,
        )

    async def async_step_co2_signal(self, user_input=None) -> FlowResult:
        """Handle the co2 signal configuration step."""
        errors = {}
        placeholders = {}

        # skip step if the signal is not enabled.
        if not self.data.get(CONF_CO2_SIGNAL, False):
            return await self.async_step_create_entry()

        # validate user input
        if user_input is not None:
            data = user_input
            self.options["co2_signal"] = data

            if not errors:
                return await self.async_step_create_entry()

        return self.async_show_form(
            step_id="co2_signal",
            data_schema=self.get_shema_co2_signal_step(),
            description_placeholders=placeholders,
            errors=errors,
        )

    async def async_step_create_entry(self) -> FlowResult:
        """Create the config entry."""
        return self.async_create_entry(
            title=self.title,  # data[CONF_NAME],
            data=self.data,
            options=self.options,
        )

    @callback
    def get_shema_user_step(self, user_input: dict) -> vol.Schema:
        """Return the schema for the user step."""
        schema = {
            vol.Required(
                CONF_NAME, default=user_input.get(CONF_NAME, "")
            ): str,
            vol.Required(CONF_LOCK_INTERVAL): selector.DurationSelector(
                selector.DurationSelectorConfig(enable_day=False)
            ),
            vol.Required(CONF_PV_SIGNAL): selector.BooleanSelector(
                selector.BooleanSelectorConfig()
            ),
            vol.Required(CONF_PRICE_SIGNAL): selector.BooleanSelector(
                selector.BooleanSelectorConfig()
            ),
            vol.Required(CONF_CO2_SIGNAL): selector.BooleanSelector(
                selector.BooleanSelectorConfig()
            ),
        }
        return vol.Schema(schema)

    @callback
    def get_shema_pv_signal_step(self) -> vol.Schema:
        """Return the shema for the pv_signal config step."""
        schema = {
            vol.Required(CONF_GRID): selector.EntitySelector(
                selector.EntitySelectorConfig()
            ),
            vol.Optional(CONF_GRID_INVERTED): selector.BooleanSelector(
                selector.BooleanSelectorConfig()
            ),
            vol.Optional(CONF_BATTERY_SOC): selector.EntitySelector(
                selector.EntitySelectorConfig()
            ),
            vol.Optional(CONF_BATTERY): selector.EntitySelector(
                selector.EntitySelectorConfig()
            ),
            vol.Optional(CONF_BATTERY_INVERTED): selector.BooleanSelector(
                selector.BooleanSelectorConfig()
            ),
            vol.Optional(CONF_HEATPUMP): selector.EntitySelector(
                selector.EntitySelectorConfig()
            ),
            vol.Optional(CONF_HEATPUMP_INVERTED): selector.BooleanSelector(
                selector.BooleanSelectorConfig()
            ),
            # vol.Optional(CONF_THRESHOLD_ENTITY): selector.EntitySelector(
            #     selector.EntitySelectorConfig()
            # ),
            # # Base threshold
            vol.Required(CONF_STATIC_THRESHOLD): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=2**32,
                    unit_of_measurement="Watt",
                    mode="box",
                ),
            ),
            vol.Optional(CONF_DYNAMIC_THRESHOLD): selector.BooleanSelector(
                selector.BooleanSelectorConfig()
            ),
            # !! disabled for now !!
            # Optional thresholds
            # vol.Optional(CONF_THRESHOLDS_OPTIONAL): selector.TextSelector(
            #     selector.NumberSelectorConfig(
            #         # type="number",
            #         multiple=True,
            #     ),
            # ),
            # Buffer power
            vol.Required(
                CONF_BUFFER_POWER,
                default=0,
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=10**8,
                    unit_of_measurement="Watt",
                    mode="box",
                ),
            ),
            # Battery minimum SoC
            vol.Required(
                CONF_BAT_MIN_SOC,
                default=0,
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=100,
                    unit_of_measurement="%",
                    mode="slider",
                ),
            ),
            # Battery minimum power
            vol.Required(
                CONF_BAT_MIN_POWER,
                default=0,
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=10**8,
                    unit_of_measurement="Watt",
                    mode="box",
                ),
            ),
            # Hysteresis
            vol.Required(
                CONF_HYSTERESIS,
                default=200,
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=10**8,
                    unit_of_measurement="Watt",
                    mode="box",
                ),
            ),
        }
        return vol.Schema(schema)

    @callback
    def get_shema_price_signal_step(self) -> vol.Schema:
        """Return the schema for the price signal step."""
        schema = {}

        return vol.Schema(schema)

    @callback
    def get_shema_co2_signal_step(self) -> vol.Schema:
        """Return the schema for the co2 signal step."""
        schema = {}

        return vol.Schema(schema)

    # @staticmethod
    # @callback
    # def async_get_options_flow(
    #         config_entry: config_entries.ConfigEntry,
    # ) -> config_entries.OptionsFlow:
    #     """Create the options flow."""
    #     return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle an options flow for the Heat pump coordinator."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize the options flow."""
        self.config_entry = config_entry
        self.options = config_entry.options

    async def async_step_init(self, user_input=None) -> FlowResult:
        """Manage the options.

        Return the user_step.

        """
        return await self.async_step_user()

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the user step.

        Allows the user to enter a name and select the required entities.

        """
        errors: dict[str, str] = {}
        # description_placeholders: dict[str, str] = {}

        if user_input is not None:
            data = user_input
            # data = {CONF_NAME: name} | user_input
            self.step_data["user"] = data

            return await self.async_step_config()

        user_input = user_input or {}
        return self.async_show_form(
            step_id="user",
            data_schema=self.get_shema_user_step(user_input),
            # description_placeholders=description_placeholders,
            errors=errors,
        )

    async def async_step_config(self, user_input=None) -> FlowResult:
        """Handle the configuration step.

        Allows the user to configure the parameters.

        """
        errors: dict[str, str] = {}
        description_placeholders: dict[str, str] = {}
        user_step_data = self.step_data["user"]

        if user_input is not None:
            # handle user_input data
            return self.async_create_entry(
                title=user_step_data[CONF_NAME],
                data=user_step_data,
                options=user_input,
            )
            # TODO: handle config entry update
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=self.updated_config
            )
            return self.async_create_entry(
                title=self.updated_config["name"], data=self.updated_config
            )

        # description_placeholders["gateway_type"] = self._gateway_reader.name
        return self.async_show_form(
            step_id="config",
            data_schema=self.get_shema_config_step(),
            errors=errors,
            description_placeholders=description_placeholders
        )

    @callback
    def get_shema_user_step(self) -> vol.Schema:
        """Return the schema for the user step."""
        data = self.config_entry.data  # default data
        schema = {
            vol.Required(
                CONF_PV_PRODUCTION,
                description={"suggested_value": data.get(CONF_PV_PRODUCTION, "")},
            ): selector.EntitySelector(selector.EntitySelectorConfig()),

            vol.Required(
                CONF_GRID,
                description={
                    "suggested_value": data.get(CONF_GRID, "")
                },
            ): selector.EntitySelector(selector.EntitySelectorConfig()),
        }
        return vol.Schema(schema)

    @callback
    def get_shema_config_step(self) -> vol.Schema:
        """Return the schema for the user step."""
        data = self.options  # default data
        schema = {
            vol.Required(
                CONF_HEATPUMP_TYP_CONS, default=data.get(CONF_HEATPUMP_TYP_CONS, "")
            ): int,
            vol.Required(
                CONF_THRESHOLD, default=data.get(CONF_THRESHOLD, "")
            ): int,
        }
        return vol.Schema(schema)





# class GatewayConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
#     """Handle a config flow for Enphase Gateway."""

#     VERSION = 2

#     def __init__(self):
#         """Initialize an gateway flow."""
#         self.ip_address = None
#         self.username = None
#         self._reauth_entry = None
#         self._discovery_info = None
#         self._gateway_reader = None
#         self._step_data = {}

#     async def async_step_zeroconf(
#             self,
#             discovery_info: zeroconf.ZeroconfServiceInfo,
#     ) -> FlowResult:
#         """Handle a config flow initialized by zeroconf discovery.

#         Update the IP adress of discovered devices unless the system
#         option to enable newly discoverd entries is off.

#         Parameters
#         ----------
#         discovery_info : zeroconf.ZeroconfServiceInfo
#             Home Assistant zeroconf discovery information.

#         Returns
#         -------
#         FlowResult
#             Config flow result.

#         """
#         _LOGGER.debug(f"""Zeroconf discovery: {discovery_info}""")
#         self._discovery_info = discovery_info
#         serial_num = discovery_info.properties["serialnum"]
#         current_entry = await self.async_set_unique_id(serial_num)

#         if current_entry and current_entry.pref_disable_new_entities:
#             _LOGGER.debug(
#                 f"""
#                 Gateway autodiscovery/ip update disabled for: {serial_num},
#                 IP detected: {discovery_info.host} {current_entry.unique_id}
#                 """
#             )
#             return self.async_abort(reason="pref_disable_new_entities")

#         self.ip_address = discovery_info.host
#         self._abort_if_unique_id_configured({CONF_HOST: self.ip_address})

#         # set unique_id if not set for an entry with the same IP adress
#         for entry in self._async_current_entries(include_ignore=False):
#             if not entry.unique_id and entry.data.get(CONF_HOST) == self.ip_adress:
#                 #  update title with serial_num if title was not changed
#                 if entry.title in {DEFAULT_TITLE, LEGACY_TITLE}:
#                     title = f"{entry.title} {serial_num}"
#                 else:
#                     title = entry.title
#                 self.hass.config_entries.async_update_entry(
#                     entry, title=title, unique_id=serial_num
#                 )
#                 self.hass.async_create_task(
#                     self.hass.config_entries.async_reload(entry.entry_id)
#                 )
#                 return self.async_abort(reason="already_configured")

#         return await self.async_step_user()

#     async def async_step_user(
#             self,
#             user_input: dict[str, Any] | None = None,
#     ) -> FlowResult:
#         """Handle the user step.

#         Parameters
#         ----------
#         user_input : dict[str, Any] | None, optional
#             Form user input. The default is None.

#         Returns
#         -------
#         FlowResult
#             Config flow result.

#         """
#         errors: dict[str, str] = {}
#         description_placeholders: dict[str, str] = {}

#         if self._reauth_entry:
#             host = self._reauth_entry.data[CONF_HOST]
#         else:
#             host = (user_input or {}).get(CONF_HOST) or self.ip_address or ""

#         if user_input is not None:
#             use_legacy_name = user_input.pop(CONF_USE_LEGACY_NAME, False)

#             if not self._reauth_entry and host in self._get_current_hosts():
#                 return self.async_abort(reason="already_configured")

#             try:
#                 gateway_reader = await validate_input(
#                     self.hass,
#                     host,
#                     username=user_input.get(CONF_USERNAME),
#                     password=user_input.get(CONF_PASSWORD),
#                 )
#             except CONFIG_FLOW_USER_ERROR as err:
#                 r = re.split('(?<=.)(?=[A-Z])', err.__class__.__name__)
#                 errors["base"] = "_".join(r).lower()
#             except CannotConnect:
#                 errors["base"] = "cannot_connect"
#             except Exception:
#                 _LOGGER.exception("Unexpected exception")
#                 errors["base"] = "unknown"
#             else:
#                 self._gateway_reader = gateway_reader
#                 name = self._generate_name(use_legacy_name)

#                 if self._reauth_entry:
#                     self.hass.config_entries.async_update_entry(
#                         self._reauth_entry,
#                         data=self._reauth_entry.data | user_input,
#                     )
#                     self.hass.async_create_task(
#                         self.hass.config_entries.async_reload(
#                             self._reauth_entry.entry_id
#                         )
#                     )
#                     return self.async_abort(reason="reauth_successful")

#                 if not self.unique_id:
#                     await self.async_set_unique_id(
#                         gateway_reader.serial_number
#                     )
#                     name = self._generate_name(use_legacy_name)
#                     #  data[CONF_NAME] = self._generate_name(use_legacy_name)

#                 else:
#                     self._abort_if_unique_id_configured()

#                 _data = {CONF_HOST: host, CONF_NAME: name} | user_input
#                 self._step_data["user"] = _data
#                 return await self.async_step_config()

#         if self.unique_id:
#             self.context["title_placeholders"] = {
#                 CONF_SERIAL_NUM: self.unique_id,
#                 CONF_HOST: self.ip_address,
#             }

#         return self.async_show_form(
#             step_id="user",
#             data_schema=self._generate_shema_user_step(),
#             description_placeholders=description_placeholders,
#             errors=errors,
#         )

#     async def async_step_config(
#             self,
#             user_input: dict[str, Any] | None = None,
#     ) -> FlowResult:
#         """Handle the configuration step.

#         Parameters
#         ----------
#         user_input : dict[str, Any] | None, optional
#             Form user input. The default is None.

#         Returns
#         -------
#         FlowResult
#             Config flow result.

#         """
#         errors: dict[str, str] = {}
#         description_placeholders: dict[str, str] = {}
#         step_data = self._step_data["user"]

#         if user_input is not None:
#             return self.async_create_entry(
#                 title=step_data[CONF_NAME],
#                 data=step_data,
#                 options=user_input,
#             )

#         description_placeholders["gateway_type"] = self._gateway_reader.name

#         return self.async_show_form(
#             step_id="config",
#             data_schema=self._generate_shema_config_step(),
#             errors=errors,
#             description_placeholders=description_placeholders
#         )

#     async def async_step_reauth(
#             self,
#             user_input: dict[str, Any] | None = None) -> FlowResult:
#         """Handle reauth.

#         Parameters
#         ----------
#         user_input : dict[str, Any] | None, optional
#             Form user input. The default is None.

#         Returns
#         -------
#         FlowResult
#             Config flow result.

#         """
#         self._reauth_entry = self.hass.config_entries.async_get_entry(
#             self.context["entry_id"]
#         )

#         if self._reauth_entry is not None:
#             if unique_id := self._reauth_entry.unique_id:
#                 await self.async_set_unique_id(
#                     unique_id,
#                     raise_on_progress=False
#                 )

#         return await self.async_step_user()

#     @callback
#     def _generate_shema_user_step(self):
#         """Generate schema."""
#         if self.ip_address:
#             ip_address_val = vol.In([self.ip_address])
#         else:
#             ip_address_val = str

#         schema = {
#             vol.Required(CONF_HOST, default=self.ip_address): ip_address_val,
#             vol.Optional(CONF_USERNAME, default=self.username or "envoy"): str,
#             vol.Optional(CONF_PASSWORD, default=""): str,
#             vol.Optional(CONF_USE_LEGACY_NAME, default=False): bool,
#         }
#         return vol.Schema(schema)

#     @callback
#     def _generate_shema_config_step(self):
#         """Generate schema."""
#         schema = {
#             vol.Required(CONF_INVERTERS): selector(
#                 {
#                     "select": {
#                         "translation_key": CONF_INVERTERS,
#                         "mode": "dropdown",
#                         "options": ["gateway_sensor", "device", "disabled"],
#                     }
#                 }
#             ),
#         }

#         if self._gateway_reader.gateway.encharge_inventory:
#             schema.update(
#                 {vol.Optional(CONF_ENCHARGE_ENTITIES, default=True): bool}
#             )
#         return vol.Schema(schema)

#     @callback
#     def _get_current_hosts(self):
#         """Return a set of hosts."""
#         return {
#             entry.data[CONF_HOST]
#             for entry in self._async_current_entries(include_ignore=False)
#             if CONF_HOST in entry.data
#         }

#     def _generate_name(self, use_legacy_name=False):
#         """Return the name of the entity."""
#         name = LEGACY_TITLE if use_legacy_name else DEFAULT_TITLE
#         if self.unique_id:
#             return f"{name} {self.unique_id}"
#         return name

#     # async def _async_set_unique_id_from_gateway(
#     #         self,
#     #         gateway_reader: GatewayReader) -> bool:
#     #     """Set the unique id by fetching it from the gateway."""
#     #     serial_num = None
#     #     with contextlib.suppress(httpx.HTTPError):
#     #         serial_num = await gateway_reader.get_serial_number()
#     #     if serial_num:
#     #         await self.async_set_unique_id(serial_num)
#     #         return True
#     #     return False

#     @staticmethod
#     @callback
#     def async_get_options_flow(
#             config_entry: config_entries.ConfigEntry
#     ) -> config_entries.OptionsFlow:
#         """Create the options flow."""
#         return GatewayOptionsFlow(config_entry)


# class GatewayOptionsFlow(config_entries.OptionsFlow):
#     """Handle a options flow for Enphase Gateway."""

#     def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
#         """Initialize options flow."""
#         self.config_entry = config_entry

#     async def async_step_init(
#             self,
#             user_input: dict[str, Any] | None = None) -> FlowResult:
#         """Manage the options."""
#         if user_input is not None:
#             return self.async_create_entry(title="", data=user_input)

#         return self.async_show_form(
#             step_id="init",
#             data_schema=self._generate_data_shema()
#         )

#     @callback
#     def _generate_data_shema(self):
#         """Generate schema."""
#         options = self.config_entry.options
#         options_keys = options.keys()
#         default_inverters = options.get(CONF_INVERTERS, "disabled")
#         # default_data_update_interval = options.get(
#         #     CONF_DATA_UPDATE_INTERVAL, "moderate"
#         # )
#         schema = {
#             vol.Optional(
#                 CONF_INVERTERS, default=default_inverters): selector(
#                     {
#                         "select": {
#                             "translation_key": CONF_INVERTERS,
#                             "mode": "dropdown",
#                             "options": [
#                                 "gateway_sensor", "device", "disabled"
#                             ],
#                         }
#                     }
#             ),
#         }
#         if CONF_ENCHARGE_ENTITIES in options_keys:
#             schema.update({
#                 vol.Optional(
#                     CONF_ENCHARGE_ENTITIES,
#                     default=options.get(CONF_ENCHARGE_ENTITIES)
#                 ): bool,
#             })
#         if CONF_CACHE_TOKEN in options_keys:
#             schema.update({
#                 vol.Optional(
#                     CONF_CACHE_TOKEN,
#                     default=options.get(CONF_CACHE_TOKEN)
#                 ): bool,
#             })
#         return vol.Schema(schema)
