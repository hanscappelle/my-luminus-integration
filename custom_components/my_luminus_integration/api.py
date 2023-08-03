"""for API calls"""
from __future__ import annotations

import asyncio
import socket

import aiohttp
import async_timeout

from .const import LOGGER


class MyLuminusApiClientError(Exception):
    """Exception to indicate a general API error."""


class MyLuminusApiClientCommunicationError(MyLuminusApiClientError):
    """Exception to indicate a communication error."""


class MyLuminusApiClientAuthenticationError(MyLuminusApiClientError):
    """Exception to indicate an authentication error."""


class MyLuminusApiClient:
    """Starcom API"""

    def __init__(
        self,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
    ) -> None:
        self._username = username
        self._password = password
        self._session = session

    async def token(self) -> any:
        """
        get new token, required for all the other requests

        POST https://mobileapi.luminus.be/token

        grant_type=password&username=UW_EMAIL&password=UW_WACHTWOORD

        {
            "access_token": "****",
            "token_type": "bearer",
            "expires_in": 1199,
            "refresh_token": "****"
        }

        there is also a refresh option where you put grant_type=refresh_token and refresh_token=current_token
        """
        return await self._api_wrapper(
            method="POST",
            url="https://mobileapi.luminus.be/token",
            # this call doesn't take json but url encoded form data
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data="grant_type=password&username="
            + self._username
            + "&password="
            + self._password,
        )

    async def contracts(self, token) -> any:
        """
        get an overview of contracts for this client.

        GET https://mobileapi.luminus.be/api/v11/GetContracts

        {
            "Contracts": [{
                "Ean":"****",
                "EnergyType":"Electricity",
                "Product":"Comfy Plugin Pro",
                "PriceVariability":"Fixed",
                "EndDate":"2100-12-31",
            }]
            "PendingContracts":[]
            ...
        }
        """
        return await self._api_wrapper(
            method="GET",
            headers={"Authorization": "Bearer " + token},
            url="https://mobileapi.luminus.be/api/v11/GetContracts",
        )

    async def meters(self, token) -> any:
        """
        gets a list of available meters

        GET https://mobileapi.luminus.be/api/v11/GetMetersConsumptionSources

        "Meters": [{
            "Ean": "****",
            "EnergyType": "Electricity",
            "Sources": [{
                "SourceProvider": "LuminusSap"
            }]
        }]
        """
        return await self._api_wrapper(
            method="GET",
            headers={"Authorization": "Bearer " + token},
            url="https://mobileapi.luminus.be/api/v11/GetMetersConsumptionSources",
        )

    async def budget(self, token) -> any:
        """
        GET https://mobileapi.luminus.be/api/v11/GetBudgetBillLines

        {
            "Lines": [
                {
                "Ean": "****",
                "NextInvoiceDate": "2023-08-14",
                "Frequency": "Monthly",
                "CurrentAmount": ***,
                "Simulation": {
                    "FromDate": "2023-05-01",
                    "ToDate": "2024-05-31",
                    "IdealAmount": ***,
                    "MinimumAmount": ***,
                    "MaximumAmount": ***,
                    "PaidAmount": ***,
                    "EstimatedOpenAmount": ***.**,
                    "EstimatedTotalAmount": ***.**,
                    "CurrentFinalInvoiceAmount": ***,
                    "OpenInvoicesCount": ***,
                    "PaidInvoicesCount": ***
                },
                "IsEmptyHouse": false,
                "UpdateAmountAllowed": true,
                "UpdateFrequencyAllowed": true,
                "UpdateEmptyHouseAllowed": true,
                "IdealAmount": ***,
                "MinimumAmount": ***,
                "MaximumAmount": ****,
                "CurrentSettlementAmount": ****,
                "SubTotal": ***.**,
                "OpenSlices": **
                }
            ]
            }
        """
        return await self._api_wrapper(
            method="GET",
            headers={"Authorization": "Bearer " + token},
            url="https://mobileapi.luminus.be/api/v11/GetBudgetBillLines",
        )

    async def accountStatements(self, token, language: str = "nl") -> any:
        """
        GET https://mobileapi.luminus.be/api/v11/GetAccountStatement

        {
            "AmountOpen": {
                "Value": 0,
                "CurrencyCode": "EUR"
            },
            "AmountOpenOnlinePaymentAllowed": false,
            "InvoiceDownloadIsInMaintenance": false,
            "Invoices": []
            "Payments": []
        }
        """
        return await self._api_wrapper(
            method="GET",
            headers={"Authorization": "Bearer " + token, "Accept-Language": language},
            url="https://mobileapi.luminus.be/api/v11/GetAccountStatement",
        )

    # TODO create service(?) to push inserting meter readings (from P1, manual...)
    # POST https://mobileapi.luminus.be/api/v11/InsertMeterReading

    # one allowed per day, delete again with
    # POST https://mobileapi.luminus.be/api/v11/DeleteMeterReading
    # {
    #    "Ean": "****",
    #    "Date": "2023-07-20"
    # }

    # other discovered API urls not yet consumed

    # https://mobileapi.luminus.be/api/v11/GetApplicationStatus
    # https://mobileapi.luminus.be/api/v11/GetBusinessPartner
    # https://mobileapi.luminus.be/api/v11/GetMeters
    # https://mobileapi.luminus.be/api/v11/GetPaymentOptions
    # https://mobileapi.luminus.be/api/v11/GetAlerts
    # https://mobileapi.luminus.be/api/v11/GetMetricsRange?ean=****&source=LuminusSap
    # https://mobileapi.luminus.be/api/v11/GetDynamicContent
    # https://mobileapi.luminus.be/api/v11/GetConsumptions?ean=****&source=LuminusSap&energyType=Electricity&dateFrom=2023-07-01T00:00:00&dateUntil=2023-12-31T23:59:59&periodicity=Month
    # https://mobileapi.luminus.be/api/v11/GetServicesOverview
    # https://mobileapi.luminus.be/api/v11/GetDynamicMenu
    # https://mobileapi.luminus.be/api/v11/GetUrlList

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        headers: dict | None = None,
        data: dict | None = None,
        json: dict | None = None,
    ) -> any:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    data=data,
                    json=json,
                )
                if response.status in (401, 403, 601):
                    raise MyLuminusApiClientAuthenticationError(
                        "Invalid credentials",
                    )
                response.raise_for_status()
                return await response.json()

        except asyncio.TimeoutError as exception:
            raise MyLuminusApiClientCommunicationError(
                "Timeout error fetching information",
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            LOGGER.debug("received error is %s", exception)
            raise MyLuminusApiClientCommunicationError(
                "Error fetching information",
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            raise MyLuminusApiClientError(
                "Something really wrong happened!"
            ) from exception
