# platform_bridge/flutter_cli.py
import subprocess
from pathlib import Path
from .config import SDKConfig


class FlutterCLI:
    """Handles all Flutter CLI operations"""

    def __init__(self, config: SDKConfig):
        self.config = config

    def run_command(self, cmd: list[str], cwd: Path | None = None, show_output: bool = True):
        """Run Flutter command and stream output"""
        cmd_list = [str(self.config.flutter_bin)] + [str(x) for x in cmd]
        process = subprocess.Popen(
            cmd_list,
            cwd=str(cwd) if cwd else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',    
            errors='replace',
        )

        output_lines = []
        for line in process.stdout:
            #print(line, end="")
            output_lines.append(line)

        process.wait()
        if process.returncode != 0:
            error_msg = ''.join(output_lines) if output_lines else "No output"
            raise RuntimeError(
                f"Flutter command failed ({process.returncode}):\n"
                f"Command: {' '.join(cmd_list)}\n"
                f"Output: {error_msg}"
            )
        
    def capture_command(self, cmd: list[str], cwd: Path | None = None) -> str:
        """Run Flutter command and capture output"""
        cmd_list = [str(self.config.flutter_bin)] + [str(x) for x in cmd]
        result = subprocess.run(
            cmd_list,
            cwd=str(cwd) if cwd else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',   
            errors='replace',
        )
        if result.returncode != 0:
            raise RuntimeError(
                result.stdout.strip() or f"Flutter command failed: {' '.join(cmd_list)}"
            )
        return result.stdout

    def create_project(self, output_dir: Path):
        app_dir = output_dir / "temp_app"
        """Create new Flutter project"""
        if app_dir.exists():
            print(f"{output_dir}/temp_app already exists, skipping flutter create")
            return app_dir
        print(f"Creating Flutter project at {output_dir}\\temp_app...")
        self.run_command(["create", "temp_app"], cwd=output_dir)
        return app_dir

    def pub_get(self, project_dir: Path):
        """Run flutter pub get"""
        print("Running flutter pub get...")
        self.run_command(["pub", "get"], cwd=(project_dir))

    def build_apk(self, project_dir: Path):
        """Build Android APK"""
        print("Building Android APK...")
        self.run_command(["build", "apk"], cwd=project_dir)

    def build_ios(self, project_dir: Path):
        """Build iOS app"""
        print("Building iOS app...")
        self.run_command(["build", "ios"], cwd=project_dir)

    def run_on_device(self, project_dir: Path, device_id: str | None = None, return_process: bool = False):
        """Run Flutter app on specified device"""
        cmd = ["run"]
        if device_id:
            cmd.extend(["-d", device_id])
        
        if return_process:
            cmd_list = [str(self.config.flutter_bin)] + [str(x) for x in cmd]
            process = subprocess.Popen(
                cmd_list,
                cwd=str(project_dir),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1
            )
            return process
        else:
            self.run_command(cmd, cwd=project_dir)

    def list_devices(self) -> list[str]:
        """Get raw device list from flutter devices"""
        out = self.capture_command(["devices"])
        return out.splitlines()
