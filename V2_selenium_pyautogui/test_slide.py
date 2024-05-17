from tools.read_list_data_from_file import read_data_from_yaml_file
from tools.url_change_judge import url_has_changed
from tools.windows_resolution import get_windows_scale_ratio

# 后面包会影响windows DPI缩放比例的计算，所以放在最前面
# 缩放比例用于计算智能验证真实的屏幕坐标，通过selenium计算出来的坐标是在缩放比例为1时的坐标
ratio = get_windows_scale_ratio()
# print(ratio)

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
import random
import time
import pyautogui
import threading
import msvcrt
import logging
import os

# 获取元素在屏幕上的坐标点
def get_element_screen_pos(driver, element, ratio=1.0):

    # 获取元素在页面上的坐标
    element_location = element.location
    # 获取浏览器窗口的位置
    window_location = driver.get_window_rect()
    # window_width = window_location['width']
    window_height = window_location['height']

    # 获取浏览器视窗（viewport）的大小
    viewport_width = driver.execute_script("return window.innerWidth;")
    viewport_height = driver.execute_script("return window.innerHeight;")

    # 计算工具栏和边框的大致尺寸
    # toolbar_border_width = window_width - viewport_width
    toolbar_border_height = window_height - viewport_height

    # 计算屏幕坐标
    x = element_location['x'] + window_location['x']
    y = element_location['y'] + window_location['y']

    # 页面滚动偏移
    scroll = driver.execute_script("return window.pageYOffset;")
    y -= scroll # 相对页面Y偏移 减去 页面滚动偏移 得到 当前坐标相对当前页面的坐标
    y += toolbar_border_height # 加上工具栏的高

    screen_x = ratio * x
    screen_y = ratio * y

    return screen_x, screen_y

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

logger.info("正在打开浏览器...")
# 启动浏览器（自动管理）
driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))
fill_form_num = 1

# 不让网页发现是在模拟状态下，在模拟状态下，智能验证通不过
driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
})

logger.info("正在打开网页...({})".format(fill_form_num))
file_path = 'E:/Projects/AutoFillForm/selenium_pyautogui_V2/docs/广南县坝美镇乡村旅游对农户生计资本影响的研究.html'
local_url = f"file:///{file_path.replace(os.path.sep, '/')}"
# 打开目标网页
driver.get(local_url)

# 找到智能验证的文本对应的标签元素
element = driver.find_element(By.CLASS_NAME, "sm-txt")
# element_slide = driver.find_element(By.XPATH, "//span[contains(text(), '请按住滑块，拖动到最右边')]")
if element is not None:
    if element.text == "点击按钮开始智能验证":
        # 获取智能验证文本对应的屏幕坐标，后续使用pyautogui自动移动鼠标来点击智能验证
        screen_x, screen_y = get_element_screen_pos(driver, element, ratio)

        # switch_window_by_driver(driver)
        pyautogui.click((screen_x, screen_y))
        logger.info("智能验证...({})".format(fill_form_num))
    else:
        element_slide = driver.find_element(By.XPATH, "//span[contains(text(), '请按住滑块，拖动到最右边')]")
        if element_slide is not None:
            # 获取智能验证文本对应的屏幕坐标，后续使用pyautogui自动移动鼠标来点击智能验证
            screen_x, screen_y = get_element_screen_pos(driver, element_slide, ratio)
            btn_slide_element = driver.find_element(By.CLASS_NAME, "btn_slide")
            btn_slide_width = btn_slide_element.size["width"] * ratio / 2

            # 在点击智能验证之前先切换到问卷对应的窗口            
            # switch_window_by_driver(driver)
            # pyautogui.click((screen_x, screen_y))
            element_slide_size = element_slide.size
            pyautogui.moveTo((screen_x + btn_slide_width, screen_y))
            pyautogui.mouseDown()
            pyautogui.dragTo(screen_x + btn_slide_width + element_slide_size["width"]*ratio, screen_y, duration=0.5)
            pyautogui.mouseUp()
            logger.info("智能验证...({})".format(fill_form_num))
        else:
            logger.error("元素不存在，代码可能有点问题\n")

# 关闭浏览器
driver.quit()