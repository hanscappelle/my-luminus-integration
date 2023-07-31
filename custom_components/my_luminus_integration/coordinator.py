"""DataUpdateCoordinator for Integration."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.exceptions import ConfigEntryAuthFailed

from .api import (
    MyLuminusApiClient,
    MyLuminusApiClientAuthenticationError,
    MyLuminusApiClientError,
)
from .const import DOMAIN, LOGGER


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class MyLuminusCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: ConfigEntry

    token = None  # auth token
    lines = []  # fetched budget lines

    def __init__(
        self,
        hass: HomeAssistant,
        client: MyLuminusApiClient,
    ) -> None:
        """Initialize."""
        self.client = client
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=5),
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            # attempt to retrieve unit number
            # return await self.client.async_get_last_transmit()

            # start by getting a new token for all the next calls
            response = await self.client.token()
            LOGGER.debug("received data from token %s", response)

            self.token = response["access_token"]

            # also get last transmit at this point
            LOGGER.debug("received access token from API %s", self.token)

            # now get some initial data to populate some sensors
            # we"ll start by implementing budget lines
            data = await self.client.budget(token=self.token)
            self.lines = data["Lines"]

            return data

        except MyLuminusApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except MyLuminusApiClientError as exception:
            raise UpdateFailed(exception) from exception
