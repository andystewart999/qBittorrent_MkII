"""Config flow for qBittorrent."""
from __future__ import annotations

import logging
from typing import Any

from qbittorrent.client import LoginRequired
from requests.exceptions import RequestException
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.const import (
    CONF_NAME,
    CONF_PASSWORD,
    CONF_URL,
    CONF_USERNAME,
    CONF_VERIFY_SSL
)
from homeassistant.data_entry_flow import FlowResult

from .const import DEFAULT_NAME, DEFAULT_URL, DOMAIN
from .helpers import setup_client

_LOGGER = logging.getLogger(__name__)

USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_URL, default=DEFAULT_URL): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_VERIFY_SSL, default=False): bool,
    }
)

USER_EVENTS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EVENT_COMPLETE, default=DEFAULT_EVENT_COMPLETE): bool,
        vol.Required(CONF_EVENT_ADDED, default=DEFAULT_EVENT_ADDED): bool,
        vol.Required(CONF_EVENT_REMOVED, default=DEFAULT_EVENT_REMOVED): bool,
    }
)


class QbittorrentConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for the qBittorrent integration."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a user-initiated config flow."""
        errors = {}

        if user_input is not None:
            self._async_abort_entries_match({CONF_URL: user_input[CONF_URL]})
            try:
                await self.hass.async_add_executor_job(
                    setup_client,
                    user_input[CONF_URL],
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                    user_input[CONF_VERIFY_SSL],
                )
            except LoginRequired:
                errors = {"base": "invalid_auth"}
            except RequestException:
                errors = {"base": "cannot_connect"}
            else:

                #Show the next page of the config flow
                return await self.async_step_events()
                
                #return self.async_create_entry(title=DEFAULT_NAME, data=user_input)

        schema = self.add_suggested_values_to_schema(USER_DATA_SCHEMA, user_input)
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_events(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Second page of the config flow"""
        errors = {}

        if user_input is not None:
            self._async_abort_entries_match({CONF_URL: user_input[CONF_URL]})   #### what is this?   only just copied and pasted this section, lots to change still
            
            #Just go straight to creating the entry
            return self.async_create_entry(title=DEFAULT_NAME, data=user_input)

        schema = self.add_suggested_values_to_schema(USER_EVENTS_SCHEMA, user_input)
        return self.async_show_form(step_id="events", data_schema=schema, errors=errors)
   

    async def async_step_import(self, config: dict[str, Any]) -> FlowResult:
        """Import a config entry from configuration.yaml."""
        self._async_abort_entries_match({CONF_URL: config[CONF_URL]})
        return self.async_create_entry(
            title=config.get(CONF_NAME, DEFAULT_NAME),
            data={
                CONF_URL: config[CONF_URL],
                CONF_USERNAME: config[CONF_USERNAME],
                CONF_PASSWORD: config[CONF_PASSWORD],
                CONF_VERIFY_SSL: True,
            },
        )
