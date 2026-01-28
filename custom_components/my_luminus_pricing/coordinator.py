"""DataUpdateCoordinator for our integration."""

from datetime import timedelta
from typing import Any
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import API, APIConnectionError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, USE_MOCK_DATA
import logging

_LOGGER = logging.getLogger(__name__)

class LuminusCoordinator(DataUpdateCoordinator):
    """Coordinator for Luminus pricing data."""

    data: list[dict[str, Any]] | None

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize coordinator."""

        # Set variables from values entered in config flow setup
        self.user = config_entry.data[CONF_USERNAME]
        self.pwd = config_entry.data[CONF_PASSWORD]

        # set variables from options.  You need a default here in case options have not been set
        self.poll_interval = config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )

        # Initialise DataUpdateCoordinator
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} ({config_entry.unique_id})",
            # Method to call on every update interval.
            update_method=self.async_update_data,
            # Polling interval. Will only be polled if you have made your
            # platform entities, CoordinatorEntities.
            # Using config option here but you can just use a fixed value.
            update_interval=timedelta(seconds=self.poll_interval),
        )

        # Initialise your api here and make available to your integration.
        self.api = API(user=self.user, pwd=self.pwd, mock=USE_MOCK_DATA)

    async def async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to retrieve and pre-process the data into an appropriate data structure
        to be used to provide values for all your entities.
        """
        try:
            # ----------------------------------------------------------------------------
            # Get the data from your api
            # NOTE: Change this to use a real api call for data
            # ----------------------------------------------------------------------------
            
            await self.hass.async_add_executor_job(self.api.login)
            meters = await self.hass.async_add_executor_job(self.api.get_meters)
            data = []
            for meter in meters['meters']:
                eanNr = meter['ean']
                energyType = meter['energyType']
                meterDetails = await self.hass.async_add_executor_job(self.api.get_meter, eanNr)
                if not meterDetails is None:
                    pname = meterDetails['productName']
                    prices = meterDetails['prices']
                    meterType = meterDetails['activeMeterType']
                    meterPrices = prices[meterType]
                    device = {
                        'device_id': eanNr,
                        'device_name': pname + ' (' + eanNr + ')',
                        'device_type': energyType,
                        'product_name': pname
                    }
                    data.append(device)
                    for prop_name, price in meterPrices.items():
                        device[prop_name] = price["rate"] / (
                            1 if prop_name == "fixed" else 100
                        )

            _LOGGER.debug("Data updated")
        except APIConnectionError as err:
            _LOGGER.error(err)
            raise UpdateFailed(err) from err
        except Exception as err:
            # This will show entities as unavailable by raising UpdateFailed exception
            raise UpdateFailed(f"Error communicating with API: {err}") from err

        # What is returned here is stored in self.data by the DataUpdateCoordinator
        return data

    # ----------------------------------------------------------------------------
    # Here we add some custom functions on our data coordinator to be called
    # from entity platforms to get access to the specific data they want.
    #
    # These will be specific to your api or yo may not need them at all
    # ----------------------------------------------------------------------------
    def get_device(self, device_id: str) -> dict[str, Any] | None:
        """Get a device entity from our api data."""
        if self.data is None:
            return None
        try:
            return next(
                (d for d in self.data if d["device_id"] == device_id),
                None,
            )
        except (TypeError, KeyError):
            return None

    def get_device_parameter(self, device_id: str, parameter: str) -> Any:
        """Get the parameter value of one of our devices from our api data."""
        if device := self.get_device(device_id):
            return device.get(parameter)
