from dataclasses import dataclass
from datetime import timedelta
import logging
from datetime import datetime
from functools import cached_property

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

@dataclass(frozen=True)
class KtwItsCameraImageDto:
    filename: str
    last_updated: datetime

class KtwItsDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, my_api):
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="My sensor",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=60),
        )
        self.my_api = my_api

    async def _async_update_data(self):
        data: dict[str, str | float | int | datetime] = {}

        weather = await self.my_api.get_weather()

        data[SensorDeviceClass.TEMPERATURE] = float(weather['temperature'])
        data[SensorDeviceClass.PRESSURE] = int(weather['pressure'])
        data[SensorDeviceClass.HUMIDITY] = int(weather['humidity'])

        data[SensorDeviceClass.WIND_SPEED] = float(weather['windSpeed'])
        data[SensorDeviceClass.AQI] = int(weather['aqi'])
        data[SensorDeviceClass.CO] = float(weather['co'])
        data[SensorDeviceClass.NITROGEN_MONOXIDE] = float(weather['no'])
        data[SensorDeviceClass.NITROGEN_DIOXIDE] = float(weather['no2'])
        data[SensorDeviceClass.OZONE] = float(weather['o3'])
        data[SensorDeviceClass.SULPHUR_DIOXIDE] = float(weather['so2'])
        data[SensorDeviceClass.PM25] = float(weather['pm2_5'])
        data[SensorDeviceClass.PM10] = float(weather['pm10'])

        data['sunrise'] = datetime.fromisoformat(weather['sunrise'])
        data['sunset'] = datetime.fromisoformat(weather['sunset'])

        return data

    async def get_cameras(self):
        return await self.my_api.get_cameras()

    async def get_camera_image(self, camera_id: int, image_id: int) -> bytes | None:
        print('get_camera_image in coordinator')
        return await self.my_api.get_camera_image(camera_id, image_id)

    async def get_camera_image_data(self, camera_id: int, image_id: int) -> KtwItsCameraImageDto:
        print('get_camera_image_data in coordinator')
        return await self.my_api.get_camera_image_data(camera_id, image_id)




