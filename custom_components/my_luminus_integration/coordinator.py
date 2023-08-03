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

            """
            # test data
            data = {
                "Lines": [
                    {
                        "Ean": "109823898932",
                        "NextInvoiceDate": "2023-08-14",
                        "Frequency": "Monthly",
                        "CurrentAmount": 116.0,
                        "IdealAmount": 192.0,
                        "MinimumAmount": 117.0,
                        "MaximumAmount": 1876.0,
                        "CurrentSettlementAmount": 1755.0,
                        "SubTotal": 1915.19,
                        "OpenSlices": 10,
                    },
                    {
                        "Ean": "2390823890",
                        "NextInvoiceDate": "2023-08-14",
                        "Frequency": "Monthly",
                        "CurrentAmount": 216.0,
                        "IdealAmount": 292.0,
                        "MinimumAmount": 217.0,
                        "MaximumAmount": 2876.0,
                        "CurrentSettlementAmount": 2755.0,
                        "SubTotal": 2915.19,
                        "OpenSlices": 10,
                    },
                ]
            }
            """

            self.lines = data["Lines"]

            # also get open amount
            self.statements = await self.client.accountStatements(token=self.token)

            return data

        except MyLuminusApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except MyLuminusApiClientError as exception:
            raise UpdateFailed(exception) from exception
