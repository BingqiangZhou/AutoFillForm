
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
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import random
import time
import pyautogui
import threading
import msvcrt
import logging
import sys
import os
import win32api
import win32con

# 配置日志
# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Set the logger's level
# Create a file handler
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.INFO)
file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_format)
# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_format)
# Add both handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)


# 单选问题
def radio_selection(driver, probabilities, question_index):
    total = sum(probabilities)
    rand = random.randint(1, total)
    cumulative = 0
    for i, prob in enumerate(probabilities):
        cumulative += prob
        if rand <= cumulative:
            option_id = f'q{question_index}_{i + 1}'
            # print(option_id)
            # option = driver.find_element(By.ID, option_id)
            # css = "a[rel='{}']".format(option_id)
            css = f"#{option_id} + a.jqradio" # 找到id为{option_id}元素，找到为class为jqradio的兄弟a标签
            
            option = driver.find_element(By.CSS_SELECTOR, css)
            # print(css, option)
            option.click()
            break

# 多选问题
def multiple_selection(driver, probabilities, question_index):
    select_option_num = 0
    for i, prob in enumerate(probabilities):
        if random.randint(1, 100) <= prob:
            option_id = f'q{question_index}_{i + 1}'
            # css = f"a[rel='{option_id}']"
            css = f"#{option_id} + a.jqcheck" # 找到id为{option_id}元素，找到为class为jqradio的兄弟a标签
            option = driver.find_element(By.CSS_SELECTOR, css)
            option.click()
            select_option_num += 1
    # 随机时没有选择任何选项，取概率最大的选择，有多个则取第一个
    if select_option_num == 0:
        max_value = max(probabilities)
        # Get the index of the maximum value
        max_index = probabilities.index(max_value)
        option_id = f'q{question_index}_{max_index + 1}'
        # css = f"a[rel='{option_id}']"
        css = f"#{option_id} + a.jqcheck" # 找到id为{option_id}元素，找到为class为jqradio的兄弟a标签
        option = driver.find_element(By.CSS_SELECTOR, css)
        option.click()

# 矩阵单选
def matrix_radio_selection(driver, probabilities_list, question_index):
    for i, probabilities in enumerate(probabilities_list):
        total = sum(probabilities)
        rand = random.randint(1, total)
        cumulative = 0
        option_id = f'drv{question_index}_{i + 1}'
        for j, prob in enumerate(probabilities):
            cumulative += prob
            if rand <= cumulative:
                # print(option_id)
                # option = driver.find_element(By.ID, option_id)
                # css = "a[rel='{}']".format(option_id)
                css = f"#{option_id} a[dval='{j + 1}']" # 找到子节点标签为a，属性包含dval='{j + 1}'的元素
                option = driver.find_element(By.CSS_SELECTOR, css)
                # print(css, option)
                option.click()
                break

# 填空题
def blank_filling(driver, info_list, question_index):
    text_list = info_list[0]
    probabilities_list = info_list[1]
    total = sum(probabilities_list)
    rand = random.randint(1, total)
    cumulative = 0
    option_id = f'q{question_index}'
    css = f"#{option_id}" # 找到id的元素
    element = driver.find_element(By.CSS_SELECTOR, css)
    # print(css, option)
    for j, prob in enumerate(probabilities_list):
        cumulative += prob
        if rand <= cumulative:
            # print(option_id)
            # option = driver.find_element(By.ID, option_id)
            # css = "a[rel='{}']".format(option_id)
            # element.text = text_list[j]
            element.send_keys(text_list[j])
            break

# 获取元素在屏幕上的坐标点
def get_element_screen_pos(driver, element, ratio=1.0):

    # 获取元素在页面上的坐标
    element_location = element.location
    # 获取浏览器窗口的位置
    window_location = driver.get_window_rect()
    window_width = window_location['width']
    window_height = window_location['height']

    # 获取浏览器视窗（viewport）的大小
    viewport_width = driver.execute_script("return window.innerWidth;")
    viewport_height = driver.execute_script("return window.innerHeight;")

    # 计算工具栏和边框的大致尺寸
    toolbar_border_width = window_width - viewport_width
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

