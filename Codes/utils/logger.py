"""
Custom logger with GUI callback support.
"""
import logging
from datetime import datetime
import os


class GuiLogger:
    """Logger that supports both file/console logging and GUI callbacks."""

    def __init__(self, name="AutoFillForm", log_dir="history", gui_callback=None):
        """
        Initialize the GUI logger.

        Args:
            name (str): Logger name.
            log_dir (str): Directory for log files.
            gui_callback (callable): Optional callback for GUI updates.
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        self.logger.handlers.clear()  # Clear existing handlers

        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)

        # Create log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = os.path.join(log_dir, f"app_{timestamp}.log")

        # File handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)

        # GUI callback
        self.gui_callback = gui_callback

        # Log buffer for session replay
        self.log_buffer = []

    def _log(self, level, message):
        """Internal log method."""
        # Log to file and console
        if level == "INFO":
            self.logger.info(message)
        elif level == "WARNING":
            self.logger.warning(message)
        elif level == "ERROR":
            self.logger.error(message)
        elif level == "DEBUG":
            self.logger.debug(message)

        # Add to buffer
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {message}"
        self.log_buffer.append(formatted_msg)

        # Call GUI callback if available
        if self.gui_callback:
            self.gui_callback(formatted_msg)

    def info(self, message):
        """Log an info message."""
        self._log("INFO", message)

    def warning(self, message):
        """Log a warning message."""
        self._log("WARNING", message)

    def error(self, message):
        """Log an error message."""
        self._log("ERROR", message)

    def debug(self, message):
        """Log a debug message."""
        self._log("DEBUG", message)

    def set_gui_callback(self, callback):
        """Set or update the GUI callback."""
        self.gui_callback = callback

    def get_logs(self):
        """Get all logged messages."""
        return self.log_buffer

    def clear_buffer(self):
        """Clear the log buffer."""
        self.log_buffer = []

    def save_session_logs(self, session_id, history_model):
        """
        Save all buffered logs to a session in history.

        Args:
            session_id (str): Session ID.
            history_model: HistoryModel instance.
        """
        for log in self.log_buffer:
            history_model.add_log_to_session(session_id, log)

    def get_log_file_path(self):
        """Get the current log file path."""
        for handler in self.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                return handler.baseFilename
        return None
