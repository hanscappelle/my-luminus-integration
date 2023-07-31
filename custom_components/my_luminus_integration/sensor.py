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
        name="NextInvoiceDate",
        icon="mdi:receipt-text",
        device_class=SensorDeviceClass.DATE,
    ),
    SensorEntityDescription(
        key="my_luminus",
        name="CurrentAmount",
        icon="mdi:cash-100",
        device_class=SensorDeviceClass.MONETARY,
    ),
    SensorEntityDescription(
        key="my_luminus",
        name="IdealAmount",
        icon="mdi:cash-100",
        device_class=SensorDeviceClass.MONETARY,
    ),
    SensorEntityDescription(
        key="my_luminus",
        name="MinimumAmount",
        icon="mdi:cash-100",
        device_class=SensorDeviceClass.MONETARY,
    ),
    SensorEntityDescription(
        key="my_luminus",
        name="MaximumAmount",
        icon="mdi:cash-100",
        device_class=SensorDeviceClass.MONETARY,
    ),
    SensorEntityDescription(
        key="my_luminus",
        name="CurrentSettlementAmount",
        icon="mdi:cash-100",
        device_class=SensorDeviceClass.MONETARY,
    ),
    SensorEntityDescription(
        key="my_luminus",
        name="SubTotal",
        icon="mdi:cash-100",
        device_class=SensorDeviceClass.MONETARY,
    ),
    SensorEntityDescription(
        key="my_luminus",
        name="OpenSlices",
        icon="mdi:circle-slice-6",
    ),
)


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # create sensors for all units found, not just the first one
    for line in coordinator.lines:
        async_add_devices(
            MyLuminusSensor(
                coordinator=coordinator,
                entity_description=entity_description,
                line=line,
            )
            for entity_description in ENTITY_DESCRIPTIONS
        )


class MyLuminusSensor(MyLuminusEntity, SensorEntity):
    """Sensor class."""

    ean: str  # each contract get its own ean
    line: dict  # data for this ean

    def __init__(
        self,
        coordinator: MyLuminusCoordinator,
        entity_description: SensorEntityDescription,
        line: dict,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.ean = line["Ean"]
        self.line = line
        # had to create unique IDs per sensor here, using key.name
        self._attr_unique_id = (
            entity_description.key + "." + self.ean + "." + entity_description.name
        )
        # make names unique per unit
        entity_description.name = entity_description.name.split(".")[0] + "." + self.ean
        self.entity_description = entity_description

    @property
    def native_value(self) -> str:
        """Return the native value of the sensor."""
        sensor = self.entity_description.name
        # value = self.coordinator.data[self.ean][0][sensor.split(".")[0]]
        value = self.line[sensor.split(".")[0]]
        LOGGER.debug(
            "Sensor value for %s is %s",
            self.unique_id,
            value,
        )
        return value