# 根据标题切换到Edge浏览器网页窗口
def switch_window_to_edge(window_title, sleep_time=2):
    logger.info("网页标题：{}".format(window_title))
    windows = pyautogui.getWindowsWithTitle(window_title)
    for window in windows:
        # print(window.title)
        if "Edge" in window.title:
            window.activate()
            logger.info("切换窗口...")
            time.sleep(sleep_time)  # 等待2秒确保窗口已经切换
            break

# 根据窗口标题切换到窗口
def switch_window(window_title, sleep_time=2):
    logger.info("窗口标题：{}".format(window_title))
    windows = pyautogui.getWindowsWithTitle(window_title)
    for window in windows:
        # print(window.title)
        if "Edge" in window.title:
            window.activate()
            logger.info("切换窗口...")
            time.sleep(sleep_time)  # 等待2秒确保窗口已经切换
            break

def switch_window_by_driver(driver):
    driver.execute_script("window.focus();")

def intelligent_verification(driver, element, ratio):
    # 获取智能验证文本对应的屏幕坐标，后续使用pyautogui自动移动鼠标来点击智能验证
    screen_x, screen_y = get_element_screen_pos(driver, element, ratio)

    # switch_window_by_driver(driver)
    # click_pos = (screen_x + random.randint(0, int(element.size["width"] * ratio / 2 )), 
    #                  screen_y + random.randint(0, int(element.size["height"] * ratio / 2)))
    click_pos = (screen_x, screen_y)
    pyautogui.click(click_pos)
    logger.info(f"智能验证...x:{click_pos[0]}, y:{click_pos[1]}")

def slider_verification(driver, element_slide, ratio):
    # 获取滑块文本对应的屏幕坐标，后续使用pyautogui自动移动鼠标来点击智能验证
    screen_x, screen_y = get_element_screen_pos(driver, element_slide, ratio)

    btn_slide_element = driver.find_element(By.CLASS_NAME, "btn_slide")
    btn_slide_width = btn_slide_element.size["width"] * ratio / 2

    # 在点击智能验证之前先切换到问卷对应的窗口            
    # switch_window_by_driver(driver)
    # pyautogui.click((screen_x, screen_y))
    element_slide_width = element_slide.size["width"] * ratio
    pyautogui.moveTo((screen_x + btn_slide_width, screen_y))
    pyautogui.mouseDown()
    pyautogui.dragTo(screen_x + btn_slide_width + element_slide_width, screen_y, duration=0.5)
    pyautogui.mouseUp()
    logger.info(f"滑块验证...x:{screen_x}, y:{screen_y}, element_slide_width:{element_slide_width}, btn_slide_width:{btn_slide_width*2}")

