"""
Core form filling functions.
Extracted from V2 v9.py
"""
import random
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait


class FormFiller:
    """Handles form filling operations for different question types."""

    def __init__(self, log_callback=None):
        """
        Initialize the form filler.

        Args:
            log_callback (callable): Optional callback function for logging.
        """
        self.log_callback = log_callback or (lambda msg: None)

    def log(self, message):
        """Log a message using the callback if available."""
        self.log_callback(message)

    def radio_selection(self, driver, probabilities, question_index):
        """
        Handle single-choice (radio) questions with weighted probabilities.

        Args:
            driver: Selenium WebDriver instance.
            probabilities (list): List of probability weights for each option.
            question_index (int): The 1-based index of the question.
        """
        total = sum(probabilities)
        rand = random.randint(1, total)
        cumulative = 0
        for i, prob in enumerate(probabilities):
            cumulative += prob
            if rand <= cumulative:
                option_id = f'q{question_index}_{i + 1}'
                css = f"#{option_id} + a.jqradio"
                option = driver.find_element(By.CSS_SELECTOR, css)
                option.click()
                break

    def multiple_selection(self, driver, probabilities, question_index):
        """
        Handle multi-choice questions with individual probabilities.

        Args:
            driver: Selenium WebDriver instance.
            probabilities (list): List of probability percentages (0-100) for each option.
            question_index (int): The 1-based index of the question.
        """
        select_option_num = 0
        for i, prob in enumerate(probabilities):
            if random.randint(1, 100) <= prob:
                option_id = f'q{question_index}_{i + 1}'
                css = f"#{option_id} + a.jqcheck"
                option = driver.find_element(By.CSS_SELECTOR, css)
                option.click()
                select_option_num += 1

        # If no options selected, choose the one with highest probability
        if select_option_num == 0:
            max_value = max(probabilities)
            max_index = probabilities.index(max_value)
            option_id = f'q{question_index}_{max_index + 1}'
            css = f"#{option_id} + a.jqcheck"
            option = driver.find_element(By.CSS_SELECTOR, css)
            option.click()

    def matrix_radio_selection(self, driver, probabilities_list, question_index):
        """
        Handle matrix-style single-choice questions.

        Args:
            driver: Selenium WebDriver instance.
            probabilities_list (list): List of probability lists, one for each sub-question.
            question_index (int): The 1-based index of the question.
        """
        for i, probabilities in enumerate(probabilities_list):
            total = sum(probabilities)
            rand = random.randint(1, total)
            cumulative = 0
            option_id = f'drv{question_index}_{i + 1}'
            for j, prob in enumerate(probabilities):
                cumulative += prob
                if rand <= cumulative:
                    css = f"#{option_id} a[dval='{j + 1}']"
                    option = driver.find_element(By.CSS_SELECTOR, css)
                    option.click()
                    break

    def blank_filling(self, driver, info_list, question_index):
        """
        Handle text input (fill-in-the-blank) questions.

        Args:
            driver: Selenium WebDriver instance.
            info_list (list): [text_list, probabilities_list] - text options and their probabilities.
            question_index (int): The 1-based index of the question.
        """
        text_list = info_list[0]
        probabilities_list = info_list[1]
        total = sum(probabilities_list)
        rand = random.randint(1, total)
        cumulative = 0
        option_id = f'q{question_index}'
        css = f"#{option_id}"
        element = driver.find_element(By.CSS_SELECTOR, css)
        for j, prob in enumerate(probabilities_list):
            cumulative += prob
            if rand <= cumulative:
                element.send_keys(text_list[j])
                break

    def fill_questions(self, driver, question_infos, delay=0.2):
        """
        Fill all questions based on the configuration.

        Args:
            driver: Selenium WebDriver instance.
            question_infos (list): List of question configurations from YAML.
            delay (float): Delay in seconds between questions.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            for index, dicts in enumerate(question_infos):
                key, value = list(dicts.items())[0]
                if key == "multiple_selection":
                    self.multiple_selection(driver, value, index + 1)
                elif key == "radio_selection":
                    self.radio_selection(driver, value, index + 1)
                elif key == "matrix_radio_selection":
                    self.matrix_radio_selection(driver, value, index + 1)
                elif key == "blank_filling":
                    self.blank_filling(driver, value, index + 1)
                else:
                    self.log(f"Unknown question type: {key}")
                time.sleep(delay)
            return True
        except Exception as e:
            self.log(f"Error filling questions: {e}")
            return False
