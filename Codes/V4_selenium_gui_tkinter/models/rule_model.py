"""
Rule model for YAML rule file loading and management.
"""
import os
import yaml
from tools.read_list_data_from_file import list_yaml_files, read_yaml_file


class RuleModel:
    """Model for managing YAML rule files."""

    def __init__(self, rules_dir="rules"):
        """
        Initialize the rule model.

        Args:
            rules_dir (str): Directory containing YAML rule files.
        """
        self.rules_dir = rules_dir
        self.current_rule = None
        self.current_rule_file = None

    def get_rules_dir(self):
        """Get the rules directory path."""
        return self.rules_dir

    def list_yaml_files(self):
        """
        List all YAML files in the rules directory.

        Returns:
            list: List of YAML file names.
        """
        if not os.path.exists(self.rules_dir):
            os.makedirs(self.rules_dir)
        return list_yaml_files(self.rules_dir)

    def get_yaml_files_dict(self):
        """
        Get a dictionary of YAML files.

        Returns:
            dict: Dictionary with file names as keys and full paths as values.
        """
        yaml_files = self.list_yaml_files()
        return {name: os.path.join(self.rules_dir, name) for name in yaml_files}

    def load_rule(self, file_name):
        """
        Load a rule from a YAML file.

        Args:
            file_name (str): Name of the YAML file.

        Returns:
            dict or None: Parsed YAML content or None if error.
        """
        file_path = os.path.join(self.rules_dir, file_name)
        try:
            self.current_rule = read_yaml_file(file_path)
            self.current_rule_file = file_name
            return self.current_rule
        except Exception as e:
            print(f"Error loading rule file: {e}")
            return None

    def get_current_rule(self):
        """Get the currently loaded rule."""
        return self.current_rule

    def get_current_rule_file(self):
        """Get the currently loaded rule file name."""
        return self.current_rule_file

    def get_rule_url(self):
        """Get the URL from the current rule."""
        if self.current_rule:
            return self.current_rule.get("url", "").strip()
        return ""

    def get_rule_fill_count(self):
        """Get the fill count from the current rule."""
        if self.current_rule:
            return self.current_rule.get("number_of_questionnaires_to_be_filled_out", 1)
        return 1

    def get_rule_rules(self):
        """Get the rules list from the current rule."""
        if self.current_rule:
            return self.current_rule.get("rules", [])
        return []

    def save_rule(self, file_name, rule_content):
        """
        Save a rule to a YAML file.

        Args:
            file_name (str): Name of the file to save.
            rule_content (dict): Rule content to save.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not file_name.endswith('.yaml') and not file_name.endswith('.yml'):
            file_name += '.yaml'

        file_path = os.path.join(self.rules_dir, file_name)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(rule_content, f, allow_unicode=True, default_flow_style=False)
            self.current_rule = rule_content
            self.current_rule_file = file_name
            return True
        except Exception as e:
            print(f"Error saving rule file: {e}")
            return False

    def validate_rule_content(self, rule_content):
        """
        Validate the structure of a rule content dictionary.

        Args:
            rule_content (dict): Rule content to validate.

        Returns:
            tuple: (is_valid, error_message)
        """
        if not isinstance(rule_content, dict):
            return False, "规则必须是一个字典"

        required_keys = ['url', 'number_of_questionnaires_to_be_filled_out', 'rules']
        for key in required_keys:
            if key not in rule_content:
                return False, f"缺少必需的字段: {key}"

        if not isinstance(rule_content['rules'], list):
            return False, "rules 必须是一个列表"

        return True, ""

    def create_template_rule(self):
        """
        Create a template rule for new rules.

        Returns:
            dict: Template rule content.
        """
        return {
            'url': 'https://www.wjx.cn/vm/XXXXXXXX',
            'number_of_questionnaires_to_be_filled_out': 1,
            'rules': [
                {'radio_selection': [50, 50]},
                {'multiple_selection': [50, 50, 50]},
                {'matrix_radio_selection': [[50, 50, 0, 0], [50, 50, 0, 0]]},
                {'blank_filling': [['选项1', '选项2'], [50, 50]]}
            ]
        }
