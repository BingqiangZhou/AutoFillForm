"""
YAML syntax validation utility.
"""
import yaml


class YamlValidator:
    """Validator for YAML syntax and structure."""

    @staticmethod
    def validate_syntax(yaml_content):
        """
        Validate YAML syntax.

        Args:
            yaml_content (str): YAML content as string.

        Returns:
            tuple: (is_valid, error_message, parsed_data)
        """
        try:
            data = yaml.safe_load(yaml_content)
            if data is None:
                return False, "YAML内容为空", None
            return True, "", data
        except yaml.YAMLError as e:
            error_msg = str(e)
            # Get more specific error location if available
            if hasattr(e, 'problem_mark'):
                mark = e.problem_mark
                error_msg = f"第{mark.line + 1}行，第{mark.column + 1}列: {e.problem}"
            return False, f"YAML语法错误: {error_msg}", None

    @staticmethod
    def validate_rule_structure(data):
        """
        Validate rule file structure.

        Args:
            data (dict): Parsed YAML data.

        Returns:
            tuple: (is_valid, error_message)
        """
        if not isinstance(data, dict):
            return False, "规则文件必须是一个对象/字典"

        required_keys = ['url', 'number_of_questionnaires_to_be_filled_out', 'rules']
        missing_keys = [k for k in required_keys if k not in data]
        if missing_keys:
            return False, f"缺少必需的字段: {', '.join(missing_keys)}"

        # Validate URL
        url = data.get('url', '').strip()
        if not url:
            return False, "URL不能为空"
        if not url.startswith('http://') and not url.startswith('https://'):
            return False, "URL必须以http://或https://开头"

        # Validate fill count
        fill_count = data.get('number_of_questionnaires_to_be_filled_out', 0)
        if not isinstance(fill_count, int) or fill_count < 1:
            return False, "填写数量必须是大于0的整数"

        # Validate rules
        rules = data.get('rules', [])
        if not isinstance(rules, list):
            return False, "rules必须是一个列表"

        if len(rules) == 0:
            return False, "rules列表不能为空"

        # Validate each rule
        for i, rule in enumerate(rules):
            if not isinstance(rule, dict):
                return False, f"规则{i + 1}必须是一个对象/字典"

            if len(rule) != 1:
                return False, f"规则{i + 1}必须只有一个键值对"

            key = list(rule.keys())[0]
            valid_types = ['radio_selection', 'multiple_selection', 'matrix_radio_selection', 'blank_filling', 'dropdown_selection']
            if key not in valid_types:
                return False, f"规则{i + 1}: 未知的问题类型 '{key}'"

            value = rule[key]
            if key == 'blank_filling':
                if not isinstance(value, list) or len(value) != 2:
                    return False, f"规则{i + 1}: blank_filling必须是一个包含两个元素的列表 [文本列表, 概率列表]"
                if not isinstance(value[0], list) or not isinstance(value[1], list):
                    return False, f"规则{i + 1}: blank_filling的两个元素都必须是列表"
                if len(value[0]) != len(value[1]):
                    return False, f"规则{i + 1}: 文本列表和概率列表长度必须相同"

            elif key == 'matrix_radio_selection':
                if not isinstance(value, list) or len(value) == 0:
                    return False, f"规则{i + 1}: matrix_radio_selection必须是一个非空列表"

            else:  # radio_selection or multiple_selection
                if not isinstance(value, list) or len(value) == 0:
                    return False, f"规则{i + 1}: {key}必须是一个非空列表"

        return True, ""

    @staticmethod
    def validate_file(file_path):
        """
        Validate a YAML file.

        Args:
            file_path (str): Path to the YAML file.

        Returns:
            tuple: (is_valid, error_message, parsed_data)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return False, f"无法读取文件: {e}", None

        is_valid, error_msg, data = YamlValidator.validate_syntax(content)
        if not is_valid:
            return False, error_msg, None

        is_valid, error_msg = YamlValidator.validate_rule_structure(data)
        if not is_valid:
            return False, error_msg, None

        return True, "", data
