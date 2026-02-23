"""
Main view with tabbed interface.
"""
import tkinter as tk
from tkinter import ttk, Menu, messagebox


class MainView:
    """Main application window with tabbed interface."""

    def __init__(self, root, title="AutoFillForm V4"):
        """
        Initialize the main view.

        Args:
            root: Tkinter root window.
            title (str): Window title.
        """
        self.root = root
        self.root.title(title)
        self.root.geometry("900x650")

        # Set up menu bar
        self.setup_menu()

        # Create notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create frames for each tab
        self.fill_frame = ttk.Frame(self.notebook)
        self.analyze_frame = ttk.Frame(self.notebook)
        self.rule_editor_frame = ttk.Frame(self.notebook)
        self.history_frame = ttk.Frame(self.notebook)

        # Add tabs to notebook
        self.notebook.add(self.fill_frame, text="问卷填写")
        self.notebook.add(self.analyze_frame, text="问卷分析")
        self.notebook.add(self.rule_editor_frame, text="规则编辑")
        self.notebook.add(self.history_frame, text="历史记录")

        # Status bar
        self.status_bar = tk.Label(
            root,
            text="就绪",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_menu(self):
        """Set up the menu bar."""
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="选择规则文件", command=lambda: self.on_menu_action("select_rule"))
        file_menu.add_command(label="新建规则", command=lambda: self.on_menu_action("new_rule"))
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)

        # Tools menu
        tools_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="导出历史", command=lambda: self.on_menu_action("export_history"))
        tools_menu.add_command(label="清空历史", command=lambda: self.on_menu_action("clear_history"))

        # Help menu
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=lambda: self.on_menu_action("about"))

    def on_menu_action(self, action):
        """Handle menu actions - to be connected to controller."""
        pass  # Controller will set up actual handlers

    def set_menu_handler(self, action, handler):
        """
        Set a handler for a menu action.

        Args:
            action (str): Menu action identifier.
            handler (callable): Handler function.
        """
        if action == "select_rule":
            self.root.nametowidget(self.root.nametowidget(self.root)['menu'])['menu'].file_menu.entryconfig(
                "选择规则文件", command=handler
            )
        # Other handlers will be set similarly

    def set_status(self, message):
        """
        Update the status bar message.

        Args:
            message (str): Status message.
        """
        self.status_bar.config(text=message)

    def get_current_tab(self):
        """Get the currently selected tab index."""
        return self.notebook.index(self.notebook.select())

    def switch_to_tab(self, tab_index):
        """
        Switch to a specific tab.

        Args:
            tab_index (int): Tab index to switch to.
        """
        self.notebook.select(tab_index)

    def get_fill_frame(self):
        """Get the fill tab frame."""
        return self.fill_frame

    def get_analyze_frame(self):
        """Get the analyze tab frame."""
        return self.analyze_frame

    def get_rule_editor_frame(self):
        """Get the rule editor tab frame."""
        return self.rule_editor_frame

    def get_history_frame(self):
        """Get the history tab frame."""
        return self.history_frame

    def show_about(self):
        """Show the about dialog."""
        messagebox.showinfo(
            "关于 AutoFillForm V4",
            "AutoFillForm V4\n\n"
            "自动填写问卷工具\n"
            "结合V2的自动化功能和V3的GUI界面\n\n"
            "功能特性:\n"
            "• YAML规则配置\n"
            "• 多种题型支持 (单选、多选、矩阵、填空)\n"
            "• 智能验证和滑块验证\n"
            "• 问卷分析\n"
            "• 规则编辑器\n"
            "• 历史记录"
        )
