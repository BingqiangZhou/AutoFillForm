"""
Loading window dialog.
Reused from V3.
"""
import tkinter as tk
from tkinter import Toplevel, Label


class LoadingWindow:
    """Modal loading indicator dialog."""

    def __init__(self, parent, message="正在加载，请稍候..."):
        """
        Initialize the loading window.

        Args:
            parent: Parent window.
            message (str): Initial message to display.
        """
        self.parent = parent
        self.window = Toplevel(parent)
        self.window.withdraw()  # Hide initially
        self.window.title("正在执行，请稍候...")
        self.window.protocol("WM_DELETE_WINDOW", self.disable_event)
        self.window.transient(parent)
        self.window.grab_set()

        self.message_label = Label(self.window, text=message)
        self.message_label.pack(pady=10)

        self.loading_label = Label(self.window, text="⏳", font=("Helvetica", 32))
        self.loading_label.pack()

        self.center_window()
        self.window.deiconify()  # Show window

        self.rotate_label()

    def center_window(self):
        """Center the window relative to parent."""
        self.parent.update_idletasks()
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        window_width = 300
        window_height = 100

        pos_x = parent_x + (parent_width // 2) - (window_width // 2)
        pos_y = parent_y + (parent_height // 2) - (window_height // 2)

        self.window.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")

    def disable_event(self):
        """Prevent window closing."""
        pass

    def close(self):
        """Close the loading window."""
        self.window.grab_release()
        self.window.destroy()

    def update_message(self, message):
        """Update the displayed message."""
        self.message_label.config(text=message)

    def rotate_label(self):
        """Rotate the loading icon."""
        current_text = self.loading_label["text"]
        if current_text == "⏳":
            self.loading_label["text"] = "⌛"
        else:
            self.loading_label["text"] = "⏳"
        self.window.after(500, self.rotate_label)
