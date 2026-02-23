"""
Form filling view - Migrated to PyQt6 with thread-safe signals.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QSpinBox, QPushButton, QProgressBar,
                             QTextEdit, QFileDialog, QMessageBox, QGroupBox)
from PyQt6.QtCore import pyqtSignal, QObject, QMutex, QMutexLocker


class FillViewSignals(QObject):
    """Signals for thread-safe updates from worker thread."""

    log_append = pyqtSignal(str)
    progress_update = pyqtSignal(int)
    status_update = pyqtSignal(str)
    running_state_changed = pyqtSignal(bool)


class FillView(QWidget):
    """View for the form filling tab using PyQt6."""

    def __init__(self, parent_widget):
        """
        Initialize the fill view.

        Args:
            parent_widget: Parent widget to contain this view.
        """
        super().__init__(parent_widget)

        # Ensure this widget fills the parent tab page
        parent_layout = QVBoxLayout(parent_widget)
        parent_layout.setContentsMargins(0, 0, 0, 0)
        parent_layout.addWidget(self)

        self.signals = FillViewSignals()
        self.setup_ui()

        # Thread-safe state
        self._mutex = QMutex()
        self._running_state = False

    def setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Top frame for configuration
        config_group = QGroupBox("配置")
        config_layout = QVBoxLayout(config_group)

        # Rule file selection
        rule_layout = QHBoxLayout()
        rule_layout.addWidget(QLabel("规则文件:"))
        self.rule_edit = QLineEdit()
        self.rule_edit.setReadOnly(True)
        rule_layout.addWidget(self.rule_edit)
        self.browse_button = QPushButton("浏览...")
        rule_layout.addWidget(self.browse_button)
        config_layout.addLayout(rule_layout)

        # Fill count
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("填写数量:"))
        self.count_spinbox = QSpinBox()
        self.count_spinbox.setRange(1, 1000)
        self.count_spinbox.setValue(1)
        count_layout.addWidget(self.count_spinbox)
        count_layout.addStretch()
        config_layout.addLayout(count_layout)

        # URL display
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("问卷链接:"))
        self.url_edit = QLineEdit()
        self.url_edit.setReadOnly(True)
        url_layout.addWidget(self.url_edit)
        config_layout.addLayout(url_layout)

        layout.addWidget(config_group)

        # Control frame
        control_group = QGroupBox("控制")
        control_layout = QHBoxLayout(control_group)
        control_layout.addStretch()

        self.start_button = QPushButton("开始填写")
        control_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("停止")
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.stop_button)

        control_layout.addStretch()
        layout.addWidget(control_group)

        # Progress frame
        progress_group = QGroupBox("进度")
        progress_layout = QVBoxLayout(progress_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("就绪")
        progress_layout.addWidget(self.status_label)

        layout.addWidget(progress_group)

        # Log display
        log_group = QGroupBox("日志")
        log_layout = QVBoxLayout(log_group)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(200)
        log_layout.addWidget(self.log_text)

        layout.addWidget(log_group, 1)

        # Connect signals to slots for thread-safe updates
        self.signals.log_append.connect(self._append_log_slot)
        self.signals.progress_update.connect(self._set_progress_slot)
        self.signals.status_update.connect(self._set_status_slot)
        self.signals.running_state_changed.connect(self._set_running_state_slot)

    def set_browse_command(self, command):
        """Set the command for the browse button."""
        self.browse_button.clicked.connect(command)

    def set_start_command(self, command):
        """Set the command for the start button."""
        self.start_button.clicked.connect(command)

    def set_stop_command(self, command):
        """Set the command for the stop button."""
        self.stop_button.clicked.connect(command)

    def get_rule_file(self):
        """Get the current rule file path."""
        return self.rule_edit.text()

    def set_rule_file(self, file_path):
        """Set the rule file path."""
        self.rule_edit.setText(file_path)

    def get_url(self):
        """Get the URL."""
        return self.url_edit.text()

    def set_url(self, url):
        """Set the URL."""
        self.url_edit.setText(url)

    def get_fill_count(self):
        """Get the fill count."""
        return self.count_spinbox.value()

    def set_fill_count(self, count):
        """Set the fill count."""
        self.count_spinbox.setValue(count)

    # Thread-safe update methods using signals
    def set_progress(self, value):
        """Set the progress bar value (0-100) - thread-safe via signal."""
        self.signals.progress_update.emit(value)

    def _set_progress_slot(self, value):
        """Slot for progress update (runs in GUI thread)."""
        self.progress_bar.setValue(value)

    def set_status(self, status):
        """Set the status text - thread-safe via signal."""
        self.signals.status_update.emit(status)

    def _set_status_slot(self, status):
        """Slot for status update (runs in GUI thread)."""
        self.status_label.setText(status)

    def append_log(self, message):
        """Append a log message - thread-safe via signal."""
        self.signals.log_append.emit(message)

    def _append_log_slot(self, message):
        """Slot for log append (runs in GUI thread)."""
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(message + "\n")
        self.log_text.setTextCursor(cursor)
        self.log_text.ensureCursorVisible()

    def clear_log(self):
        """Clear the log display."""
        self.log_text.clear()

    def set_running_state(self, is_running):
        """Enable/disable buttons based on running state - thread-safe via signal."""
        self.signals.running_state_changed.emit(is_running)

    def _set_running_state_slot(self, is_running):
        """Slot for running state update (runs in GUI thread)."""
        with QMutexLocker(self._mutex):
            self._running_state = is_running

        if is_running:
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.browse_button.setEnabled(False)
        else:
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.browse_button.setEnabled(True)

    def check_is_running(self):
        """Check if currently running (thread-safe)."""
        with QMutexLocker(self._mutex):
            return self._running_state

    def show_info(self, title, message):
        """Show an info dialog."""
        QMessageBox.information(self, title, message)

    def show_error(self, title, message):
        """Show an error dialog."""
        QMessageBox.critical(self, title, message)

    def ask_to_browse_rule_file(self, initial_dir):
        """Show file dialog for selecting rule file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择规则文件",
            initial_dir,
            "YAML files (*.yaml *.yml);;All files (*.*)"
        )
        return file_path

    # For backward compatibility with controller using after()
    def after(self, ms, callback):
        """Schedule a callback to run after ms milliseconds (for compatibility)."""
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(ms, callback)
