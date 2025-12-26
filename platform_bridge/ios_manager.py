# platform_bridge/ios_manager.py
from .config import SDKConfig
from .device import Device


class IOSDeviceManager:
    """Manages iOS devices and simulators - TODO"""

    def __init__(self, config: SDKConfig):
        self.config = config

    def list_simulators(self) -> list[Device]:
        """List iOS simulators - TODO"""
        raise NotImplementedError("iOS support not implemented yet")

    def start_simulator(self, simulator_id: str):
        """Start iOS simulator - TODO"""
        raise NotImplementedError("iOS support not implemented yet")

    def list_connected_devices(self) -> list[Device]:
        """List connected iOS devices - TODO"""
        raise NotImplementedError("iOS support not implemented yet")
