"""
Verification handling for intelligent verification and slider verification.
Extracted from V2 v9.py
"""
import pyautogui
from selenium.webdriver.common.by import By


class VerificationHandler:
    """Handles various types of verification challenges."""

    def __init__(self, ratio=1.0):
        """
        Initialize the verification handler.

        Args:
            ratio (float): Windows DPI scaling ratio for coordinate calculation.
        """
        self.ratio = ratio

    def get_element_screen_pos(self, driver, element):
        """
        Get the screen coordinates of an element, accounting for DPI scaling.

        Args:
            driver: Selenium WebDriver instance.
            element: WebElement to get coordinates for.

        Returns:
            tuple: (screen_x, screen_y) coordinates.
        """
        # Get element position on page
        element_location = element.location
        # Get browser window position
        window_location = driver.get_window_rect()
        window_width = window_location['width']
        window_height = window_location['height']

        # Get viewport size
        viewport_width = driver.execute_script("return window.innerWidth;")
        viewport_height = driver.execute_script("return window.innerHeight;")

        # Calculate toolbar and border size
        toolbar_border_width = window_width - viewport_width
        toolbar_border_height = window_height - viewport_height

        # Calculate screen coordinates
        x = element_location['x'] + window_location['x']
        y = element_location['y'] + window_location['y']

        # Page scroll offset
        scroll = driver.execute_script("return window.pageYOffset;")
        y -= scroll  # Relative to page
        y += toolbar_border_height  # Add toolbar height

        screen_x = self.ratio * x
        screen_y = self.ratio * y

        return screen_x, screen_y

    def switch_window_to_edge(self, window_title, sleep_time=2):
        """
        Switch to the Edge browser window by title.

        Args:
            window_title (str): Title of the window to switch to.
            sleep_time (int): Time to wait after switching.
        """
        windows = pyautogui.getWindowsWithTitle(window_title)
        for window in windows:
            if "Edge" in window.title:
                window.activate()
                import time
                time.sleep(sleep_time)
                break

    def intelligent_verification(self, driver, element):
        """
        Handle intelligent verification by clicking on the element.

        Args:
            driver: Selenium WebDriver instance.
            element: WebElement to click.
        """
        screen_x, screen_y = self.get_element_screen_pos(driver, element)
        click_pos = (screen_x, screen_y)
        pyautogui.click(click_pos)

    def slider_verification(self, driver, element_slide):
        """
        Handle slider verification by dragging the slider.

        Args:
            driver: Selenium WebDriver instance.
            element_slide: WebElement for the slider.
        """
        screen_x, screen_y = self.get_element_screen_pos(driver, element_slide)

        btn_slide_element = driver.find_element(By.CLASS_NAME, "btn_slide")
        btn_slide_width = btn_slide_element.size["width"] * self.ratio / 2

        element_slide_width = element_slide.size["width"] * self.ratio

        # Move to slider button
        pyautogui.moveTo((screen_x + btn_slide_width, screen_y))
        pyautogui.mouseDown()
        # Drag to the right
        pyautogui.dragTo(screen_x + btn_slide_width + element_slide_width, screen_y, duration=0.5)
        pyautogui.mouseUp()
