# platform_bridge/device.py
from dataclasses import dataclass
from enum import Enum


class DeviceType(Enum):
    ANDROID = "android"
    IOS = "ios"
    WEB = "web"
    DESKTOP = "desktop"
    UNKNOWN = "unknown"


class DeviceStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    BOOTING = "booting"


@dataclass
class Device:
    """Represents a target device/emulator"""

    id: str
    name: str
    type: DeviceType
    status: DeviceStatus
    platform_details: str = ""

    def is_android(self):
        return self.type == DeviceType.ANDROID

    def is_available(self):
        return self.status == DeviceStatus.ONLINE

    def __str__(self):
        return f"{self.name} ({self.id}) - {self.status.value}"
