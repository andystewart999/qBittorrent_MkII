"""Config flow for qBittorrent."""
from __future__ import annotations

#import logging
from typing import Any

import qbittorrentapi
from qbittorrentapi import Client

from requests.exceptions import RequestException
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlow
from homeassistant.core import callback
from homeassistant.const import (
    CONF_NAME,
    CONF_URL,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_VERIFY_SSL,
    CONF_SCAN_INTERVAL,
)
from homeassistant.data_entry_flow import FlowResult

from .const import *
from .helpers import setup_client
from urllib.parse import urlparse

USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_URL, default=DEFAULT_URL): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_VERIFY_SSL, default=DEFAULT_VERIFY_SSL): bool,
        vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SENSOR_SCAN_INTERVAL): int,
    }
)

USER_EVENTS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EVENT_COMPLETE, default=DEFAULT_EVENT_COMPLETE): bool,
        vol.Required(CONF_EVENT_ADDED, default=DEFAULT_EVENT_ADDED): bool,
        vol.Required(CONF_EVENT_REMOVED, default=DEFAULT_EVENT_REMOVED): bool,
        vol.Required(CONF_EVENT_SCAN_INTERVAL, default=DEFAULT_EVENT_SCAN_INTERVAL): int,
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
                
            except qbittorrentapi.LoginFailed as ex:
                errors = {"base": "invalid_auth"}

            except RequestException:
                errors = {"base": "cannot_connect"}

            return self.async_create_entry(title=DEFAULT_NAME + ' - ' + urlparse(user_input[CONF_URL]).hostname, data=user_input)

        return self.async_show_form(step_id="user", data_schema=USER_DATA_SCHEMA, errors=errors)


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

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return qBittorrentOptionsFlowHandler()

class qBittorrentOptionsFlowHandler(config_entries.OptionsFlow):
    """qBittorrent config flow options handler"""

    @property
    def config_entry(self):
        return self.hass.config_entries.async_get_entry(self.handler)

    async def async_step_init(self, user_input=None):
        """Handle an options flow initalised by the user"""
        errors = {}
        
        if user_input is not None:
            changed = self.hass.config_entries.async_update_entry(
                entry=self.config_entry,
                options=user_input
            )

            if changed:
                await self.hass.config_entries.async_reload(self.config_entry.entry_id)

            return self.async_create_entry(title="", data=user_input)
        
        """Show the options form"""
        return self.async_show_form(step_id="init", 
            data_schema=vol.Schema({
                    vol.Optional(CONF_EVENT_COMPLETE, default=self.config_entry.options.get(CONF_EVENT_COMPLETE, DEFAULT_EVENT_COMPLETE)): bool,
                    vol.Optional(CONF_EVENT_ADDED, default=self.config_entry.options.get(CONF_EVENT_ADDED, DEFAULT_EVENT_ADDED)): bool,
                    vol.Optional(CONF_EVENT_REMOVED, default=self.config_entry.options.get(CONF_EVENT_REMOVED, DEFAULT_EVENT_REMOVED)): bool,
                    vol.Required(CONF_EVENT_SCAN_INTERVAL, default=self.config_entry.options.get(CONF_EVENT_SCAN_INTERVAL, DEFAULT_EVENT_SCAN_INTERVAL)): int
                }),
                errors=errors)
        