def save_webpage():
    # 需要添加下面三行代码：
    # options = webdriver.EdgeOptions()
    # options.add_argument('--save-page-as-mhtml')
    # options.add_argument('--enable-chrome-browser-cloud-management')
    # driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)

    ## 保存文件
    win32api.keybd_event(17, 0, 0, 0)           # 按下ctrl
    win32api.keybd_event(83, 0, 0, 0)           # 按下s
    win32api.keybd_event(83, 0, win32con.KEYEVENTF_KEYUP, 0)    # 释放s
    win32api.keybd_event(17, 0, win32con.KEYEVENTF_KEYUP, 0)    # 释放ctrl
    time.sleep(1)
    # ## 切换路径
    # win32api.keybd_event(17, 0, 0, 0)           # 按下ctrl
    # win32api.keybd_event(76, 0, 0, 0)           # 按下l
    # win32api.keybd_event(83, 0, win32con.KEYEVENTF_KEYUP, 0)    # 释放l
    # win32api.keybd_event(17, 0, win32con.KEYEVENTF_KEYUP, 0)    # 释放ctrl
    # time.sleep(1)
    # pyautogui.typewrite(script_dir, interval=0.01)  # 设置文件夹
    # pyautogui.typewrite(r"C:\\", interval=0.01)  # 设置文件夹
    # win32api.keybd_event(13, 0, 0, 0)           # 按下enter
    # win32api.keybd_event(13, 0, win32con.KEYEVENTF_KEYUP, 0)    # 释放enter
    # time.sleep(0.5)
    # win32api.keybd_event(17, 0, 0, 0)           # 按下ctrl
    # win32api.keybd_event(83, 0, 0, 0)           # 按下s
    # win32api.keybd_event(83, 0, win32con.KEYEVENTF_KEYUP, 0)    # 释放s
    # win32api.keybd_event(17, 0, win32con.KEYEVENTF_KEYUP, 0)    # 释放ctrl
    # time.sleep(1)

    win32api.keybd_event(13, 0, 0, 0)           # 按下enter
    win32api.keybd_event(13, 0, win32con.KEYEVENTF_KEYUP, 0)    # 释放enter
    time.sleep(0.5)
    win32api.keybd_event(37, 0, 0, 0)           # 按下左箭头（是否覆盖文件，选择是）
    win32api.keybd_event(37, 0, win32con.KEYEVENTF_KEYUP, 0)    # 释放左箭头
    time.sleep(0.5)
    win32api.keybd_event(13, 0, 0, 0)           # 按下enter
    win32api.keybd_event(13, 0, win32con.KEYEVENTF_KEYUP, 0)    # 释放enter
    time.sleep(3)

logger.info("选择并读取yaml配置文件")

if getattr(sys, 'frozen', False):
    # The application is frozen using a bundling tool like PyInstaller
    script_dir = os.path.dirname(sys.executable)
else:
    # Normal execution
    script_dir = os.path.dirname(os.path.abspath(__file__))
rules_path = os.path.join(script_dir, "rules")
config_dict = read_data_from_yaml_file(rules_path)
logger.info(f"成功读取yaml配置文件，内容如下\n{config_dict}")
question_infos = config_dict["rules"]

# 问卷链接
url = config_dict["url"].strip()
total_fill_number = config_dict["number_of_questionnaires_to_be_filled_out"]
logger.info(f"即将开始自动填写问卷，预计填写{total_fill_number}份问题\n")

# print(url, question_infos)

# 退出程序标志
exit_flag = False
finished = False

