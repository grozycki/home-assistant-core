import aiohttp
import asyncio
import ssl
import certifi

from .const import WEATHER_DATA
from datetime import datetime, timedelta
import logging
from .coordinator import KtwItsCameraImageDto, KtwItsSensorDto
from collections.abc import Iterable

from .sensor import KtwItsSensorEntityDescription
from ..sensor import SensorDeviceClass
import pytz

from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    CONCENTRATION_PARTS_PER_MILLION,
    CONF_NAME,
    PERCENTAGE,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfSpeed,
)


_LOGGER = logging.getLogger(__name__)


#async def main():
#   api = KtwItsApi()

# cameras = await get_cameras()
# print(cameras)
# camera_353 = await get_camera_images_by_id(353)
# print(camera_353)
# weather = await get_weather()
# print(weather)


async def make_request(url: str):
    _LOGGER.warning(f"making request to {url}")
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    conn = aiohttp.TCPConnector(ssl=ssl_context)
    async with aiohttp.ClientSession(connector=conn) as session:
        async with session.get(url) as resp:
            return await resp.json()


async def make_request_read(url: str):
    print(url)
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    conn = aiohttp.TCPConnector(ssl=ssl_context)
    async with aiohttp.ClientSession(connector=conn) as session:
        async with session.get(url) as resp:
            return await resp.read()


##asyncio.run(main())


