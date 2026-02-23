"""
History and logs view.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext


class HistoryView:
    """View for the history and logs tab."""

    def __init__(self, parent_frame):
        """
        Initialize the history view.

        Args:
            parent_frame: Parent frame to contain this view.
        """
        self.frame = parent_frame
        self.setup_ui()

    def setup_ui(self):
        """Set up the UI components."""
        # Toolbar
        toolbar_frame = ttk.Frame(self.frame)
        toolbar_frame.pack(fill=tk.X, padx=5, pady=5)

        self.refresh_button = ttk.Button(toolbar_frame, text="刷新", width=10)
        self.refresh_button.pack(side=tk.LEFT, padx=2)

        self.export_button = ttk.Button(toolbar_frame, text="导出选中", width=10)
        self.export_button.pack(side=tk.LEFT, padx=2)

        self.clear_button = ttk.Button(toolbar_frame, text="清空历史", width=10)
        self.clear_button.pack(side=tk.LEFT, padx=2)

        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)

        self.view_logs_button = ttk.Button(toolbar_frame, text="查看日志", width=10)
        self.view_logs_button.pack(side=tk.LEFT, padx=2)

        # History list
        history_frame = ttk.LabelFrame(self.frame, text="会话历史", padding=10)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Treeview for history
        columns = ("时间", "规则文件", "URL", "数量", "状态")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=10)

        self.tree.heading("时间", text="时间")
        self.tree.heading("规则文件", text="规则文件")
        self.tree.heading("URL", text="URL")
        self.tree.heading("数量", text="填写数量")
        self.tree.heading("状态", text="状态")

        self.tree.column("时间", width=150)
        self.tree.column("规则文件", width=200)
        self.tree.column("URL", width=250)
        self.tree.column("数量", width=80)
        self.tree.column("状态", width=80)

        # Scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", lambda e: self.on_selection_changed())

        # Log viewer frame
        log_frame = ttk.LabelFrame(self.frame, text="日志详情", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=12,
            state="disabled",
            wrap=tk.WORD,
            font=("Consolas", 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def set_button_command(self, button_name, command):
        """Set command for a toolbar button."""
        button_map = {
            "refresh": self.refresh_button,
            "export": self.export_button,
            "clear": self.clear_button,
            "view_logs": self.view_logs_button
        }
        if button_name in button_map:
            button_map[button_name].config(command=command)

    def clear_history(self):
        """Clear all history items from the tree."""
        for item in self.tree.get_children():
            self.tree.delete(item)

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

        self.tree.insert("", tk.END, iid=session_id, values=(
            display_time,
            rule_file,
            display_url,
            fill_count,
            status
        ))

    def get_selected_session_id(self):
        """Get the selected session ID."""
        selection = self.tree.selection()
        if selection:
            return selection[0]
        return None

    def display_logs(self, logs):
        """Display logs in the log viewer."""
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        for log in logs:
            self.log_text.insert(tk.END, log + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def clear_logs(self):
        """Clear the log viewer."""
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")

    def on_selection_changed(self):
        """Handle selection change event - to be connected to controller."""
        pass

    def show_info(self, title, message):
        """Show an info dialog."""
        messagebox.showinfo(title, message)

    def show_error(self, title, message):
        """Show an error dialog."""
        messagebox.showerror(title, message)

    def ask_to_confirm_clear(self):
        """Ask user to confirm clearing history."""
        return messagebox.askyesno(
            "确认清空",
            "确定要清空所有历史记录吗？此操作不可撤销。"
        )

    def ask_to_export(self):
        """Show file dialog for exporting logs."""
        return filedialog.asksaveasfilename(
            title="导出日志",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

    def get_session_count(self):
        """Get the number of sessions in the history."""
        return len(self.tree.get_children())
