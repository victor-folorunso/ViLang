# platform_bridge/executor.py
from pathlib import Path
from .config import SDKConfig
from .flutter_cli import FlutterCLI
from .android_manager import AndroidDeviceManager
from .ios_manager import IOSDeviceManager
from .device import Device, DeviceType


class Executor:
    """
    Main orchestrator for Flutter development workflow.
    
    Coordinates Flutter CLI, Android, and iOS device management.
    """

    def __init__(self, config: SDKConfig | None = None):
        self.config = config or SDKConfig.auto_detect()
        self.flutter = FlutterCLI(self.config)
        self.android = AndroidDeviceManager(self.config)
        self.ios = IOSDeviceManager(self.config)

    # -------------------------
    # Project operations
    # -------------------------

    def create_project(self, output_dir: Path, project_name: str = "temp_app"):
        """Create new Flutter project"""
        app_dir = self.flutter.create_project(output_dir)
        return app_dir

    def pub_get(self, project_dir: Path):
        """Run pub get"""
        self.flutter.pub_get(project_dir)

    def build_apk(self, project_dir: Path):
        """Build Android APK"""
        self.flutter.build_apk(project_dir)

    def build_ios(self, project_dir: Path):
        """Build iOS app"""
        self.flutter.build_ios(project_dir)
    
    def build_web(self, project_dir: Path):
        """Build web app"""
        print("Building web app...")
        self.flutter.run_command(["build", "web"], cwd=project_dir)

    # -------------------------
    # Device queries
    # -------------------------

    def list_all_devices(self) -> list[Device]:
        """List all available devices (Android, iOS, desktop, web)"""
        devices = []
        
        # Get Android devices
        try:
            devices.extend(self.android.list_connected_devices())
        except Exception as e:
            print(f"Warning: Could not list Android devices: {e}")

        # TODO: Add iOS devices
        # devices.extend(self.ios.list_connected_devices())

        # Parse Flutter devices for web/desktop
        try:
            flutter_lines = self.flutter.list_devices()
            for line in flutter_lines:
                if "•" in line and not line.strip().lower().startswith("found"):
                    parts = [p.strip() for p in line.split("•")]
                    if len(parts) >= 2:
                        device_id = parts[1]
                        device_name = parts[0]
                        
                        # Skip if already added (Android)
                        if any(d.id == device_id for d in devices):
                            continue
                        
                        # Determine type
                        dtype = DeviceType.UNKNOWN
                        if "chrome" in device_id.lower() or "edge" in device_id.lower():
                            dtype = DeviceType.WEB
                        elif "windows" in device_id.lower() or "macos" in device_id.lower() or "linux" in device_id.lower():
                            dtype = DeviceType.DESKTOP
                        
                        from .device import DeviceStatus
                        devices.append(Device(
                            id=device_id,
                            name=device_name,
                            type=dtype,
                            status=DeviceStatus.ONLINE
                        ))
        except Exception as e:
            print(f"Warning: Could not parse Flutter devices: {e}")

        return devices

    def list_avds(self) -> list[str]:
        """List installed Android AVDs"""
        return self.android.list_avds()

    # -------------------------
    # Run operations
    # -------------------------

    def run_app_interactive(self, project_dir: Path, return_process: bool = False):
        """
        Run Flutter app with interactive device selection.
        Shows running devices and offline AVDs, lets user pick.
        """
        # Get running devices
        running_devices = self.list_all_devices()
        
        # Get offline AVDs (installed but not running)
        all_avds = self.list_avds()
        running_android_count = sum(1 for d in running_devices if d.is_android())
        offline_avds = all_avds[running_android_count:] if running_android_count < len(all_avds) else []
        
        # Check if we have any options
        if not running_devices and not offline_avds:
            raise RuntimeError(
                "No devices available.\n"
                "- Start an emulator manually, or\n"
                "- Create an AVD in Android Studio Device Manager"
            )
        
        # Display options
        print("\n=== Available Devices ===\n")
        
        count = 1
        device_map = {}
        
        if running_devices:
            print("Running devices:")
            for device in running_devices:
                print(f"  {count}. {device.name} ({device.type.value})")
                device_map[count] = ('device', device)
                count += 1
        
        if offline_avds:
            print("\nOffline emulators (will be started):")
            for avd in offline_avds:
                print(f"  {count}. {avd}")
                device_map[count] = ('avd', avd)
                count += 1
        
        # Get user choice
        print()
        while True:
            try:
                choice = int(input("Choose device number: "))
            except (KeyboardInterrupt):
                print("\nCancelled.")
                return
            if choice in device_map:
                break
            elif choice not in device_map:
                print(f"Invalid choice: {choice}")
        
        # Execute based on choice
        option_type, option_data = device_map[choice]
        
        if option_type == 'device':
            # Run on existing device
            device = option_data
            print(f"\nRunning on {device.name}...")
            return self.flutter.run_on_device(project_dir, device.id, return_process=return_process)
        
        elif option_type == 'avd':
            # Start AVD and run
            avd_name = option_data
            print(f"\nStarting {avd_name}...")
            self.android.start_avd(avd_name, wait=True)
            print(f"Running app on {avd_name}...")
            return self.flutter.run_on_device(project_dir, return_process=return_process)

    def run_app(self, project_dir: Path, target: str | None = None, avd: str | None = None):
        """
        Run Flutter app with smart device selection (programmatic).
        
        Priority:
        1. If target specified: use it
        2. If Android device connected: use it
        3. If avd specified: start it and use it
        4. Error with available options
        """
        if target:
            print(f"Running on target: {target}")
            self.flutter.run_on_device(project_dir, target)
            return

        # Check for connected Android device
        if self.android.is_any_device_connected():
            print("Android device detected, running app...")
            self.flutter.run_on_device(project_dir)
            return

        # Start AVD if specified
        if avd:
            self.android.start_avd(avd, wait=True)
            print("Running app on started emulator...")
            self.flutter.run_on_device(project_dir)
            return

        # No device available - error with info
        avds = self.list_avds()
        if not avds:
            raise RuntimeError(
                "No devices connected and no AVDs installed.\n"
                "Create an AVD in Android Studio Device Manager."
            )

        raise RuntimeError(
            "No device/emulator running.\n"
            f"Available AVDs: {avds}\n"
            "Start one manually or use: executor.run_app(project_dir, avd='<n>')"
        )
