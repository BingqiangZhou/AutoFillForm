"""
Cross-platform DPI scaling ratio calculation.

- Windows: uses pywin32 API (falls back to 1.0 if unavailable)
- macOS: detects Retina via system_profiler
- Linux: reads GDK_SCALE env or Xft.dpi from xrdb
"""
import platform
import subprocess
import os


def _get_scale_ratio_windows():
    """Get DPI scale ratio on Windows using pywin32."""
    try:
        from win32 import win32api, win32gui, win32print
        from win32.lib import win32con

        hDC = win32gui.GetDC(0)
        real_w = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
        logical_w = win32api.GetSystemMetrics(0)
        return round(real_w / logical_w, 2)
    except ImportError:
        return 1.0


def _get_scale_ratio_macos():
    """Get DPI scale ratio on macOS by detecting Retina displays."""
    try:
        output = subprocess.check_output(
            ["system_profiler", "SPDisplaysDataType"],
            text=True, timeout=5
        )
        if "Retina" in output:
            return 2.0
        return 1.0
    except Exception:
        return 1.0


def _get_scale_ratio_linux():
    """Get DPI scale ratio on Linux from GDK_SCALE or xrdb Xft.dpi."""
    gdk_scale = os.environ.get("GDK_SCALE")
    if gdk_scale:
        try:
            return float(gdk_scale)
        except ValueError:
            pass

    try:
        output = subprocess.check_output(
            ["xrdb", "-query"], text=True, timeout=5
        )
        for line in output.splitlines():
            if "Xft.dpi" in line:
                dpi = float(line.split(":")[-1].strip())
                return round(dpi / 96.0, 2)
    except Exception:
        pass

    return 1.0


def get_scale_ratio():
    """Get the DPI scaling ratio for the current platform."""
    system = platform.system()
    if system == "Windows":
        return _get_scale_ratio_windows()
    elif system == "Darwin":
        return _get_scale_ratio_macos()
    elif system == "Linux":
        return _get_scale_ratio_linux()
    return 1.0


# Backward compatibility alias
get_windows_scale_ratio = get_scale_ratio


if __name__ == "__main__":
    print(f"Platform: {platform.system()}")
    print(f"Scale ratio: {get_scale_ratio()}")
