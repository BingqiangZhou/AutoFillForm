"""
Verification handling for intelligent verification and slider verification.
Migrated from Selenium to Playwright.
"""
import pyautogui


class VerificationHandler:
    """Handles various types of verification challenges using Playwright."""

    def __init__(self, ratio=1.0):
        """
        Initialize the verification handler.

        Args:
            ratio (float): Windows DPI scaling ratio for coordinate calculation.
        """
        self.ratio = ratio

    def get_element_screen_pos(self, page, element):
        """
        Get the screen coordinates of an element, accounting for DPI scaling.

        Args:
            page: Playwright Page instance.
            element: Playwright Locator to get coordinates for.

        Returns:
            tuple: (screen_x, screen_y) coordinates.
        """
        # Get element bounding box
        box = element.bounding_box()

        # Get viewport size
        viewport_size = page.viewport_size

        # Get page scroll position
        scroll_y = page.evaluate("window.pageYOffset")

        # Calculate window position (approximate for Playwright)
        # Playwright doesn't directly expose window position like Selenium
        # We'll need to use the page's viewport info
        window_x = 0  # Assuming window is at default position
        window_y = 0

        # Calculate screen coordinates
        element_x = box['x']
        element_y = box['y'] - scroll_y

        # Add window position and account for DPI
        screen_x = self.ratio * (element_x + window_x)
        screen_y = self.ratio * (element_y + window_y)

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

    def intelligent_verification(self, page, locator):
        """
        Handle intelligent verification by clicking on the element.

        Args:
            page: Playwright Page instance.
            locator: Playwright Locator for the element.
        """
        screen_x, screen_y = self.get_element_screen_pos(page, locator)
        click_pos = (screen_x, screen_y)
        pyautogui.click(click_pos)

    def slider_verification(self, page, locator_slide):
        """
        Handle slider verification by dragging the slider.

        Args:
            page: Playwright Page instance.
            locator_slide: Playwright Locator for the slider.
        """
        screen_x, screen_y = self.get_element_screen_pos(page, locator_slide)

        # Get the slider button element
        locator_btn_slide = page.locator(".btn_slide")
        btn_box = locator_btn_slide.bounding_box()
        btn_slide_width = btn_box['width'] * self.ratio / 2

        slide_box = locator_slide.bounding_box()
        element_slide_width = slide_box['width'] * self.ratio

        # Move to slider button
        pyautogui.moveTo((screen_x + btn_slide_width, screen_y))
        pyautogui.mouseDown()
        # Drag to the right
        pyautogui.dragTo(screen_x + btn_slide_width + element_slide_width, screen_y, duration=0.5)
        pyautogui.mouseUp()
