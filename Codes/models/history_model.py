"""
History model for session history storage.
"""
import os
import json
from datetime import datetime


class HistoryModel:
    """Model for managing session history."""

    def __init__(self, history_dir="history"):
        """
        Initialize the history model.

        Args:
            history_dir (str): Directory for storing history files.
        """
        self.history_dir = history_dir
        os.makedirs(history_dir, exist_ok=True)
        self.history_file = os.path.join(history_dir, "sessions.json")
        self.sessions = self.load_sessions()

    def load_sessions(self):
        """
        Load sessions from file.

        Returns:
            list: List of session dictionaries.
        """
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as file:
                    return json.load(file)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def save_sessions(self):
        """Save sessions to file."""
        try:
            with open(self.history_file, "w", encoding="utf-8") as file:
                json.dump(self.sessions, file, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving history: {e}")

    def add_session(self, rule_file, url, fill_count, status="completed",
                    parsed_questions=None, rules=None):
        """
        Add a new session to history.

        Args:
            rule_file (str): Name of the rule file used.
            url (str): Survey URL.
            fill_count (int): Number of forms filled.
            status (str): Session status (completed, stopped, error).
            parsed_questions (list): Parsed question dicts from survey analysis.
            rules (list): Rule dicts with configured probabilities.

        Returns:
            str: Session ID (timestamp).
        """
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        session = {
            "id": session_id,
            "timestamp": datetime.now().isoformat(),
            "rule_file": rule_file,
            "url": url,
            "fill_count": fill_count,
            "status": status,
            "logs": [],
            "parsed_questions": parsed_questions,
            "rules": rules,
        }
        self.sessions.insert(0, session)  # Add to beginning
        self.save_sessions()
        return session_id

    def get_sessions(self):
        """
        Get all sessions.

        Returns:
            list: List of session dictionaries.
        """
        return self.sessions

    def get_session(self, session_id):
        """
        Get a specific session by ID.

        Args:
            session_id (str): Session ID.

        Returns:
            dict or None: Session dictionary or None if not found.
        """
        for session in self.sessions:
            if session["id"] == session_id:
                return session
        return None

    def add_log_to_session(self, session_id, log_message):
        """
        Add a log message to a session.

        Args:
            session_id (str): Session ID.
            log_message (str): Log message with timestamp.
        """
        session = self.get_session(session_id)
        if session:
            session["logs"].append(log_message)
            self.save_sessions()

    def update_session_status(self, session_id, status):
        """
        Update the status of a session.

        Args:
            session_id (str): Session ID.
            status (str): New status.
        """
        session = self.get_session(session_id)
        if session:
            session["status"] = status
            self.save_sessions()

    def clear_history(self):
        """Clear all session history."""
        self.sessions = []
        self.save_sessions()

    def delete_session(self, session_id):
        """
        Delete a specific session.

        Args:
            session_id (str): Session ID to delete.
        """
        self.sessions = [s for s in self.sessions if s["id"] != session_id]
        self.save_sessions()

    def export_session_logs(self, session_id, file_path):
        """
        Export session logs to a text file.

        Args:
            session_id (str): Session ID.
            file_path (str): Path to save the log file.

        Returns:
            bool: True if successful, False otherwise.
        """
        session = self.get_session(session_id)
        if not session:
            return False

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"Session: {session_id}\n")
                f.write(f"Timestamp: {session['timestamp']}\n")
                f.write(f"Rule File: {session['rule_file']}\n")
                f.write(f"URL: {session['url']}\n")
                f.write(f"Fill Count: {session['fill_count']}\n")
                f.write(f"Status: {session['status']}\n")
                f.write("=" * 50 + "\n")
                f.write("Logs:\n")
                for log in session.get("logs", []):
                    f.write(f"{log}\n")
            return True
        except IOError:
            return False
