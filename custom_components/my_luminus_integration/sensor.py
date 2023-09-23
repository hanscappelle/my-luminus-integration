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

ENTITY_DESCRIPTIONS_LINES = (
    SensorEntityDescription(
        key="my_luminus",
        name="NextInvoiceDate",
        icon="mdi:receipt-text",
        # device_class=SensorDeviceClass.DATE,
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
ENTITIES_STATEMENTS = (
    SensorEntityDescription(
        key="my_luminus",
        name="AmountOpen",
        icon="mdi:cash-100",
        device_class=SensorDeviceClass.MONETARY,
    ),
)


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # create sensors for all units found, not just the first one
    LOGGER.debug("lines found %s", coordinator.lines)
    devices = []

    for line in coordinator.lines:
        LOGGER.debug("(0)init data for %s", line)
        for entity_description in ENTITY_DESCRIPTIONS_LINES:
            # async_add_devices(
            devices.append(
                MyLuminusSensor(
                    coordinator=coordinator,
                    entity_description=entity_description,
                    ean=line["Ean"],
                    line=line,
                    sensor=entity_description.name.split(".")[0],
                )
            )
            # for entity_description in ENTITY_DESCRIPTIONS_LINES
            # )

    # append statement data
    devices.append(
        MyLuminusStatementSensor(
            coordinator=coordinator,
            entity_description=ENTITIES_STATEMENTS[0],
        )
    )
    async_add_devices(devices)


class MyLuminusStatementSensor(MyLuminusEntity, SensorEntity):
    """Sensor class for My Luminus open amount"""

    statements: dict

    def __init__(
        self,
        coordinator: MyLuminusCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        LOGGER.debug("creating sensor for open amount")
        self.statements = coordinator.statements
        self.entity_description = entity_description

    @property
    def native_value(self) -> str:
        """Return the native value of the sensor."""
        value = self.statements["AmountOpen"]["Value"]
        LOGGER.debug("parsing amount for sensor open amount %s", value)
        return float(value)


class MyLuminusSensor(MyLuminusEntity, SensorEntity):
    """Sensor class."""

    line = None
    sensor = str

    def __init__(
        self,
        coordinator: MyLuminusCoordinator,
        entity_description: SensorEntityDescription,
        ean: str,
        line: dict,
        sensor: str,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)

        # init data
        LOGGER.debug("init data for ean %s and sensor %s", ean, sensor)
        self.line = line
        self.sensor = sensor

        self.entity_description = entity_description

        # had to create unique IDs per sensor here, using key.name
        self._attr_unique_id = entity_description.key + "." + ean + "." + sensor
        # this way sensor name no longer needs to be unique
        self._attr_name = sensor  # + "." + ean
        # self.entity_id = sensor  # + "." + ean

    @property
    def native_value(self) -> str:
        """Return the native value of the sensor."""

        value = self.line[self.sensor]
        LOGGER.debug(
            "Sensor (id, name, value) is %s, %s, %s",
            self.unique_id,
            self.name,
            value,
        )
        # some values are numeric, check if we can parse those
        try:
            value = float(value)
        except: # noqa: E722
            LOGGER.debug("non numeric value received, not parsed")

        return value
