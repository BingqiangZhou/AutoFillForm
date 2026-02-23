"""
YAML rule editor view.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class RuleEditorView:
    """View for the YAML rule editor tab."""

    def __init__(self, parent_frame):
        """
        Initialize the rule editor view.

        Args:
            parent_frame: Parent frame to contain this view.
        """
        self.frame = parent_frame
        self._current_file = None
        self._modified = False
        self.setup_ui()

    @property
    def current_file(self):
        """Get the current file path."""
        return self._current_file

    @property
    def modified(self):
        """Get the modified flag."""
        return self._modified

    def setup_ui(self):
        """Set up the UI components."""
        # Top toolbar
        toolbar_frame = ttk.Frame(self.frame)
        toolbar_frame.pack(fill=tk.X, padx=5, pady=5)

        self.new_button = ttk.Button(toolbar_frame, text="新建", width=10)
        self.new_button.pack(side=tk.LEFT, padx=2)

        self.open_button = ttk.Button(toolbar_frame, text="打开", width=10)
        self.open_button.pack(side=tk.LEFT, padx=2)

        self.save_button = ttk.Button(toolbar_frame, text="保存", width=10)
        self.save_button.pack(side=tk.LEFT, padx=2)

        self.save_as_button = ttk.Button(toolbar_frame, text="另存为", width=10)
        self.save_as_button.pack(side=tk.LEFT, padx=2)

        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)

        self.validate_button = ttk.Button(toolbar_frame, text="验证语法", width=10)
        self.validate_button.pack(side=tk.LEFT, padx=2)

        self.template_button = ttk.Button(toolbar_frame, text="从模板新建", width=12)
        self.template_button.pack(side=tk.LEFT, padx=2)

        # File info
        info_frame = ttk.Frame(self.frame)
        info_frame.pack(fill=tk.X, padx=5, pady=(0, 5))

        self.file_label = ttk.Label(info_frame, text="未打开文件", anchor=tk.W)
        self.file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.modified_label = ttk.Label(info_frame, text="", foreground="red")
        self.modified_label.pack(side=tk.RIGHT)

        # Text editor with line numbers
        editor_frame = ttk.Frame(self.frame)
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Line numbers
        self.line_numbers = tk.Text(
            editor_frame,
            width=4,
            padx=3,
            pady=3,
            state="disabled",
            bg="#f0f0f0",
            relief=tk.FLAT
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Main editor
        self.editor = tk.Text(
            editor_frame,
            wrap=tk.NONE,
            padx=5,
            pady=5,
            font=("Consolas", 10),
            tabstyle="wordprocessor"
        )
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(editor_frame, orient=tk.VERTICAL, command=self.on_vscroll)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        h_scrollbar = ttk.Scrollbar(self.frame, orient=tk.HORIZONTAL, command=self.editor.xview)
        h_scrollbar.pack(fill=tk.X, padx=5, pady=(0, 5))

        self.editor.config(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Status bar
        self.status_var = tk.StringVar(value="就绪")
        self.status_bar = ttk.Label(
            self.frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X, padx=5, pady=(0, 5))

        # Configure text highlighting
        self.configure_highlighting()

        # Bind events
        self.editor.bind("<<Modified>>", self.on_modified)
        self.editor.bind("<KeyRelease>", self.on_key_release)
        self.editor.bind("<MouseWheel>", self.on_vscroll)  # Windows

    def configure_highlighting(self):
        """Configure syntax highlighting for YAML."""
        self.editor.tag_config("key", foreground="#0000ff")  # Blue
        self.editor.tag_config("value", foreground="#008000")  # Green
        self.editor.tag_config("comment", foreground="#808080")  # Gray
        self.editor.tag_config("error", background="#ffcccc")  # Light red

    def set_button_command(self, button_name, command):
        """Set command for a toolbar button."""
        button_map = {
            "new": self.new_button,
            "open": self.open_button,
            "save": self.save_button,
            "save_as": self.save_as_button,
            "validate": self.validate_button,
            "template": self.template_button
        }
        if button_name in button_map:
            button_map[button_name].config(command=command)

    def on_modified(self, event=None):
        """Handle modified flag."""
        if self.editor.edit_modified():
            self._modified = True
            self.modified_label.config(text="*")
            self.editor.edit_modified(False)

    def on_key_release(self, event=None):
        """Update line numbers on key release."""
        self.update_line_numbers()

    def on_vscroll(self, *args):
        """Handle vertical scroll."""
        self.editor.yview(*args)
        self.line_numbers.yview(*args)

    def update_line_numbers(self):
        """Update the line numbers display."""
        lines = int(self.editor.index("end-1c").split(".")[0])
        line_numbers_text = "\n".join(str(i) for i in range(1, lines + 1))

        self.line_numbers.config(state="normal")
        self.line_numbers.delete(1.0, tk.END)
        self.line_numbers.insert(1.0, line_numbers_text)
        self.line_numbers.config(state="disabled")

    def get_content(self):
        """Get the editor content."""
        return self.editor.get(1.0, tk.END).strip()

    def set_content(self, content):
        """Set the editor content."""
        self.editor.delete(1.0, tk.END)
        self.editor.insert(1.0, content)
        self.update_line_numbers()
        self._modified = False
        self.modified_label.config(text="")

    def new_file(self):
        """Create a new file."""
        if self._modified and not self.confirm_discard():
            return False
        self.editor.delete(1.0, tk.END)
        self._current_file = None
        self._modified = False
        self.modified_label.config(text="")
        self.file_label.config(text="未打开文件")
        self.update_line_numbers()
        return True

    def open_file(self, file_path=None):
        """Open a file."""
        if not file_path:
            file_path = filedialog.askopenfilename(
                title="打开规则文件",
                filetypes=[("YAML files", "*.yaml *.yml"), ("All files", "*.*")]
            )
            if not file_path:
                return False

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.set_content(content)
            self._current_file = file_path
            self._modified = False
            self.modified_label.config(text="")
            self.file_label.config(text=file_path)
            return True
        except Exception as e:
            messagebox.showerror("打开文件错误", f"无法打开文件:\n{e}")
            return False

    def save_file(self, file_path=None):
        """Save the current file."""
        if not file_path:
            if self.current_file:
                file_path = self.current_file
            else:
                file_path = filedialog.asksaveasfilename(
                    title="保存规则文件",
                    defaultextension=".yaml",
                    filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")]
                )
                if not file_path:
                    return False

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.get_content())
            self._current_file = file_path
            self._modified = False
            self.modified_label.config(text="")
            self.file_label.config(text=file_path)
            return True
        except Exception as e:
            messagebox.showerror("保存文件错误", f"无法保存文件:\n{e}")
            return False

    def confirm_discard(self):
        """Ask user to confirm discarding changes."""
        return messagebox.askyesno(
            "未保存的更改",
            "当前文件有未保存的更改，是否继续？"
        )

    def highlight_error(self, line_number):
        """Highlight an error line."""
        start = f"{line_number}.0"
        end = f"{line_number}.end"
        self.editor.tag_add("error", start, end)

    def clear_error_highlighting(self):
        """Clear all error highlights."""
        self.editor.tag_remove("error", 1.0, tk.END)

    def set_status(self, message):
        """Set the status bar message."""
        self.status_var.set(message)

    def show_validation_result(self, is_valid, message):
        """Show validation result in status bar."""
        if is_valid:
            self.set_status("验证通过 - " + message)
            messagebox.showinfo("验证结果", "YAML语法正确！")
        else:
            self.set_status("验证失败 - " + message)
            messagebox.showerror("验证结果", f"YAML语法错误:\n{message}")
