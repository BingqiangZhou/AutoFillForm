"""
Survey analysis view - V3 features enhanced.
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox


class AnalyzeView:
    """View for the survey analysis tab."""

    def __init__(self, parent_frame, initial_link=""):
        """
        Initialize the analyze view.

        Args:
            parent_frame: Parent frame to contain this view.
            initial_link (str): Initial survey link.
        """
        self.frame = parent_frame
        self.setup_ui(initial_link)

    def setup_ui(self, initial_link):
        """Set up the UI components."""
        # Input frame
        input_frame = ttk.LabelFrame(self.frame, text="问卷链接", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        self.link_label = ttk.Label(input_frame, text="链接:")
        self.link_label.pack(side=tk.LEFT)

        self.link_entry = ttk.Entry(input_frame, width=60)
        self.link_entry.pack(side=tk.LEFT, padx=5)
        self.link_entry.insert(0, initial_link)

        self.analyze_button = ttk.Button(input_frame, text="分析问卷")
        self.analyze_button.pack(side=tk.LEFT, padx=5)

        # Toolbar
        toolbar_frame = ttk.Frame(self.frame)
        toolbar_frame.pack(fill=tk.X, padx=10, pady=(0, 5))

        self.export_text_button = ttk.Button(toolbar_frame, text="导出文本", width=12)
        self.export_text_button.pack(side=tk.LEFT, padx=2)

        self.export_yaml_button = ttk.Button(toolbar_frame, text="导出为YAML模板", width=15)
        self.export_yaml_button.pack(side=tk.LEFT, padx=2)

        self.clear_button = ttk.Button(toolbar_frame, text="清空", width=10)
        self.clear_button.pack(side=tk.LEFT, padx=2)

        # Results frame
        results_frame = ttk.LabelFrame(self.frame, text="分析结果", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.result_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            font=("Consolas", 10)
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)

    def set_analyze_command(self, command):
        """Set the command for the analyze button."""
        self.analyze_button.config(command=command)

    def set_export_text_command(self, command):
        """Set the command for the export text button."""
        self.export_text_button.config(command=command)

    def set_export_yaml_command(self, command):
        """Set the command for the export YAML button."""
        self.export_yaml_button.config(command=command)

    def set_clear_command(self, command):
        """Set the command for the clear button."""
        self.clear_button.config(command=command)

    def get_survey_link(self):
        """Get the survey link from the entry."""
        return self.link_entry.get().strip()

    def set_survey_link(self, link):
        """Set the survey link in the entry."""
        self.link_entry.delete(0, tk.END)
        self.link_entry.insert(0, link)

    def display_results(self, results):
        """Display analysis results in the text area."""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, results)

    def get_results(self):
        """Get the current results text."""
        return self.result_text.get(1.0, tk.END).strip()

    def clear_results(self):
        """Clear the results text area."""
        self.result_text.delete(1.0, tk.END)

    def show_info(self, title, message):
        """Show an info dialog."""
        messagebox.showinfo(title, message)

    def show_error(self, title, message):
        """Show an error dialog."""
        messagebox.showerror(title, message)

    def ask_to_save_text(self):
        """Show file dialog for saving text results."""
        return filedialog.asksaveasfilename(
            title="导出分析结果",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

    def ask_to_save_yaml(self):
        """Show file dialog for saving YAML template."""
        return filedialog.asksaveasfilename(
            title="导出YAML模板",
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")]
        )
