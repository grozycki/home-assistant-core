import aiohttp
import asyncio
import ssl
import certifi

from .const import WEATHER_DATA


#async def main():
 #   api = KtwItsApi()

    # cameras = await get_cameras()
    # print(cameras)
    # camera_353 = await get_camera_images_by_id(353)
    # print(camera_353)
    # weather = await get_weather()
    # print(weather)


async def make_request(url):
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    conn = aiohttp.TCPConnector(ssl=ssl_context)
    async with aiohttp.ClientSession(connector=conn) as session:
        async with session.get(url) as resp:
            return await resp.json()


##asyncio.run(main())


class KtwItsApi:
    def fetch_data(self):
        return {
            WEATHER_DATA: 'fff',
        }
    async def get_camera_images_by_id(self, camera_id: int):
        return await make_request('https://its.katowice.eu/api/cameras/' + str(camera_id) + '/images')

    async def get_cameras(self):
        return await make_request('https://its.katowice.eu/api/cameras')

    async def get_weather(self):
        return await make_request('https://its.katowice.eu/api/v1/weather/air')
