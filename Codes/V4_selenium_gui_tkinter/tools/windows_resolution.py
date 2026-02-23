"""
Windows DPI scaling ratio calculation.
Must be imported before other modules that depend on DPI calculations.
"""
from win32 import win32api, win32gui, win32print
from win32.lib import win32con
from win32.win32api import GetSystemMetrics


def get_real_resolution():
    """Get the real (physical) resolution."""
    hDC = win32gui.GetDC(0)
    # Horizontal resolution
    w = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
    # Vertical resolution
    h = win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES)
    return w, h


def get_screen_size():
    """Get the scaled (logical) resolution."""
    w = GetSystemMetrics(0)
    h = GetSystemMetrics(1)
    return w, h


def get_windows_scale_ratio():
    """Calculate the Windows DPI scaling ratio."""
    real_resolution = get_real_resolution()
    screen_size = get_screen_size()
    screen_scale_rate = round(real_resolution[0] / screen_size[0], 2)
    return screen_scale_rate


if __name__ == "__main__":
    print(f"Windows scale ratio: {get_windows_scale_ratio()}")
