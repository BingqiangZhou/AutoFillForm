"""
Main view with tabbed interface - Migrated to PySide6.
"""
import os
import subprocess
import sys
import webbrowser

# Add parent directory to path for version import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import version as version_info

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                              QStatusBar, QLabel, QPushButton, QTextEdit,
                              QProgressBar, QFileDialog, QMessageBox,
                              QScrollArea)
from PySide6.QtCore import Qt

from utils.updater import UpdateChecker


class MainView(QWidget):
    """Main application window with tabbed interface using PySide6."""

    def __init__(self, main_window, title=None):
        """
        Initialize the main view.

        Args:
            main_window: QMainWindow instance.
            title (str): Window title.
        """
        super().__init__()
        self.main_window = main_window

        # Set default title if not provided
        if title is None:
            title = version_info.__fullname__

        # Set up the central widget layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create notebook (tabs)
        self.notebook = QTabWidget()
        layout.addWidget(self.notebook)

        # Create widgets for each tab
        self.workflow_widget = QWidget()
        self.history_widget = QWidget()
        self.about_widget = QWidget()

        # Add tabs to notebook
        self.notebook.addTab(self.workflow_widget, "问卷工作流")
        self.notebook.addTab(self.history_widget, "历史记录")
        self.notebook.addTab(self.about_widget, "关于")

        # Build about page content
        self._setup_about_page()

        # Set up status bar on main window
        self.setup_status_bar(main_window)

    # ------------------------------------------------------------------
    # About page
    # ------------------------------------------------------------------

    def _setup_about_page(self):
        """Set up the about tab page content with update checker UI."""
        # Use a scroll area so the page is scrollable on small screens
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)

        # --- Static about info ---
        about_text = QLabel(
            f"<h2>{version_info.__fullname__}</h2>"
            "<p>自动填写问卷工具</p>"
            "<p>迁移自V4: Playwright + PySide6</p>"
            "<hr>"
            "<h3>功能特性</h3>"
            "<ul>"
            "<li>问卷工作流 (分析+配置+填写)</li>"
            "<li>多种题型支持 (单选、多选、矩阵、填空、下拉)</li>"
            "<li>智能验证和滑块验证</li>"
            "<li>历史记录与会话恢复</li>"
            "</ul>"
            "<h3>技术栈</h3>"
            "<ul>"
            "<li>Playwright (浏览器自动化)</li>"
            "<li>PySide6 (GUI框架)</li>"
            "</ul>"
        )
        about_text.setWordWrap(True)
        about_text.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(about_text)

        # --- Update section ---
        layout.addWidget(self._make_separator())

        # Check update row
        check_row = QHBoxLayout()
        self._check_btn = QPushButton("检查更新")
        self._check_btn.setFixedWidth(120)
        self._check_btn.clicked.connect(self._on_check_update)
        check_row.addWidget(self._check_btn)

        self._version_label = QLabel("")
        check_row.addWidget(self._version_label, 1)
        layout.addLayout(check_row)

        # Release notes area (hidden by default)
        self._notes_edit = QTextEdit()
        self._notes_edit.setReadOnly(True)
        self._notes_edit.setVisible(False)
        self._notes_edit.setMaximumHeight(200)
        layout.addWidget(self._notes_edit)

        # Download row (hidden by default)
        self._download_row = QWidget()
        dl_layout = QHBoxLayout(self._download_row)
        dl_layout.setContentsMargins(0, 0, 0, 0)

        self._download_btn = QPushButton("下载更新")
        self._download_btn.clicked.connect(self._on_download)
        dl_layout.addWidget(self._download_btn)

        self._open_browser_btn = QPushButton("在浏览器中打开")
        self._open_browser_btn.clicked.connect(self._on_open_in_browser)
        dl_layout.addWidget(self._open_browser_btn)

        self._cancel_btn = QPushButton("取消")
        self._cancel_btn.clicked.connect(self._on_cancel_download)
        self._cancel_btn.setVisible(False)
        dl_layout.addWidget(self._cancel_btn)

        dl_layout.addStretch()
        self._download_row.setVisible(False)
        layout.addWidget(self._download_row)

        # Progress bar (hidden by default)
        self._progress_bar = QProgressBar()
        self._progress_bar.setVisible(False)
        layout.addWidget(self._progress_bar)

        layout.addStretch()

        scroll.setWidget(container)

        page_layout = QVBoxLayout(self.about_widget)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll)

        # --- UpdateChecker instance ---
        self._updater = UpdateChecker(
            version_info.__repo_owner__,
            version_info.__repo_name__,
            version_info.__version__,
            parent=self,
        )
        self._updater.check_finished.connect(self._on_check_finished)
        self._updater.check_error.connect(self._on_check_error)
        self._updater.download_progress.connect(self._on_download_progress)
        self._updater.download_finished.connect(self._on_download_finished)
        self._updater.download_error.connect(self._on_download_error)

        # Stash latest release info
        self._latest_release = None

    @staticmethod
    def _make_separator():
        sep = QLabel("<hr>")
        sep.setFixedHeight(20)
        return sep

    # --- Update slots ---

    def _on_check_update(self):
        self._check_btn.setEnabled(False)
        self._version_label.setText("正在检查更新...")
        self._notes_edit.setVisible(False)
        self._download_row.setVisible(False)
        self._progress_bar.setVisible(False)
        self._updater.check()

    def _on_check_finished(self, info):
        self._check_btn.setEnabled(True)
        self._latest_release = info

        if info["has_update"]:
            self._version_label.setText(
                f"<b>发现新版本: {info['latest_version']}</b>  (当前: v{info['current_version']})"
            )
            # Show release notes
            body = info.get("body", "")
            if body:
                self._notes_edit.setPlainText(body)
                self._notes_edit.setVisible(True)
            # Show download row
            if info.get("asset_url"):
                self._download_btn.setText(f"下载 {info['asset_name']}")
            else:
                self._download_btn.setText("下载更新 (未找到当前平台安装包)")
                self._download_btn.setEnabled(False)
            self._download_row.setVisible(True)
        else:
            self._version_label.setText(
                f"当前已是最新版本 (v{info['current_version']})"
            )

    def _on_check_error(self, msg):
        self._check_btn.setEnabled(True)
        self._version_label.setText(f"检查更新失败: {msg}")

    def _on_download(self):
        if not self._latest_release or not self._latest_release.get("asset_url"):
            return

        asset_name = self._latest_release["asset_name"]
        save_path, _ = QFileDialog.getSaveFileName(
            self, "保存更新文件", asset_name, "Zip files (*.zip)"
        )
        if not save_path:
            return

        self._download_btn.setEnabled(False)
        self._cancel_btn.setVisible(True)
        self._progress_bar.setValue(0)
        self._progress_bar.setVisible(True)
        self._updater.download(self._latest_release["asset_url"], save_path)

    def _on_open_in_browser(self):
        if self._latest_release and self._latest_release.get("html_url"):
            webbrowser.open(self._latest_release["html_url"])

    def _on_cancel_download(self):
        self._updater.cancel_download()

    def _on_download_progress(self, downloaded, total):
        if total > 0:
            self._progress_bar.setMaximum(total)
            self._progress_bar.setValue(downloaded)
        else:
            # Indeterminate
            self._progress_bar.setMaximum(0)

    def _on_download_finished(self, path):
        self._download_btn.setEnabled(True)
        self._cancel_btn.setVisible(False)
        self._progress_bar.setVisible(False)

        folder = os.path.dirname(os.path.abspath(path))
        reply = QMessageBox.information(
            self, "下载完成",
            f"文件已保存到:\n{path}\n\n是否打开所在文件夹？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._open_folder(folder)

    def _on_download_error(self, msg):
        self._download_btn.setEnabled(True)
        self._cancel_btn.setVisible(False)
        self._progress_bar.setVisible(False)
        QMessageBox.warning(self, "下载失败", msg)

    @staticmethod
    def _open_folder(folder):
        """Open a folder in the system file manager."""
        import platform as _plat
        system = _plat.system()
        if system == "Windows":
            os.startfile(folder)
        elif system == "Darwin":
            subprocess.Popen(["open", folder])
        else:
            subprocess.Popen(["xdg-open", folder])

    # ------------------------------------------------------------------
    # Status bar & tab helpers
    # ------------------------------------------------------------------

    def setup_status_bar(self, main_window):
        """Set up the status bar."""
        self.status_bar = main_window.statusBar()
        self.status_label = QLabel("就绪")
        self.status_bar.addPermanentWidget(self.status_label, 1)

    def set_status(self, message):
        """
        Update the status bar message.

        Args:
            message (str): Status message.
        """
        self.status_label.setText(message)

    def get_current_tab(self):
        """Get the currently selected tab index."""
        return self.notebook.currentIndex()

    def switch_to_tab(self, tab_index):
        """
        Switch to a specific tab.

        Args:
            tab_index (int): Tab index to switch to.
        """
        self.notebook.setCurrentIndex(tab_index)

    def get_workflow_widget(self):
        """Get the workflow tab widget."""
        return self.workflow_widget

    def get_history_widget(self):
        """Get the history tab widget."""
        return self.history_widget
