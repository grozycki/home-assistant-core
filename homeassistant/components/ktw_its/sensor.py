from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)

from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.core import callback
from .const import (
    DOMAIN,
    DEFAULT_NAME
)
from datetime import timedelta

from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    CONF_NAME,
    PERCENTAGE,
    UnitOfPressure,
    UnitOfTemperature,
)

SCAN_INTERVAL = timedelta(seconds=10)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [KtwItsSensorEntity(coordinator, description) for description in SENSORS]
    async_add_entities(entities, False)


class KtwItsSensorEntity(CoordinatorEntity, SensorEntity):
    def __init__(
            self,
            coordinator: CoordinatorEntity,
            description: KtwItsSensorEntityDescription
    ) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, context=description.key)

        _device_id = "ktw-its"

        self.entity_description = description
        self._attr_unique_id = f"{_device_id}-{description.key.lower()}"
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, _device_id)},
            manufacturer=DEFAULT_NAME,
            name=DEFAULT_NAME,
        )

    # def update(self) -> None:
    #     self._attr_native_value = 23

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_native_value = self.coordinator.data[self.entity_description.key]
        self.async_write_ha_state()


@dataclass(frozen=True, kw_only=True)
class KtwItsSensorEntityDescription(SensorEntityDescription):
    state_class = SensorStateClass.MEASUREMENT


SENSORS: tuple[KtwItsSensorEntityDescription, ...] = (
    KtwItsSensorEntityDescription(
        key=SensorDeviceClass.TEMPERATURE,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS
    ),
    KtwItsSensorEntityDescription(
        key=SensorDeviceClass.HUMIDITY,
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE
    ),
    KtwItsSensorEntityDescription(
        key=SensorDeviceClass.PM10,
        device_class=SensorDeviceClass.PM10,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
    ),
    KtwItsSensorEntityDescription(
        key=SensorDeviceClass.PM25,
        device_class=SensorDeviceClass.PM25,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
    ),
)
