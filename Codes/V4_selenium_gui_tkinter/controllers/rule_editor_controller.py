"""
Rule editor controller - YAML rule editor logic.
"""
from utils.yaml_validator import YamlValidator
from models.rule_model import RuleModel


class RuleEditorController:
    """Controller for rule editor operations."""

    def __init__(self, model, view, rule_model):
        """
        Initialize the rule editor controller.

        Args:
            model: SurveyModel instance.
            view: RuleEditorView instance.
            rule_model: RuleModel instance.
        """
        self.model = model
        self.view = view
        self.rule_model = rule_model

        # Setup view callbacks
        self.setup_view_callbacks()

    def setup_view_callbacks(self):
        """Set up view button callbacks."""
        self.view.set_button_command("new", self.new_rule)
        self.view.set_button_command("open", self.open_rule)
        self.view.set_button_command("save", self.save_rule)
        self.view.set_button_command("save_as", self.save_rule_as)
        self.view.set_button_command("validate", self.validate_rule)
        self.view.set_button_command("template", self.new_from_template)

    def new_rule(self):
        """Create a new rule file."""
        if self.view.modified:
            if not self.view.confirm_discard():
                return

        self.view.new_file()
        self.view.set_status("新规则文件")

    def new_from_template(self):
        """Create a new rule from template."""
        if self.view.modified:
            if not self.view.confirm_discard():
                return

        template = self.rule_model.create_template_rule()
        import yaml
        content = yaml.dump(template, allow_unicode=True, default_flow_style=False)
        self.view.set_content(content)
        self.view.set_status("已从模板创建新规则")

    def open_rule(self, file_path=None):
        """Open a rule file."""
        if not file_path:
            # Get file from rules directory
            import tkinter.filedialog as filedialog
            file_path = filedialog.askopenfilename(
                title="打开规则文件",
                initialdir=self.rule_model.get_rules_dir(),
                filetypes=[("YAML files", "*.yaml *.yml"), ("All files", "*.*")]
            )
            if not file_path:
                return

        success = self.view.open_file(file_path)
        if success:
            self.view.set_status(f"已打开: {file_path}")

    def save_rule(self):
        """Save the current rule."""
        content = self.view.get_content()
        is_valid, error_msg, data = YamlValidator.validate_syntax(content)
        if not is_valid:
            self.view.show_validation_result(False, error_msg)
            return False

        # If validation passes, save to file
        current_file = self.view.current_file
        success = self.view.save_file(current_file)
        if success:
            self.view.set_status(f"已保存: {self.view.current_file}")
            return True
        return False

    def save_rule_as(self):
        """Save the rule with a new filename."""
        content = self.view.get_content()
        is_valid, error_msg, data = YamlValidator.validate_syntax(content)
        if not is_valid:
            self.view.show_validation_result(False, error_msg)
            return False

        # Save as new file
        import tkinter.filedialog as filedialog
        file_path = filedialog.asksaveasfilename(
            title="另存为",
            defaultextension=".yaml",
            initialdir=self.rule_model.get_rules_dir(),
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")]
        )
        if not file_path:
            return False

        success = self.view.save_file(file_path)
        if success:
            self.view.set_status(f"已保存: {file_path}")
            return True
        return False

    def validate_rule(self):
        """Validate the current rule content."""
        content = self.view.get_content()

        # Clear previous error highlighting
        self.view.clear_error_highlighting()

        # Validate syntax
        is_valid, error_msg, data = YamlValidator.validate_syntax(content)
        if not is_valid:
            self.view.show_validation_result(False, error_msg)
            # Try to extract line number from error message
            if "第" in error_msg and "行" in error_msg:
                try:
                    parts = error_msg.split("第")[1].split("行")[0]
                    line_num = int(parts)
                    self.view.highlight_error(line_num)
                except:
                    pass
            return

        # Validate structure
        is_valid, error_msg = YamlValidator.validate_rule_structure(data)
        self.view.show_validation_result(is_valid, error_msg if not is_valid else "语法正确，结构有效")

    def load_rule_by_name(self, file_name):
        """Load a rule by file name (called from other controllers)."""
        file_path = f"{self.rule_model.get_rules_dir()}/{file_name}"
        self.open_rule(file_path)

    def has_unsaved_changes(self):
        """Check if there are unsaved changes."""
        return self.view.modified
