"""
Main controller - coordinates between views and sub-controllers.
Migrated to PyQt6.
"""
from PyQt6.QtWidgets import QMessageBox


class MainController:
    """Main controller that coordinates all sub-controllers using PyQt6."""

    def __init__(self, main_window, models, views, controllers):
        """
        Initialize the main controller.

        Args:
            main_window: QMainWindow instance.
            models: Dictionary of model instances.
            views: Dictionary of view instances.
            controllers: Dictionary of controller instances.
        """
        self.main_window = main_window
        self.models = models
        self.views = views
        self.controllers = controllers

        self.setup_menu_handlers()

    def setup_menu_handlers(self):
        """Set up menu bar handlers."""
        main_view = self.views['main']

        def new_rule():
            self.controllers['rule_editor'].new_rule()
            main_view.switch_to_tab(1)  # Rule editor tab

        def export_yaml():
            self.controllers['workflow'].export_yaml()

        def export_history():
            self.controllers['history'].export_selected()

        def clear_history():
            self.controllers['history'].clear_all_history()

        # Connect handlers to main view
        main_view.set_menu_handler("new_rule", new_rule)
        main_view.set_menu_handler("export_yaml", export_yaml)
        main_view.set_menu_handler("export_history", export_history)
        main_view.set_menu_handler("clear_history", clear_history)

    def on_closing(self):
        """Handle window closing event."""
        # Check for unsaved changes in rule editor
        if self.controllers['rule_editor'].has_unsaved_changes():
            reply = QMessageBox.question(
                None,
                "退出确认",
                "规则编辑器有未保存的更改，确定要退出吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return

        # Stop any running fills
        if self.controllers['workflow'].check_is_running():
            reply = QMessageBox.question(
                None,
                "退出确认",
                "填写任务正在运行，确定要退出吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
            self.controllers['workflow'].stop_fill()

        # Save configuration
        self.models['survey'].save_config_to_file()

        # Clean up workflow controller
        self.controllers['workflow'].cleanup()

    def get_controller(self, name):
        """Get a sub-controller by name."""
        return self.controllers.get(name)

    def get_model(self, name):
        """Get a model by name."""
        return self.models.get(name)

    def get_view(self, name):
        """Get a view by name."""
        return self.views.get(name)

    def set_status(self, message):
        """Set the main window status bar."""
        self.views['main'].set_status(message)

    def switch_to_tab(self, tab_index):
        """Switch to a specific tab."""
        self.views['main'].switch_to_tab(tab_index)
