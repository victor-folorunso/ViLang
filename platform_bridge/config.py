# platform_bridge/config.py
import os
from pathlib import Path
from dataclasses import dataclass


@dataclass
class SDKConfig:
    """Configuration for Flutter and Android SDKs"""

    flutter_bin: Path
    android_sdk_root: Path | None = None
    adb_bin: Path | None = None
    emulator_bin: Path | None = None

    @classmethod
    def auto_detect(cls):
        """Auto-detect SDK paths"""
        # Flutter SDK (local)
        flutter_bin = (
            Path(__file__).parent
            / "flutter"
            / "bin"
            / ("flutter.bat" if os.name == "nt" else "flutter")
        )
        if not flutter_bin.exists():
            raise FileNotFoundError(f"Flutter binary not found at {flutter_bin}")

        # Android SDK root
        android_sdk_root = cls._find_android_sdk()

        # adb and emulator
        adb_bin = cls._find_tool(
            "adb", android_sdk_root / "platform-tools" if android_sdk_root else None
        )
        emulator_bin = cls._find_tool(
            "emulator", android_sdk_root / "emulator" if android_sdk_root else None
        )

        return cls(
            flutter_bin=flutter_bin,
            android_sdk_root=android_sdk_root,
            adb_bin=adb_bin,
            emulator_bin=emulator_bin,
        )

    @staticmethod
    def _find_android_sdk():
        """Find Android SDK root"""
        # Check environment variables
        for var in ["ANDROID_SDK_ROOT", "ANDROID_HOME"]:
            if var in os.environ:
                p = Path(os.environ[var])
                if p.exists():
                    return p

        # Windows default
        if os.name == "nt":
            local = os.environ.get("LOCALAPPDATA")
            if local:
                p = Path(local) / "Android" / "Sdk"
                if p.exists():
                    return p

        return None

    @staticmethod
    def _find_tool(name, sdk_path):
        """Find tool by name (adb, emulator)"""
        import shutil

        # Try PATH first
        tool = shutil.which(name)
        if tool:
            return Path(tool)

        # Try SDK path
        if sdk_path and sdk_path.exists():
            exe = sdk_path / (f"{name}.exe" if os.name == "nt" else name)
            if exe.exists():
                return exe

        return None
