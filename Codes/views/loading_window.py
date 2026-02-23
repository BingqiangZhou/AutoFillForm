"""
Loading window dialog - Migrated to PyQt6.
"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont


class LoadingWindow(QDialog):
    """Modal loading indicator dialog using PyQt6."""

    def __init__(self, parent, message="正在加载，请稍候..."):
        """
        Initialize the loading window.

        Args:
            parent: Parent window.
            message (str): Initial message to display.
        """
        super().__init__(parent)
        self.setWindowTitle("正在执行，请稍候...")
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setFixedSize(300, 100)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        self.message_label = QLabel(message)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.message_label)

        self.loading_label = QLabel("⏳")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setFont(QFont("Helvetica", 32))
        layout.addWidget(self.loading_label)

        # Center the dialog
        if parent:
            parent_rect = parent.geometry()
            x = parent_rect.x() + (parent_rect.width() - 300) // 2
            y = parent_rect.y() + (parent_rect.height() - 100) // 2
            self.move(x, y)

        # Start the animation
        self.rotate_label()

    def rotate_label(self):
        """Rotate the loading icon."""
        current_text = self.loading_label.text()
        if current_text == "⏳":
            self.loading_label.setText("⌛")
        else:
            self.loading_label.setText("⏳")
        QTimer.singleShot(500, self.rotate_label)

    def closeEvent(self, event):
        """Prevent window closing with X button."""
        event.ignore()

    def update_message(self, message):
        """Update the displayed message."""
        self.message_label.setText(message)
