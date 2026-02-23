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

        self.setup_cross_controller_wiring()

    def setup_cross_controller_wiring(self):
        """Wire cross-controller callbacks."""
        def on_restore_session(session):
            self.controllers['workflow'].restore_session(session)
            self.views['main'].switch_to_tab(0)  # Switch to workflow tab

        self.controllers['history'].set_restore_callback(on_restore_session)

    def on_closing(self):
        """Handle window closing event."""
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
