from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import timedelta

from homeassistant.components.image import (
    ImageEntityDescription,
    ImageEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)
from . import KtwItsDataUpdateCoordinator
from .const import (
    DOMAIN,
    DEFAULT_NAME
)

SCAN_INTERVAL = timedelta(seconds=10)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = await __get_image_entities(hass, coordinator)
    async_add_entities(entities, False)


async def __get_image_entities(hass, coordinator) -> Iterable[KtwItsImageEntity]:
    descriptions = [
        KtwItsImageEntity(
            hass,
            coordinator,
            KtwItsImageEntityDescription(
                key="372",
                camera_id=372,
                image_id=0
            )
        ),
    ]

    return descriptions


class KtwItsImageEntity(ImageEntity):
    def __init__(
            self,
            hass: HomeAssistant,
            coordinator: KtwItsDataUpdateCoordinator,
            description: KtwItsImageEntityDescription
    ) -> None:
        ImageEntity.__init__(self, hass)
        _device_id = "ktw-its"

        self.entity_description = description
        self._attr_unique_id = f"{_device_id}-{description.key.lower()}"
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, _device_id)},
            manufacturer=DEFAULT_NAME,
            name=DEFAULT_NAME,
        )
        self.coordinator = coordinator

        print(description)

        self.camera_id: int = description.camera_id
        self.image_id: int = description.image_id

    # @callback
    # def _handle_coordinator_update(self) -> None:
    #     """Handle updated coordinator."""
    #     ##self._attr_image_url = 'https://its.katowice.eu/api/camera/image/372/image24-04-10_18-49-57-01_00013.jpg'
    #     self._attr_image_last_updated = datetime.now()
    #     super()._handle_coordinator_update()

    async def async_image(self) -> bytes | None:
        print('async_image')
        return await self.coordinator.get_camera_image(self.camera_id, self.image_id)


@dataclass(frozen=True, kw_only=True)
class KtwItsImageEntityDescription(ImageEntityDescription):
    """A class that describes image entities."""
    camera_id: int
    image_id: int
