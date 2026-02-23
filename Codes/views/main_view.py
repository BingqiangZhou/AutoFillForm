"""
Main view with tabbed interface - Migrated to PyQt6.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QMenuBar,
                             QMenu, QStatusBar, QLabel, QMessageBox)
from PyQt6.QtCore import Qt


class MainView(QWidget):
    """Main application window with tabbed interface using PyQt6."""

    def __init__(self, main_window, title="AutoFillForm V5"):
        """
        Initialize the main view.

        Args:
            main_window: QMainWindow instance.
            title (str): Window title.
        """
        super().__init__()
        self.main_window = main_window

        # Set up the central widget layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create notebook (tabs)
        self.notebook = QTabWidget()
        layout.addWidget(self.notebook)

        # Create widgets for each tab
        self.workflow_widget = QWidget()
        self.rule_editor_widget = QWidget()
        self.history_widget = QWidget()

        # Add tabs to notebook
        self.notebook.addTab(self.workflow_widget, "问卷工作流")
        self.notebook.addTab(self.rule_editor_widget, "规则编辑")
        self.notebook.addTab(self.history_widget, "历史记录")

        # Set up menu bar and status bar on main window
        self.setup_menu(main_window)
        self.setup_status_bar(main_window)

    def setup_menu(self, main_window):
        """Set up the menu bar."""
        menubar = main_window.menuBar()

        # File menu
        file_menu = menubar.addMenu("文件")

        action_new_rule = file_menu.addAction("新建规则")
        action_new_rule.triggered.connect(lambda: self.on_menu_action("new_rule"))

        action_export_yaml = file_menu.addAction("导出YAML")
        action_export_yaml.triggered.connect(lambda: self.on_menu_action("export_yaml"))

        file_menu.addSeparator()

        action_exit = file_menu.addAction("退出")
        action_exit.triggered.connect(main_window.close)

        # Tools menu
        tools_menu = menubar.addMenu("工具")

        action_export = tools_menu.addAction("导出历史")
        action_export.triggered.connect(lambda: self.on_menu_action("export_history"))

        action_clear = tools_menu.addAction("清空历史")
        action_clear.triggered.connect(lambda: self.on_menu_action("clear_history"))

        # Help menu
        help_menu = menubar.addMenu("帮助")

        action_about = help_menu.addAction("关于")
        action_about.triggered.connect(self.show_about)

        # Store menu actions for controller to connect
        self.menu_actions = {
            "new_rule": action_new_rule,
            "export_yaml": action_export_yaml,
            "export_history": action_export,
            "clear_history": action_clear
        }

    def setup_status_bar(self, main_window):
        """Set up the status bar."""
        self.status_bar = main_window.statusBar()
        self.status_label = QLabel("就绪")
        self.status_bar.addPermanentWidget(self.status_label, 1)

    def on_menu_action(self, action):
        """Handle menu actions - to be connected to controller."""
        if hasattr(self, 'menu_handler') and action in self.menu_handler:
            self.menu_handler[action]()

    def set_menu_handler(self, action, handler):
        """
        Set a handler for a menu action.

        Args:
            action (str): Menu action identifier.
            handler (callable): Handler function.
        """
        if not hasattr(self, 'menu_handler'):
            self.menu_handler = {}
        self.menu_handler[action] = handler

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

    def get_rule_editor_widget(self):
        """Get the rule editor tab widget."""
        return self.rule_editor_widget

    def get_history_widget(self):
        """Get the history tab widget."""
        return self.history_widget

    def show_about(self):
        """Show the about dialog."""
        QMessageBox.information(
            None,
            "关于 AutoFillForm V5",
            "AutoFillForm V5\n\n"
            "自动填写问卷工具\n"
            "迁移自V4: Playwright + PyQt6\n\n"
            "功能特性:\n"
            "• 问卷工作流 (分析+配置+填写)\n"
            "• 多种题型支持 (单选、多选、矩阵、填空)\n"
            "• 智能验证和滑块验证\n"
            "• 规则编辑器\n"
            "• 历史记录\n\n"
            "技术栈:\n"
            "• Playwright (浏览器自动化)\n"
            "• PyQt6 (GUI框架)"
        )
