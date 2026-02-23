"""
Rule editor controller - YAML rule editor logic.
Migrated to PyQt6.
"""
from utils.yaml_validator import YamlValidator


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
        # Use lambda to avoid clicked(bool) passing False as file_path
        self.view.set_button_command("open", lambda checked=False: self.open_rule())
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
            # File dialog is handled by view
            success = self.view.open_file()
        else:
            success = self.view.open_file(file_path)

        if success:
            self.view.set_status(f"已打开: {self.view.current_file}")

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

        # Save as new file (file dialog is handled by view)
        success = self.view.save_file()
        if success:
            self.view.set_status(f"已保存: {self.view.current_file}")
            return True
        return False

    def validate_rule(self):
        """Validate the current rule content."""
        content = self.view.get_content()

        # Validate syntax
        is_valid, error_msg, data = YamlValidator.validate_syntax(content)
        if not is_valid:
            self.view.show_validation_result(False, error_msg)
            return

        # Validate structure
        is_valid, error_msg = YamlValidator.validate_rule_structure(data)
        self.view.show_validation_result(is_valid, error_msg if not is_valid else "语法正确，结构有效")

    def load_rule_by_name(self, file_name):
        """Load a rule by file name (called from other controllers)."""
        import os
        file_path = os.path.join(self.rule_model.get_rules_dir(), file_name)
        self.open_rule(file_path)

    def has_unsaved_changes(self):
        """Check if there are unsaved changes."""
        return self.view.modified
