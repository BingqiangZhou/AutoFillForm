"""
Form filling view - V2 features in GUI.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext


class FillView:
    """View for the form filling tab."""

    def __init__(self, parent_frame):
        """
        Initialize the fill view.

        Args:
            parent_frame: Parent frame to contain this view.
        """
        self.frame = parent_frame
        self.setup_ui()

    def setup_ui(self):
        """Set up the UI components."""
        # Top frame for configuration
        config_frame = ttk.LabelFrame(self.frame, text="配置", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=10)

        # Rule file selection
        rule_frame = ttk.Frame(config_frame)
        rule_frame.pack(fill=tk.X, pady=5)

        ttk.Label(rule_frame, text="规则文件:").pack(side=tk.LEFT)
        self.rule_file_var = tk.StringVar()
        self.rule_entry = ttk.Entry(rule_frame, textvariable=self.rule_file_var, state="readonly")
        self.rule_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.browse_button = ttk.Button(rule_frame, text="浏览...")
        self.browse_button.pack(side=tk.LEFT)

        # Fill count
        count_frame = ttk.Frame(config_frame)
        count_frame.pack(fill=tk.X, pady=5)

        ttk.Label(count_frame, text="填写数量:").pack(side=tk.LEFT)
        self.fill_count_var = tk.IntVar(value=1)
        self.count_spinbox = ttk.Spinbox(
            count_frame,
            from_=1,
            to=1000,
            textvariable=self.fill_count_var,
            width=10
        )
        self.count_spinbox.pack(side=tk.LEFT, padx=5)

        # URL display
        url_frame = ttk.Frame(config_frame)
        url_frame.pack(fill=tk.X, pady=5)

        ttk.Label(url_frame, text="问卷链接:").pack(side=tk.LEFT)
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, state="readonly")
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Control frame
        control_frame = ttk.LabelFrame(self.frame, text="控制", padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        button_frame = ttk.Frame(control_frame)
        button_frame.pack()

        self.start_button = ttk.Button(button_frame, text="开始填写")
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(button_frame, text="停止", state="disabled")
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Progress frame
        progress_frame = ttk.LabelFrame(self.frame, text="进度", padding=10)
        progress_frame.pack(fill=tk.X, padx=10, pady=5)

        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            length=400
        )
        self.progress_bar.pack(pady=5)

        # Status label
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        self.status_label.pack()

        # Log display
        log_frame = ttk.LabelFrame(self.frame, text="日志", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            state="disabled",
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def set_browse_command(self, command):
        """Set the command for the browse button."""
        self.browse_button.config(command=command)

    def set_start_command(self, command):
        """Set the command for the start button."""
        self.start_button.config(command=command)

    def set_stop_command(self, command):
        """Set the command for the stop button."""
        self.stop_button.config(command=command)

    def get_rule_file(self):
        """Get the current rule file path."""
        return self.rule_file_var.get()

    def set_rule_file(self, file_path):
        """Set the rule file path."""
        self.rule_file_var.set(file_path)

    def get_url(self):
        """Get the URL."""
        return self.url_var.get()

    def set_url(self, url):
        """Set the URL."""
        self.url_var.set(url)

    def get_fill_count(self):
        """Get the fill count."""
        return self.fill_count_var.get()

    def set_fill_count(self, count):
        """Set the fill count."""
        self.fill_count_var.set(count)

    def set_progress(self, value):
        """Set the progress bar value (0-100)."""
        self.progress_var.set(value)

    def set_status(self, status):
        """Set the status text."""
        self.status_var.set(status)

    def append_log(self, message):
        """Append a log message to the log display."""
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def clear_log(self):
        """Clear the log display."""
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")

    def set_running_state(self, is_running):
        """Enable/disable buttons based on running state."""
        if is_running:
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.browse_button.config(state="disabled")
        else:
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
            self.browse_button.config(state="normal")

    def show_info(self, title, message):
        """Show an info dialog."""
        messagebox.showinfo(title, message)

    def show_error(self, title, message):
        """Show an error dialog."""
        messagebox.showerror(title, message)

    def ask_to_browse_rule_file(self, initial_dir):
        """Show file dialog for selecting rule file."""
        return filedialog.askopenfilename(
            title="选择规则文件",
            initialdir=initial_dir,
            filetypes=[("YAML files", "*.yaml *.yml"), ("All files", "*.*")]
        )
