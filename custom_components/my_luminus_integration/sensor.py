"""Sensor platform for integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
)

from .const import DOMAIN, LOGGER
from .coordinator import MyLuminusCoordinator
from .entity import MyLuminusEntity

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="my_luminus",
        name="soc",
        icon="mdi:battery-charging-50",
        device_class=SensorDeviceClass.BATTERY,
    ),
    SensorEntityDescription(
        key="my_luminus",
        name="name",
        icon="mdi:id-card",
    ),
    SensorEntityDescription(
        key="my_luminus",
        name="mileage",
        icon="mdi:gauge",
        device_class=SensorDeviceClass.DISTANCE,
    ),
)


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # create sensors for all units found, not just the first one
    for unit in coordinator.units:
        async_add_devices(
            MyLuminusSensor(
                coordinator=coordinator,
                entity_description=entity_description,
                unitnumber=unit["unitnumber"],
            )
            for entity_description in ENTITY_DESCRIPTIONS
        )


class MyLuminusSensor(MyLuminusEntity, SensorEntity):
    """Sensor class."""

    unitnumber: str  # each motorcycle gets this unique unit number assigned

    def __init__(
        self,
        coordinator: MyLuminusCoordinator,
        entity_description: SensorEntityDescription,
        unitnumber: str,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.unitnumber = unitnumber
        # had to create unique IDs per sensor here, using key.name
        # unitnumber = self.coordinator.units[0]["unitnumber"] # this was limited to the first unit
        self._attr_unique_id = (
            entity_description.key + "." + unitnumber + "." + entity_description.name
        )
        # make names unique per unit
        entity_description.name = (
            entity_description.name.split(".")[0] + "." + unitnumber
        )
        # entity_description.key = "unit." + unitnumber + "." + entity_description.name
        self.entity_description = entity_description

    @property
    def native_value(self) -> str:
        """Return the native value of the sensor."""
        sensor = self.entity_description.name
        # unitnumber = self.coordinator.units[0]["unitnumber"] # this was limited to the first unit
        # value = self.coordinator.data[self.unitnumber][0][sensor]
        value = self.coordinator.data[self.unitnumber][0][sensor.split(".")[0]]
        LOGGER.debug(
            "Sensor value for %s is %s",
            self.unique_id,
            value,
        )
        return value
