from datetime import timedelta
import logging

import async_timeout

from homeassistant.components.light import LightEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import callback
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)

from .const import (
    DOMAIN,
    TEMPERATURE_DATA,
    HUMIDITY_DATA
)
from .sensor import KtwItsSensorEntity

_LOGGER = logging.getLogger(__name__)


class KtwItsDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, my_api):
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="My sensor",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=30),
        )
        self.my_api = my_api

    async def _async_update_data(self):
        data: dict[str, str | float | int] = {}

        weather = await self.my_api.get_weather()

        data[SensorDeviceClass.TEMPERATURE] = float(weather['temperature'])
        data[SensorDeviceClass.HUMIDITY] = int(weather['humidity'])
        data[SensorDeviceClass.PM10] = float(weather['pm10'])
        data[SensorDeviceClass.PM25] = float(weather['pm2_5'])

        return data
