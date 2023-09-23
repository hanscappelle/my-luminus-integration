"""Custom integration for Home Assistant.

For more details about this integration, please refer to
https://github.com/hanscappelle/my-luminus-integration
"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MyLuminusApiClient
from .const import DOMAIN, LOGGER
from .coordinator import MyLuminusCoordinator

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
]

ATTR_PAYLOAD = "payload"


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """
    This class is called by the HomeAssistant framework when a configuration entry is 
    provided. For us, the configuration entry is the username-password credentials that 
    the user needs to access API.
    """

    # Retrieve the stored credentials from config-flow
    username = entry.data.get(CONF_USERNAME)
    LOGGER.debug("Loaded %s: %s", CONF_USERNAME, username)
    password = entry.data.get(CONF_PASSWORD)
    LOGGER.debug("Loadded %s: ********", CONF_PASSWORD)

    # Initialize the HASS structure
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator = MyLuminusCoordinator(
        hass=hass,
        client=MyLuminusApiClient(
            username=username,
            password=password,
            session=async_get_clientsession(hass),
        ),
    )

    # add a service from this integration to push meter values
    hass.services.register(DOMAIN, "publish_meter_values", handle_new_meter_values)

    # Initiate the coordinator. This method will also make sure to login to the API

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def handle_new_meter_values(call: any) -> bool:
    payload = call.data.get(ATTR_PAYLOAD, {})
    hass.client


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    if unloaded := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
