"""
AutoFillForm V5 - Main Entry Point

Migrated from V4: Tkinter -> PyQt6, Selenium -> Playwright
"""
import os
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QSettings

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import SurveyModel, RuleModel, HistoryModel
from views import MainView, WorkflowView, HistoryView
from controllers import MainController, WorkflowController, HistoryController
from utils import GuiLogger


class AutoFillFormApp(QMainWindow):
    """Main application class with PyQt6."""

    def __init__(self):
        """Initialize the application."""
        super().__init__()
        self.setWindowTitle("AutoFillForm V5")
        self.resize(900, 700)

        # QSettings for window geometry persistence
        self.settings = QSettings("AutoFillForm", "V5")

        # Get the script directory
        if getattr(sys, 'frozen', False):
            self.script_dir = os.path.dirname(sys.executable)
        else:
            self.script_dir = os.path.dirname(os.path.abspath(__file__))

        # Create logger
        self.logger = GuiLogger(
            name="AutoFillForm",
            log_dir=os.path.join(self.script_dir, "history")
        )

        # Create models
        self.models = {
            'survey': SurveyModel(config_dir=os.path.join(self.script_dir, "history")),
            'rule': RuleModel(rules_dir=os.path.join(self.script_dir, "rules")),
            'history': HistoryModel(history_dir=os.path.join(self.script_dir, "history"))
        }

        # Create main view and set as central widget
        self.main_view = MainView(self)
        self.setCentralWidget(self.main_view)

        # Create sub-views
        self.views = {
            'main': self.main_view,
            'workflow': WorkflowView(self.main_view.get_workflow_widget()),
            'history': HistoryView(self.main_view.get_history_widget())
        }

        # Create controllers
        self.controllers = {
            'workflow': WorkflowController(
                self.models['survey'],
                self.views['workflow'],
                self.models['rule'],
                self.models['history'],
                self.logger
            ),
            'history': HistoryController(
                self.models['survey'],
                self.views['history'],
                self.models['history']
            )
        }

        # Create main controller
        self.main_controller = MainController(
            self,
            self.models,
            self.views,
            self.controllers
        )

        # Set initial status
        self.main_view.set_status("就绪 - AutoFillForm V5")

        # Log application start
        self.logger.info("AutoFillForm V5 启动")

        # Load window geometry if saved
        self._load_window_geometry()

    def _load_window_geometry(self):
        """Load and restore window geometry from QSettings."""
        geometry = self.settings.value("window_geometry")
        if geometry:
            try:
                self.restoreGeometry(geometry)
            except:
                pass

    def closeEvent(self, event):
        """Handle window closing event."""
        # Save window geometry
        self.settings.setValue("window_geometry", self.saveGeometry())

        # Use main controller's close handler
        self.main_controller.on_closing()
        event.accept()

    def run(self):
        """Run the application main loop."""
        self.show()


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("AutoFillForm")
    app.setOrganizationName("AutoFillForm")

    window = AutoFillFormApp()
    window.run()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
