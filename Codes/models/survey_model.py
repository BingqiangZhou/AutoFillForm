"""
Survey model for data persistence.
Extended from V3 to support more configuration options.
"""
import os
import json


class SurveyModel:
    """Model for survey link and configuration persistence."""

    def __init__(self, config_dir="history"):
        """
        Initialize the survey model.

        Args:
            config_dir (str): Directory for storing configuration files.
        """
        self.config_dir = config_dir
        os.makedirs(config_dir, exist_ok=True)

        self.link_file = os.path.join(config_dir, "survey_link.txt")
        self.config_file = os.path.join(config_dir, "app_config.json")
        self.survey_link = self.load_link_from_file()
        self.config = self.load_config_from_file()

    def set_survey_link(self, link):
        """Set and save the survey link."""
        self.survey_link = link
        self.save_link_to_file(link)

    def get_survey_link(self):
        """Get the current survey link."""
        return self.survey_link

    def load_link_from_file(self):
        """Load survey link from file."""
        if os.path.exists(self.link_file):
            with open(self.link_file, "r", encoding="utf-8") as file:
                return file.read().strip()
        return ""

    def save_link_to_file(self, link):
        """Save survey link to file."""
        with open(self.link_file, "w", encoding="utf-8") as file:
            file.write(link)

    def load_config_from_file(self):
        """Load application configuration from file."""
        default_config = {
            "last_rule_file": "",
            "last_fill_count": 1,
            "window_geometry": ""
        }
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as file:
                    return json.load(file)
            except (json.JSONDecodeError, IOError):
                return default_config
        return default_config

    def save_config_to_file(self):
        """Save application configuration to file."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as file:
                json.dump(self.config, file, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving config: {e}")

    def set_config(self, key, value):
        """Set a configuration value."""
        self.config[key] = value
        self.save_config_to_file()

    def get_config(self, key, default=None):
        """Get a configuration value."""
        return self.config.get(key, default)

    def get_last_rule_file(self):
        """Get the last used rule file."""
        return self.get_config("last_rule_file", "")

    def set_last_rule_file(self, rule_file):
        """Set the last used rule file."""
        self.set_config("last_rule_file", rule_file)

    def get_last_fill_count(self):
        """Get the last fill count."""
        return self.get_config("last_fill_count", 1)

    def set_last_fill_count(self, count):
        """Set the last fill count."""
        self.set_config("last_fill_count", count)
