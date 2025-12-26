# platform_bridge/android_manager.py
import subprocess
import time
from pathlib import Path
from .config import SDKConfig
from .device import Device, DeviceType, DeviceStatus


class AndroidDeviceManager:
    """Manages Android devices and emulators"""

    def __init__(self, config: SDKConfig):
        self.config = config

    def _require_adb(self) -> Path:
        """Ensure adb is available"""
        if not self.config.adb_bin:
            raise RuntimeError(
                "adb not found. Install Android SDK platform-tools or set ANDROID_SDK_ROOT."
            )
        return self.config.adb_bin

    def _require_emulator(self) -> Path:
        """Ensure emulator is available"""
        if not self.config.emulator_bin:
            raise RuntimeError(
                "Android emulator not found. Install Android SDK emulator or set ANDROID_SDK_ROOT."
            )
        return self.config.emulator_bin

    def _run_adb(self, args: list[str]) -> str:
        """Run adb command and return output"""
        adb = self._require_adb()
        result = subprocess.run(
            [str(adb)] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"adb command failed: {result.stdout.strip()}")
        return result.stdout

    def _run_emulator(self, args: list[str]) -> str:
        """Run emulator command and return output"""
        emulator = self._require_emulator()
        result = subprocess.run(
            [str(emulator)] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"emulator command failed: {result.stdout.strip()}")
        return result.stdout

    def list_connected_devices(self) -> list[Device]:
        """List all connected Android devices/emulators via adb"""
        out = self._run_adb(["devices"])
        devices = []

        for line in out.splitlines()[1:]:  # Skip header
            if "\tdevice" in line:
                device_id = line.split("\t")[0].strip()
                devices.append(
                    Device(
                        id=device_id,
                        name=device_id,  # Could query more details with adb -s
                        type=DeviceType.ANDROID,
                        status=DeviceStatus.ONLINE,
                    )
                )

        return devices

    def is_any_device_connected(self) -> bool:
        """Check if any Android device is connected"""
        return len(self.list_connected_devices()) > 0

    def list_avds(self) -> list[str]:
        """List installed AVDs (not necessarily running)"""
        out = self._run_emulator(["-list-avds"])
        return [line.strip() for line in out.splitlines() if line.strip()]

    def is_avd_running(self, avd_name: str) -> bool:
        """Check if specific AVD is running"""
        devices = self.list_connected_devices()
        # This is approximate - adb doesn't expose AVD name directly
        return len(devices) > 0

    def start_avd(self, avd_name: str, wait: bool = True, timeout_s: int = 180):
        """Start an AVD emulator"""
        emulator = self._require_emulator()
        adb = self._require_adb()

        # Verify AVD exists
        avds = self.list_avds()
        if avd_name not in avds:
            raise RuntimeError(f"AVD '{avd_name}' not found. Available: {avds}")

        print(f"Starting Android emulator: {avd_name}")
        subprocess.Popen(
            [str(emulator), "-avd", avd_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        if not wait:
            return

        print("Waiting for emulator to boot...")
        start = time.time()
        while True:
            if self.is_any_device_connected():
                print("Emulator ready!")
                return

            if time.time() - start > timeout_s:
                raise RuntimeError(
                    f"Timed out waiting for emulator to start (>{timeout_s}s)"
                )

            time.sleep(2)
