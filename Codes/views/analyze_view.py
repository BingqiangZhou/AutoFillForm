"""
Survey analysis view - Migrated to PyQt6.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTextEdit, QFileDialog,
                             QMessageBox, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class AnalyzeView(QWidget):
    """View for the survey analysis tab using PyQt6."""

    def __init__(self, parent_widget, initial_link=""):
        """
        Initialize the analyze view.

        Args:
            parent_widget: Parent widget to contain this view.
            initial_link (str): Initial survey link.
        """
        super().__init__(parent_widget)

        # Ensure this widget fills the parent tab page
        parent_layout = QVBoxLayout(parent_widget)
        parent_layout.setContentsMargins(0, 0, 0, 0)
        parent_layout.addWidget(self)

        self.setup_ui(initial_link)

    def setup_ui(self, initial_link):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Input frame
        input_group = QGroupBox("问卷链接")
        input_layout = QHBoxLayout(input_group)

        self.link_label = QLabel("链接:")
        input_layout.addWidget(self.link_label)

        self.link_edit = QLineEdit()
        self.link_edit.setText(initial_link)
        self.link_edit.setMinimumWidth(400)
        input_layout.addWidget(self.link_edit)

        self.analyze_button = QPushButton("分析问卷")
        input_layout.addWidget(self.analyze_button)

        layout.addWidget(input_group)

        # Toolbar
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(0, 5, 0, 5)

        self.export_text_button = QPushButton("导出文本")
        self.export_text_button.setFixedWidth(100)
        toolbar_layout.addWidget(self.export_text_button)

        self.export_yaml_button = QPushButton("导出为YAML模板")
        self.export_yaml_button.setFixedWidth(130)
        toolbar_layout.addWidget(self.export_yaml_button)

        self.clear_button = QPushButton("清空")
        self.clear_button.setFixedWidth(80)
        toolbar_layout.addWidget(self.clear_button)

        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)

        # Results frame
        results_group = QGroupBox("分析结果")
        results_layout = QVBoxLayout(results_group)

        self.result_text = QTextEdit()
        font = QFont("Consolas", 10)
        self.result_text.setFont(font)
        self.result_text.setPlaceholderText("分析结果将显示在这里...")
        results_layout.addWidget(self.result_text)

        layout.addWidget(results_group, 1)

    def set_analyze_command(self, command):
        """Set the command for the analyze button."""
        self.analyze_button.clicked.connect(command)

    def set_export_text_command(self, command):
        """Set the command for the export text button."""
        self.export_text_button.clicked.connect(command)

    def set_export_yaml_command(self, command):
        """Set the command for the export YAML button."""
        self.export_yaml_button.clicked.connect(command)

    def set_clear_command(self, command):
        """Set the command for the clear button."""
        self.clear_button.clicked.connect(command)

    def get_survey_link(self):
        """Get the survey link from the entry."""
        return self.link_edit.text().strip()

    def set_survey_link(self, link):
        """Set the survey link in the entry."""
        self.link_edit.setText(link)

    def display_results(self, results):
        """Display analysis results in the text area."""
        self.result_text.setPlainText(results)

    def get_results(self):
        """Get the current results text."""
        return self.result_text.toPlainText().strip()

    def clear_results(self):
        """Clear the results text area."""
        self.result_text.clear()

    def show_info(self, title, message):
        """Show an info dialog."""
        QMessageBox.information(self, title, message)

    def show_error(self, title, message):
        """Show an error dialog."""
        QMessageBox.critical(self, title, message)

    def ask_to_save_text(self):
        """Show file dialog for saving text results."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出分析结果",
            "",
            "Text files (*.txt);;All files (*.*)"
        )
        return file_path

    def ask_to_save_yaml(self):
        """Show file dialog for saving YAML template."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出YAML模板",
            "",
            "YAML files (*.yaml);;All files (*.*)"
        )
        return file_path

    # For backward compatibility with controller using after()
    def after(self, ms, callback):
        """Schedule a callback to run after ms milliseconds (for compatibility)."""
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(ms, callback)
