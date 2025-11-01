"""Config flow for qBittorrent."""
from __future__ import annotations

import logging
from typing import Any

import qbittorrentapi
from qbittorrentapi import Client, APIConnectionError, LoginFailed, HTTPError, Forbidden403Error, InternalServerError500Error

from requests.exceptions import RequestException, ConnectTimeout
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlow, SOURCE_RECONFIGURE, SOURCE_REAUTH
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

_LOGGER = logging.getLogger(__name__)


class QbittorrentConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for the qBittorrent integration."""

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle a user-initiated config flow."""
        errors = {}

        if user_input is not None:
            # Update the previous entry data with whatever the user has just entered
            self._user_input.update(user_input)
            if not errors:
                if self.source not in (SOURCE_RECONFIGURE, SOURCE_REAUTH):
                    await self.async_set_unique_id(DOMAIN + "_" + urlparse(self._user_input[CONF_URL]).hostname.replace('.', '_'))
                    self._abort_if_unique_id_configured(
                        description_placeholders = {"ipaddress": urlparse(self._user_input[CONF_URL]).hostname}
                        )

                # Check the (new) credentials
                try:
                    client = None
                    client = await self.hass.async_add_executor_job(
                        setup_client,
                        self._user_input[CONF_URL],
                        self._user_input[CONF_USERNAME],
                        self._user_input[CONF_PASSWORD],
                        self._user_input[CONF_VERIFY_SSL],
                    )

                    if self.source not in (SOURCE_RECONFIGURE, SOURCE_REAUTH):
                        # Create a new entry
                        return self.async_create_entry (
                            title=DEFAULT_NAME + ' - ' + urlparse(self._user_input[CONF_URL]).hostname,
                            data=self._user_input
                            )
                    else:
                        # Just update and reload the existing entry
                        if self.source == SOURCE_RECONFIGURE:
                            config_entry = self._get_reconfigure_entry()
                            reason = "reconfigure_successful"
                        else:
                            config_entry = self._get_reauth_entry()
                            reason = "reauth_successful"
    
                        return self.async_update_reload_and_abort(
                            config_entry,
                            data = self._user_input,
                            reason = reason,
                            reload_even_if_entry_is_unchanged=False
                        )

                except LoginFailed as ex:
                    errors = {"base": "invalid_auth"}

                except Forbidden403Error as ex:
                    errors = {"base": "blocked_connection"}

                except APIConnectionError as ex:
                    errors = {"base": "api_error"}
    
                except ConnectTimeout as ex:
                    errors = {"base": "connection_timeout"}

                except RequestException as ex:
                    errors = {"base": "request_exception"}

                except Exception as ex:
                    errors = {"base": "unknown"}

        # We'll only get here if there's an error with the filled-in form, or it's the first time showing the form
        # Each scenario has a slightly different schema requirement, unfortunately
        if self.source == SOURCE_REAUTH:
            config_entry = self._get_reauth_entry()
            self._user_input = dict(config_entry.data)
            action = "Update"

            USER_DATA_SCHEMA = vol.Schema(
                {
                    vol.Required(CONF_USERNAME, default = self._user_input.get(CONF_USERNAME, "")): str,
                    vol.Required(CONF_PASSWORD, default = ""): str,
                }
            )
            
        elif self.source == SOURCE_RECONFIGURE:
            config_entry = self._get_reconfigure_entry()
            self._user_input = dict(config_entry.data)
            action = "Update"

            USER_DATA_SCHEMA = vol.Schema(
                {
                    vol.Required(CONF_USERNAME, default = self._user_input.get(CONF_USERNAME, "")): str,
                    vol.Required(CONF_PASSWORD, default = self._user_input.get(CONF_PASSWORD, "")): str,
                    vol.Required(CONF_SCAN_INTERVAL, default = self._user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SENSOR_SCAN_INTERVAL)): int,
                }
            )

        else:
            if user_input is None:
                self._user_input = {}

            action = "Enter"

            USER_DATA_SCHEMA = vol.Schema(
                {
                    vol.Required(CONF_URL, default = self._user_input.get(CONF_URL, DEFAULT_URL)): str,
                    vol.Required(CONF_USERNAME, default = self._user_input.get(CONF_USERNAME, "")): str,
                    vol.Required(CONF_PASSWORD, default = self._user_input.get(CONF_PASSWORD, "")): str,
                    vol.Required(CONF_VERIFY_SSL, default = self._user_input.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL)): bool,
                    vol.Required(CONF_SCAN_INTERVAL, default = self._user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SENSOR_SCAN_INTERVAL)): int,
                }
            )

        return self.async_show_form(
            step_id = "user",
            data_schema = USER_DATA_SCHEMA,
            errors = errors,
            description_placeholders = {"action": action}
            )

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None):
        """User wants to update the username, password or sensor update interval"""
        return await self.async_step_user()

    async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> ConfigFlowResult:
        """Require that the user re-enter the username and password"""
        
        return await self.async_step_user()


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
        
