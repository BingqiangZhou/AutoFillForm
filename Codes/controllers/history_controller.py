"""
History controller - session history management.
Migrated to PyQt6.
"""
from PyQt6.QtWidgets import QMessageBox
from datetime import datetime


class HistoryController:
    """Controller for history management operations."""

    def __init__(self, model, view, history_model):
        """
        Initialize the history controller.

        Args:
            model: SurveyModel instance.
            view: HistoryView instance.
            history_model: HistoryModel instance.
        """
        self.model = model
        self.view = view
        self.history_model = history_model

        # Setup view callbacks
        self.setup_view_callbacks()

        # Connect selection event
        self.view.tree.itemSelectionChanged.connect(self.on_selection_changed)

        # Load initial history
        self.refresh_history()

    def setup_view_callbacks(self):
        """Set up view button callbacks."""
        self.view.set_button_command("refresh", self.refresh_history)
        self.view.set_button_command("export", self.export_selected)
        self.view.set_button_command("clear", self.clear_all_history)
        self.view.set_button_command("view_logs", self.view_selected_logs)

    def refresh_history(self):
        """Refresh the history display."""
        self.view.clear_history()
        sessions = self.history_model.get_sessions()

        for session in sessions:
            self.view.add_session(
                session['id'],
                session['timestamp'],
                session['rule_file'],
                session['url'],
                session['fill_count'],
                session['status']
            )

        self.view.set_status(f"已加载 {len(sessions)} 条记录")

    def on_selection_changed(self):
        """Handle selection change in history list."""
        session_id = self.view.get_selected_session_id()
        if session_id:
            session = self.history_model.get_session(session_id)
            if session:
                self.view.display_logs(session.get('logs', []))

    def view_selected_logs(self):
        """View logs for the selected session."""
        session_id = self.view.get_selected_session_id()
        if not session_id:
            QMessageBox.information(self.view, "提示", "请先选择一个会话")
            return

        session = self.history_model.get_session(session_id)
        if session:
            self.view.display_logs(session.get('logs', []))

    def export_selected(self):
        """Export the selected session's logs."""
        session_id = self.view.get_selected_session_id()
        if not session_id:
            QMessageBox.information(self.view, "提示", "请先选择一个会话")
            return

        file_path = self.view.ask_to_export()
        if file_path:
            success = self.history_model.export_session_logs(session_id, file_path)
            if success:
                self.view.show_info("导出成功", f"日志已保存到:\n{file_path}")
            else:
                self.view.show_error("导出失败", "保存文件时出错")

    def clear_all_history(self):
        """Clear all history."""
        if self.view.ask_to_confirm_clear():
            self.history_model.clear_history()
            self.view.clear_history()
            self.view.clear_logs()
            self.view.set_status("历史记录已清空")

    def add_session(self, rule_file, url, fill_count, status="completed"):
        """Add a new session (called by fill_controller)."""
        return self.history_model.add_session(rule_file, url, fill_count, status)

    def add_log_to_session(self, session_id, log_message):
        """Add a log message to a session (called by fill_controller)."""
        self.history_model.add_log_to_session(session_id, log_message)

    def update_session_status(self, session_id, status):
        """Update session status (called by fill_controller)."""
        self.history_model.update_session_status(session_id, status)
        # Refresh history display
        self.refresh_history()

    def has_unsaved_changes(self):
        """Return False - history controller doesn't have persistent state."""
        return False
