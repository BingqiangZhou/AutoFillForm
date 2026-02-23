"""
AutoFillForm V4 - Main Entry Point

Combines V2's automation capabilities with V3's modern GUI architecture.
"""
import tkinter as tk
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import SurveyModel, RuleModel, HistoryModel
from views import MainView, FillView, AnalyzeView, RuleEditorView, HistoryView
from controllers import MainController, FillController, AnalyzeController, RuleEditorController, HistoryController
from utils import GuiLogger


class AutoFillFormApp:
    """Main application class."""

    def __init__(self):
        """Initialize the application."""
        self.root = tk.Tk()
        self.root.title("AutoFillForm V4")

        # Set window icon if available
        # self.root.iconbitmap('icon.ico')

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

        # Create main view
        self.main_view = MainView(self.root, "AutoFillForm V4")

        # Create sub-views
        self.views = {
            'main': self.main_view,
            'fill': FillView(self.main_view.get_fill_frame()),
            'analyze': AnalyzeView(
                self.main_view.get_analyze_frame(),
                initial_link=self.models['survey'].get_survey_link()
            ),
            'rule_editor': RuleEditorView(self.main_view.get_rule_editor_frame()),
            'history': HistoryView(self.main_view.get_history_frame())
        }

        # Create controllers
        self.controllers = {
            'fill': FillController(
                self.models['survey'],
                self.views['fill'],
                self.models['rule'],
                self.models['history'],
                self.logger
            ),
            'analyze': AnalyzeController(
                self.models['survey'],
                self.views['analyze'],
                self.models['rule']
            ),
            'rule_editor': RuleEditorController(
                self.models['survey'],
                self.views['rule_editor'],
                self.models['rule']
            ),
            'history': HistoryController(
                self.models['survey'],
                self.views['history'],
                self.models['history']
            )
        }

        # Create main controller
        self.main_controller = MainController(
            self.root,
            self.models,
            self.views,
            self.controllers
        )

        # Load last rule file if available
        last_rule = self.models['survey'].get_last_rule_file()
        if last_rule:
            self.controllers['fill'].load_rule_file(last_rule)

        # Set initial status
        self.main_view.set_status("就绪 - AutoFillForm V4")

        # Log application start
        self.logger.info("AutoFillForm V4 启动")

        # Load window geometry if saved
        self._load_window_geometry()

        # Handle window close for geometry saving
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _load_window_geometry(self):
        """Load and restore window geometry."""
        geometry = self.models['survey'].get_config("window_geometry")
        if geometry:
            try:
                self.root.geometry(geometry)
            except:
                pass

    def _on_closing(self):
        """Handle window closing."""
        # Save window geometry
        self.models['survey'].set_config(
            "window_geometry",
            self.root.geometry()
        )

        # Use main controller's close handler
        self.main_controller.on_closing()

    def run(self):
        """Run the application main loop."""
        self.root.mainloop()


def main():
    """Main entry point."""
    app = AutoFillFormApp()
    app.run()


if __name__ == "__main__":
    main()
