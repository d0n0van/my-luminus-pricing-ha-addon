"""Sensor setup for My Luminus - Pricing."""

import logging

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import MyConfigEntry
from .base import LuminusBaseEntity
from .const import DEVICE_META_KEYS
from .coordinator import LuminusCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Sensors."""
    # This gets the data update coordinator from the config entry runtime data as specified in your __init__.py
    coordinator: LuminusCoordinator = config_entry.runtime_data.coordinator

    # ----------------------------------------------------------------------------
    # Here we enumerate the sensors in your data value from your
    # DataUpdateCoordinator and add an instance of your sensor class to a list
    # for each one.
    # This maybe different in your specific case, depending on how your data is
    # structured
    # ----------------------------------------------------------------------------

    sensors = []
    for device in coordinator.data or []:
        sensors.append(LuminusBaseSensor(coordinator, device, "product_name"))
        for prop_name, _ in device.items():
            if prop_name in DEVICE_META_KEYS:
                continue
            sensor_type = (
                YearlyPriceSensor if prop_name == "fixed" else EnergyPriceSensor
            )
            sensors.append(sensor_type(coordinator, device, prop_name))

    # Now create the sensors.
    async_add_entities(sensors)


class LuminusBaseSensor(LuminusBaseEntity, SensorEntity):
    @property
    def native_value(self) -> int | float | None:
        """Return the state of the entity."""
        return self.coordinator.get_device_parameter(self.device_id, self.parameter)


class YearlyPriceSensor(LuminusBaseSensor):

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_native_unit_of_measurement = 'EUR/year'
    _attr_suggested_display_precision = 2


class EnergyPriceSensor(LuminusBaseSensor):

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_native_unit_of_measurement = 'EUR/kWh'
    _attr_suggested_display_precision = 4

