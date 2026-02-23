"""
GitHub Release update checker.

Uses urllib (stdlib) to query the GitHub API — no extra dependencies required.
"""
import json
import os
import platform
import re
import threading
import urllib.request
import urllib.error

from PySide6.QtCore import QObject, Signal


def _parse_version(version_str):
    """Parse a version string like '5.1.0' or 'v5.1.0' into a comparable tuple."""
    cleaned = version_str.lstrip("vV")
    parts = re.findall(r"\d+", cleaned)
    return tuple(int(p) for p in parts)


def _platform_keyword():
    """Return a keyword that matches asset file names for the current OS."""
    system = platform.system()
    if system == "Windows":
        return "windows"
    elif system == "Darwin":
        return "macos"
    elif system == "Linux":
        return "linux"
    return system.lower()


class UpdateChecker(QObject):
    """Check for updates via GitHub Releases API and download assets."""

    # Signals
    check_finished = Signal(dict)   # release info dict
    check_error = Signal(str)       # error message

    download_progress = Signal(int, int)  # bytes_downloaded, total_bytes
    download_finished = Signal(str)       # saved file path
    download_error = Signal(str)          # error message

    def __init__(self, owner, repo, current_version, parent=None):
        super().__init__(parent)
        self.owner = owner
        self.repo = repo
        self.current_version = current_version
        self._cancel_event = threading.Event()

    # ------------------------------------------------------------------
    # Check for updates
    # ------------------------------------------------------------------

    def check(self):
        """Start checking for updates in a background thread."""
        self._cancel_event.clear()
        t = threading.Thread(target=self._check_worker, daemon=True)
        t.start()

    def _check_worker(self):
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/releases/latest"
        req = urllib.request.Request(url, headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "AutoFillForm-UpdateChecker",
        })
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                self.check_error.emit("没有找到任何 Release")
            else:
                self.check_error.emit(f"GitHub API 错误: HTTP {e.code}")
            return
        except Exception as e:
            self.check_error.emit(f"网络请求失败: {e}")
            return

        tag = data.get("tag_name", "")
        remote_version = _parse_version(tag)
        local_version = _parse_version(self.current_version)

        keyword = _platform_keyword()
        matching_asset = None
        for asset in data.get("assets", []):
            name = asset.get("name", "").lower()
            if keyword in name and name.endswith(".zip"):
                matching_asset = asset
                break

        result = {
            "has_update": remote_version > local_version,
            "latest_version": tag,
            "current_version": self.current_version,
            "html_url": data.get("html_url", ""),
            "body": data.get("body", ""),
            "asset_name": matching_asset["name"] if matching_asset else None,
            "asset_url": matching_asset["browser_download_url"] if matching_asset else None,
            "asset_size": matching_asset["size"] if matching_asset else 0,
        }
        self.check_finished.emit(result)

    # ------------------------------------------------------------------
    # Download asset
    # ------------------------------------------------------------------

    def download(self, url, save_path):
        """Download an asset to *save_path* in a background thread."""
        self._cancel_event.clear()
        t = threading.Thread(target=self._download_worker, args=(url, save_path), daemon=True)
        t.start()

    def cancel_download(self):
        """Cancel an in-progress download."""
        self._cancel_event.set()

    def _download_worker(self, url, save_path):
        req = urllib.request.Request(url, headers={
            "User-Agent": "AutoFillForm-UpdateChecker",
        })
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                total = int(resp.headers.get("Content-Length", 0))
                downloaded = 0
                chunk_size = 64 * 1024  # 64 KB

                with open(save_path, "wb") as f:
                    while True:
                        if self._cancel_event.is_set():
                            f.close()
                            # Clean up partial file
                            try:
                                os.remove(save_path)
                            except OSError:
                                pass
                            self.download_error.emit("下载已取消")
                            return

                        chunk = resp.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        self.download_progress.emit(downloaded, total)

            self.download_finished.emit(save_path)

        except Exception as e:
            # Clean up partial file on error
            try:
                os.remove(save_path)
            except OSError:
                pass
            self.download_error.emit(f"下载失败: {e}")