class KtwItsApi:
    def __init__(self):
        self.weather_data_valid_to: datetime | None = None
        self.weather_data: dict = {}

    def fetch_data(self, groups: set):

        return self.__get_weather()


    async def get_camera_images_by_id(self, camera_id: int):
        return await make_request('https://its.katowice.eu/api/cameras/' + str(camera_id) + '/images')

    async def get_camera_image(self, camera_id: int, image_id: int) -> bytes | None:
        print('get_camera_image in api')

        images = await make_request('https://its.katowice.eu/api/cameras/' + str(camera_id) + '/images')
        filename = images['images'][image_id]['filename']

        return await make_request_read('https://its.katowice.eu/api/camera/image/' + str(camera_id) + '/' + filename)

    async def get_camera_image_data(self, camera_id: int, image_id: int) -> KtwItsCameraImageDto:
        images = await make_request('https://its.katowice.eu/api/cameras/' + str(camera_id) + '/images')
        print(images)
        filename = images['images'][image_id]['filename']
        print(filename)

        last_updated = datetime.fromisoformat(images['images'][image_id]['addTime'])
        print(last_updated)

        return KtwItsCameraImageDto(last_updated=last_updated, filename=filename)

    async def get_cameras(self):
        return await make_request('https://its.katowice.eu/api/cameras')

    async def __get_weather(self) -> Iterable[KtwItsSensorDto]:
        if self.weather_data_valid_to is not None and self.weather_data_valid_to <= pytz.UTC.localize(datetime.now()):
            return self.weather_data

        weather = await make_request('https://its.katowice.eu/api/v1/weather/air')
        self.weather_data_valid_to = datetime.fromisoformat(weather['date']) + timedelta(minutes=15)

        self.weather_data.update(
            [
                (
                    SensorDeviceClass.TEMPERATURE,
                    KtwItsSensorDto(
                        value=float(weather['temperature']),
                        entity_description=KtwItsSensorEntityDescription(
                            group='weather',
                            key=SensorDeviceClass.TEMPERATURE,
                            device_class=SensorDeviceClass.TEMPERATURE,
                            native_unit_of_measurement=UnitOfTemperature.CELSIUS
                        ),
                    )
                ),
                (
                    SensorDeviceClass.PRESSURE,
                    KtwItsSensorDto(
                        value=int(weather['pressure']),
                        entity_description=
                        KtwItsSensorEntityDescription(
                            group='weather',
                            key=SensorDeviceClass.PRESSURE,
                            device_class=SensorDeviceClass.PRESSURE,
                            native_unit_of_measurement=UnitOfPressure.HPA
                        ),
                    )
                ),
                (
                    SensorDeviceClass.HUMIDITY,
                    KtwItsSensorDto(
                        value=int(weather['humidity']),
                        entity_description=
                        KtwItsSensorEntityDescription(
                            group='weather',
                            key=SensorDeviceClass.HUMIDITY,
                            device_class=SensorDeviceClass.HUMIDITY,
                            native_unit_of_measurement=PERCENTAGE
                        ),
                    )
                ),
                (
                    SensorDeviceClass.WIND_SPEED,
                    KtwItsSensorDto(
                        value=float(weather['windSpeed']),
                        entity_description=
                        KtwItsSensorEntityDescription(
                            group='weather',
                            key=SensorDeviceClass.WIND_SPEED,
                            device_class=SensorDeviceClass.WIND_SPEED,
                            native_unit_of_measurement=UnitOfSpeed.METERS_PER_SECOND
                        ),
                    )
                ),
                (
                    SensorDeviceClass.AQI,
                    KtwItsSensorDto(
                        value=int(weather['aqi']),
                        entity_description=
                        KtwItsSensorEntityDescription(
                            group='weather',
                            key=SensorDeviceClass.AQI,
                            device_class=SensorDeviceClass.AQI,
                            native_unit_of_measurement=None
                        ),
                    )
                ),
                (
                    SensorDeviceClass.CO,
                    KtwItsSensorDto(
                        value=float(weather['co']),
                        entity_description=
                        KtwItsSensorEntityDescription(
                            group='weather',
                            key=SensorDeviceClass.CO,
                            device_class=SensorDeviceClass.CO,
                            native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION
                        ),
                    )
                ),
                (
                    SensorDeviceClass.NITROGEN_MONOXIDE,
                    KtwItsSensorDto(
                        value=float(weather['no']),
                        entity_description=
                        KtwItsSensorEntityDescription(
                            group='weather',
                            key=SensorDeviceClass.NITROGEN_MONOXIDE,
                            device_class=SensorDeviceClass.NITROGEN_MONOXIDE,
                            native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER

                        ),
                    )
                ),
                (
                    SensorDeviceClass.NITROGEN_DIOXIDE,
                    KtwItsSensorDto(
                        value=float(weather['no2']),
                        entity_description=
                        KtwItsSensorEntityDescription(
                            group='weather',
                            key=SensorDeviceClass.NITROGEN_DIOXIDE,
                            device_class=SensorDeviceClass.NITROGEN_DIOXIDE,
                            native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
                        ),
                    )
                ),
                (
                    SensorDeviceClass.OZONE,
                    KtwItsSensorDto(
                        value=float(weather['o3']),
                        entity_description=
                        KtwItsSensorEntityDescription(
                            group='weather',
                            key=SensorDeviceClass.OZONE,
                            device_class=SensorDeviceClass.OZONE,
                            native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
                        ),
                    )
                ),
                (
                    SensorDeviceClass.SULPHUR_DIOXIDE,
                    KtwItsSensorDto(
                        value=float(weather['so2']),
                        entity_description=
                        KtwItsSensorEntityDescription(
                            group='weather',
                            key=SensorDeviceClass.SULPHUR_DIOXIDE,
                            device_class=SensorDeviceClass.SULPHUR_DIOXIDE,
                            native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
                        ),
                    )
                ),
                (
                    SensorDeviceClass.PM25,
                    KtwItsSensorDto(
                        value=float(weather['pm2_5']),
                        entity_description=
                        KtwItsSensorEntityDescription(
                            group='weather',
                            key=SensorDeviceClass.PM25,
                            device_class=SensorDeviceClass.PM25,
                            native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
                        ),
                    )
                ),
                (
                    SensorDeviceClass.PM10,
                    KtwItsSensorDto(
                        value=float(weather['pm10']),
                        entity_description=
                        KtwItsSensorEntityDescription(
                            group='weather',
                            key=SensorDeviceClass.PM10,
                            device_class=SensorDeviceClass.PM10,
                            native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
                        ),
                    )
                ),
                (
                    'sunrise',
                    KtwItsSensorDto(
                        value=datetime.fromisoformat(weather['sunrise']),
                        entity_description=
                        KtwItsSensorEntityDescription(
                            group='weather',
                            key='sunrise',
                            device_class=SensorDeviceClass.TIMESTAMP,
                            native_unit_of_measurement=None
                        ),
                    )
                ),
                (
                    'sunset',
                    KtwItsSensorDto(
                        value=datetime.fromisoformat(weather['sunset']),
                        entity_description=
                        KtwItsSensorEntityDescription(
                            group='weather',
                            key='sunset',
                            device_class=SensorDeviceClass.TIMESTAMP,
                            native_unit_of_measurement=None
                        ),
                    )
                ),
            ]
        )

        return self.weather_data