def fill_form():

    try:
        global exit_flag
        logger.info("正在打开浏览器...")
        # 启动浏览器（自动管理）
        options = webdriver.EdgeOptions()
        options.add_argument('--save-page-as-mhtml')
        options.add_argument('--enable-chrome-browser-cloud-management')
        # options.add_experimental_option("prefs", {"download.default_directory": "/"})  # 设置默认下载路径
        driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)
        fill_form_num = 1
        while not exit_flag:

            # 不让网页发现是在模拟状态下，在模拟状态下，智能验证通不过
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
            })

            logger.info("正在打开网页...({})".format(fill_form_num))
            # 打开目标网页
            driver.get(url)

            # 获取页面标题，用于后续切换窗口
            window_title = driver.title

            # 隐性等待10秒，最多等10秒，网页加载完等待结束
            driver.implicitly_wait(10)

            logger.info("填写问题...({})".format(fill_form_num))
            # 遍历并填写问题
            for index, dicts in enumerate(question_infos):
                # print(index, dicts)
                key, value = list(dicts.items())[0]
                if key == "multiple_selection":
                    multiple_selection(driver, value, index + 1)
                elif key == "radio_selection":
                    radio_selection(driver, value, index + 1)
                elif key == "matrix_radio_selection":
                    # matrix_radio_selection(driver, value, index + 1)
                    matrix_radio_selection(driver, value, index + 1)
                elif key == "blank_filling":
                    blank_filling(driver, value, index + 1)
                else:
                    pass
                time.sleep(0.2)  # 没填写一个问题等待0.2秒

            # 提交问卷
            # driver.find_element(By.ID, "submit_button").click()
            driver.find_element(By.CLASS_NAME, 'submitbtn').click()
            logger.info("提交问卷...({})".format(fill_form_num))
            time.sleep(2) # 等2秒，看表单是否已经提交，表单已提交，则URL会改变

            # 如果链接没有改变说明触发了智能验证
            if url_has_changed(url)(driver) is False:
                logger.info("触发了验证...({})".format(fill_form_num))
                # 找到智能验证的文本对应的标签元素
                element = driver.find_element(By.CLASS_NAME, "sm-txt")
                # element_slide = driver.find_element(By.XPATH, "//span[contains(text(), '请按住滑块，拖动到最右边')]")
                if element.text == "点击按钮开始智能验证":
                    # 在点击智能验证之前先切换到问卷对应的窗口            
                    switch_window_to_edge(window_title)
                    logger.info(f"智能验证...({fill_form_num})")
                    intelligent_verification(driver, element, ratio)
                    # time.sleep(2) # 等2秒，看表单是否已经提交，表单已提交，则URL会改变
                    try:
                        WebDriverWait(driver, 5).until(url_has_changed(url))
                    except TimeoutException as e:
                        # 如果链接没有改变说明触发了智能验证
                        if url_has_changed(url)(driver) is False:
                            element_slide = driver.find_element(By.XPATH, "//span[contains(text(), '请按住滑块，拖动到最右边')]")
                            if element_slide is not None:
                                switch_window_to_edge(window_title)
                                logger.info("滑块验证...({})".format(fill_form_num))
                                slider_verification(driver, element_slide, ratio)
                                WebDriverWait(driver, 10).until(url_has_changed(url))
                            else:
                                logger.error("元素不存在，代码可能有点问题\n")
                                save_webpage()
                                logger.error("已保存网页，保存位置请在浏览器下载器中查看位置，快捷键ctrl+j.\n")
                                exit_flag = True # 退出循环
                                break
                    except Exception as e:
                        logger.error("元素不存在，代码可能有点问题\n")
                        save_webpage()
                        logger.error("已保存网页，保存位置请在浏览器下载器中查看位置，快捷键ctrl+j.\n")
                        exit_flag = True # 退出循环
                        break
                else:
                    element_slide = driver.find_element(By.XPATH, "//span[contains(text(), '请按住滑块，拖动到最右边')]")
                    if element_slide is not None:
                        # 在点击滑块验证之前先切换到问卷对应的窗口            
                        switch_window_to_edge(window_title)
                        
                        logger.info("滑块验证...({})".format(fill_form_num))
                        slider_verification(driver, element_slide, ratio)

                        WebDriverWait(driver, 10).until(url_has_changed(url))
                    else:
                        logger.error("元素不存在，代码可能有点问题\n")
                        save_webpage()
                        logger.error("已保存网页，保存位置请在浏览器下载器中查看位置，快捷键ctrl+j.\n")
                        exit_flag = True # 退出循环
                        break
            
            fill_form_num += 1
            if fill_form_num > total_fill_number:
                logger.info(f"问卷已填写{total_fill_number}份，任务结束，即将结束程序...")
                exit_flag = True
                break

        # 关闭浏览器
        driver.quit()
        logger.info("浏览器已关闭.")
    except Exception as e:
        exit_flag = True # 退出循环
        logger.error(e)
        logger.error("程序出错，异常结束...,30秒后退出程序")
        save_webpage()
        logger.error("已保存网页，保存位置请在浏览器下载器中查看位置，快捷键ctrl+j.\n")
        time.sleep(30)

def listen_for_exit():
    global exit_flag
    logger.info("按下 'ESC'键可提前退出程序...")
    while not exit_flag:
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b'\x1b':  # ESC 键的 ASCII 码
                logger.info("按下 'ESC'键，程序将在填写完当前问卷之后结束...")
                exit_flag = True

# 创建并启动填写表单的线程
logger.info("开启填写问卷线程.")
form_thread = threading.Thread(target=fill_form)
form_thread.start()

# 创建并启动监听退出的线程
logger.info("开启按键退出监控线程.")
exit_thread = threading.Thread(target=listen_for_exit)
exit_thread.start()

# 等待线程结束
form_thread.join()
exit_thread.join()

logger.info("程序结束.")