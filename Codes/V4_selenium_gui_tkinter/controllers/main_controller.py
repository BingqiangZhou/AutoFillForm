"""
Main controller - coordinates between views and sub-controllers.
"""
import tkinter as tk
from tkinter import messagebox


class MainController:
    """Main controller that coordinates all sub-controllers."""

    def __init__(self, root, models, views, controllers):
        """
        Initialize the main controller.

        Args:
            root: Tkinter root window.
            models: Dictionary of model instances.
            views: Dictionary of view instances.
            controllers: Dictionary of controller instances.
        """
        self.root = root
        self.models = models
        self.views = views
        self.controllers = controllers

        self.setup_menu_handlers()
        self.setup_window_handlers()

    def setup_menu_handlers(self):
        """Set up menu bar handlers."""
        # Get main view's menu
        main_view = self.views['main']
        menubar = self.root.nametowidget(self.root.nametowidget(self.root)['menu'])

        # File menu handlers
        def select_rule():
            self.controllers['rule_editor'].open_file()
            main_view.switch_to_tab(2)  # Switch to rule editor tab

        def new_rule():
            self.controllers['rule_editor'].new_rule()
            main_view.switch_to_tab(2)

        # Tools menu handlers
        def export_history():
            self.controllers['history'].export_selected()

        def clear_history():
            self.controllers['history'].clear_all_history()

        # Help menu handler
        def show_about():
            main_view.show_about()

        # Store handlers for menu (simplified approach)
        self.menu_handlers = {
            'select_rule': select_rule,
            'new_rule': new_rule,
            'export_history': export_history,
            'clear_history': clear_history,
            'about': show_about
        }

        # Configure menu items
        file_menu = menubar.nametowidget(menubar.winfo_children()[0])
        file_menu.entryconfig("选择规则文件", command=select_rule)
        file_menu.entryconfig("新建规则", command=new_rule)

        tools_menu = menubar.nametowidget(menubar.winfo_children()[1])
        tools_menu.entryconfig("导出历史", command=export_history)
        tools_menu.entryconfig("清空历史", command=clear_history)

        help_menu = menubar.nametowidget(menubar.winfo_children()[2])
        help_menu.entryconfig("关于", command=show_about)

    def setup_window_handlers(self):
        """Set up window event handlers."""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Handle window closing event."""
        # Check for unsaved changes in rule editor
        if self.controllers['rule_editor'].has_unsaved_changes():
            if not messagebox.askyesno(
                "退出确认",
                "规则编辑器有未保存的更改，确定要退出吗？"
            ):
                return

        # Stop any running fills
        if self.controllers['fill'].check_is_running():
            if not messagebox.askyesno(
                "退出确认",
                "填写任务正在运行，确定要退出吗？"
            ):
                return
            self.controllers['fill'].stop_fill()

        # Save configuration
        self.models['survey'].save_config_to_file()

        self.root.destroy()

    def get_controller(self, name):
        """Get a sub-controller by name."""
        return self.controllers.get(name)

    def get_model(self, name):
        """Get a model by name."""
        return self.models.get(name)

    def get_view(self, name):
        """Get a view by name."""
        return self.views.get(name)

    def set_status(self, message):
        """Set the main window status bar."""
        self.views['main'].set_status(message)

    def switch_to_tab(self, tab_index):
        """Switch to a specific tab."""
        self.views['main'].switch_to_tab(tab_index)
