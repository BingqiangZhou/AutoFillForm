"""
Main view with tabbed interface - Migrated to PyQt6.
"""
import sys
import os

# Add parent directory to path for version import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import version as version_info

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTabWidget,
                             QStatusBar, QLabel)
from PyQt6.QtCore import Qt


class MainView(QWidget):
    """Main application window with tabbed interface using PyQt6."""

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

    def _setup_about_page(self):
        """Set up the about tab page content."""
        layout = QVBoxLayout(self.about_widget)
        layout.setContentsMargins(30, 30, 30, 30)

        about_text = QLabel(
            f"<h2>{version_info.__fullname__}</h2>"
            "<p>自动填写问卷工具</p>"
            "<p>迁移自V4: Playwright + PyQt6</p>"
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
            "<li>PyQt6 (GUI框架)</li>"
            "</ul>"
        )
        about_text.setWordWrap(True)
        about_text.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(about_text)

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

