"""
History and logs view - Migrated to PySide6.
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QTextEdit, QFileDialog, QMessageBox,
                              QGroupBox, QTreeWidget, QTreeWidgetItem,
                              QAbstractItemView, QHeaderView)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class HistoryView(QWidget):
    """View for the history and logs tab using PySide6."""

    def __init__(self, parent_widget):
        """
        Initialize the history view.

        Args:
            parent_widget: Parent widget to contain this view.
        """
        super().__init__(parent_widget)

        # Ensure this widget fills the parent tab page
        parent_layout = QVBoxLayout(parent_widget)
        parent_layout.setContentsMargins(0, 0, 0, 0)
        parent_layout.addWidget(self)

        self.setup_ui()

    def setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Toolbar
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(0, 0, 0, 5)

        self.refresh_button = QPushButton("刷新")
        self.refresh_button.setFixedWidth(80)
        toolbar_layout.addWidget(self.refresh_button)

        self.export_button = QPushButton("导出选中")
        self.export_button.setFixedWidth(80)
        toolbar_layout.addWidget(self.export_button)

        self.clear_button = QPushButton("清空历史")
        self.clear_button.setFixedWidth(80)
        toolbar_layout.addWidget(self.clear_button)

        toolbar_layout.addSpacing(20)

        self.view_logs_button = QPushButton("查看日志")
        self.view_logs_button.setFixedWidth(80)
        toolbar_layout.addWidget(self.view_logs_button)

        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)

        # History list
        history_group = QGroupBox("会话历史")
        history_layout = QVBoxLayout(history_group)

        # TreeWidget for history
        self.tree = QTreeWidget()
        self.tree.setColumnCount(6)
        self.tree.setHeaderLabels(["时间", "规则文件", "URL", "填写数量", "状态", "操作"])
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tree.setAlternatingRowColors(True)

        # Set column widths
        header = self.tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.tree.setColumnWidth(5, 120)

        self._restore_command = None

        self.tree.itemSelectionChanged.connect(self.on_selection_changed)
        history_layout.addWidget(self.tree)

        layout.addWidget(history_group, 1)

        # Log viewer frame
        log_group = QGroupBox("日志详情")
        log_layout = QVBoxLayout(log_group)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        font = QFont("Consolas", 9)
        self.log_text.setFont(font)
        log_layout.addWidget(self.log_text)

        layout.addWidget(log_group, 1)

    def set_button_command(self, button_name, command):
        """Set command for a toolbar button."""
        button_map = {
            "refresh": self.refresh_button,
            "export": self.export_button,
            "clear": self.clear_button,
            "view_logs": self.view_logs_button,
        }
        if button_name in button_map:
            button_map[button_name].clicked.connect(command)

    def clear_history(self):
        """Clear all history items from the tree."""
        self.tree.clear()

    def add_session(self, session_id, timestamp, rule_file, url, fill_count, status):
        """
        Add a session to the history list.

        Args:
            session_id (str): Session ID.
            timestamp (str): ISO format timestamp.
            rule_file (str): Rule file name.
            url (str): Survey URL.
            fill_count (int): Number of forms filled.
            status (str): Session status.
        """
        # Format timestamp for display
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(timestamp)
            display_time = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            display_time = timestamp

        # Truncate URL if too long
        display_url = url if len(url) <= 40 else url[:37] + "..."

        # Create tree item
        item = QTreeWidgetItem(self.tree)
        item.setText(0, display_time)
        item.setText(1, rule_file)
        item.setText(2, display_url)
        item.setText(3, str(fill_count))
        item.setText(4, status)

        # Store session_id as data
        item.setData(0, Qt.ItemDataRole.UserRole, session_id)

        # Add restore button in the "操作" column, centered with fixed width
        container = QWidget()
        btn_layout = QHBoxLayout(container)
        btn_layout.setContentsMargins(4, 2, 4, 2)
        restore_btn = QPushButton("继续填写问卷")
        restore_btn.setFixedWidth(100)
        restore_btn.clicked.connect(lambda checked, sid=session_id: self._on_restore_clicked(sid))
        btn_layout.addWidget(restore_btn, 0, Qt.AlignmentFlag.AlignCenter)
        self.tree.setItemWidget(item, 5, container)

    def get_selected_session_id(self):
        """Get the selected session ID."""
        selected_items = self.tree.selectedItems()
        if selected_items:
            return selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        return None

    def display_logs(self, logs):
        """Display logs in the log viewer."""
        self.log_text.clear()
        for log in logs:
            self.log_text.append(log)

    def clear_logs(self):
        """Clear the log viewer."""
        self.log_text.clear()

    def set_restore_command(self, command):
        """Set the callback for per-row restore buttons.

        Args:
            command: Function that accepts a session_id string.
        """
        self._restore_command = command

    def _on_restore_clicked(self, session_id):
        """Handle a per-row restore button click."""
        if self._restore_command:
            self._restore_command(session_id)

    def on_selection_changed(self):
        """Handle selection change event - to be connected to controller."""
        pass

    def show_info(self, title, message):
        """Show an info dialog."""
        QMessageBox.information(self, title, message)

    def show_error(self, title, message):
        """Show an error dialog."""
        QMessageBox.critical(self, title, message)

    def ask_to_confirm_clear(self):
        """Ask user to confirm clearing history."""
        reply = QMessageBox.question(
            self,
            "确认清空",
            "确定要清空所有历史记录吗？此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes

    def ask_to_export(self):
        """Show file dialog for exporting logs."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出日志",
            "",
            "Text files (*.txt);;All files (*.*)"
        )
        return file_path

    def get_session_count(self):
        """Get the number of sessions in the history."""
        return self.tree.topLevelItemCount()

    def set_status(self, message):
        """Set the status bar message (for controller compatibility)."""
        # Status is handled by the main window's status bar
        pass
