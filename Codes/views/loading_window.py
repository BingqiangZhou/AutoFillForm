"""
Loading window dialog - Migrated to PySide6 with modern styling.
"""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QFont, QColor, QPainter, QPen


class SpinnerWidget(QLabel):
    """Animated circular spinner widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._angle = 0
        self.setFixedSize(48, 48)

        self._anim = QPropertyAnimation(self, b"angle")
        self._anim.setStartValue(0)
        self._anim.setEndValue(360)
        self._anim.setDuration(1000)
        self._anim.setLoopCount(-1)
        self._anim.start()

    def _get_angle(self):
        return self._angle

    def _set_angle(self, value):
        self._angle = value
        self.update()

    angle = Property(int, _get_angle, _set_angle)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw background arc (track)
        pen = QPen(QColor("#3E3E52"), 4)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        rect = self.rect().adjusted(6, 6, -6, -6)
        painter.drawEllipse(rect)

        # Draw spinning arc
        pen.setColor(QColor("#3B82F6"))
        pen.setWidth(4)
        painter.setPen(pen)
        painter.drawArc(rect, -self._angle * 16, 90 * 16)

        painter.end()


class LoadingWindow(QDialog):
    """Modal loading indicator dialog using PySide6."""

    def __init__(self, parent, message="正在加载，请稍候..."):
        """
        Initialize the loading window.

        Args:
            parent: Parent window.
            message (str): Initial message to display.
        """
        super().__init__(parent)
        self.setWindowTitle("正在执行，请稍候...")
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setFixedSize(320, 140)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)

        # Spinner
        self.spinner = SpinnerWidget()
        layout.addWidget(self.spinner, 0, Qt.AlignmentFlag.AlignCenter)

        # Message
        self.message_label = QLabel(message)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setFont(QFont("Microsoft YaHei UI", 11))
        self.message_label.setStyleSheet("color: #E4E4EF;")
        layout.addWidget(self.message_label)

        # Center the dialog
        if parent:
            parent_rect = parent.geometry()
            x = parent_rect.x() + (parent_rect.width() - 320) // 2
            y = parent_rect.y() + (parent_rect.height() - 140) // 2
            self.move(x, y)

    def paintEvent(self, event):
        """Draw rounded semi-transparent background."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(30, 30, 46, 230))
        painter.setPen(QPen(QColor("#3E3E52"), 1))
        painter.drawRoundedRect(self.rect(), 16, 16)
        painter.end()

    def closeEvent(self, event):
        """Prevent window closing with X button."""
        event.ignore()

    def update_message(self, message):
        """Update the displayed message."""
        self.message_label.setText(message)

