

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

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()


# 单选问题
def danxuan(driver, probabilities, question_index):
    total = sum(probabilities)
    rand = random.randint(1, total)
    cumulative = 0
    for i, prob in enumerate(probabilities):
        cumulative += prob
        if rand <= cumulative:
            option_id = f'q{question_index}_{i + 1}'
            # print(option_id)
            # option = driver.find_element(By.ID, option_id)
            css = "a[rel='{}']".format(option_id)
            option = driver.find_element(By.CSS_SELECTOR, css)
            # print(css, option)
            option.click()
            break

# 多选问题
def duoxuan(driver, probabilities, question_index):
    for i, prob in enumerate(probabilities):
        if random.randint(1, 100) <= prob:
            option_id = f'q{question_index}_{i + 1}'
            css = "a[rel='{}']".format(option_id)
            option = driver.find_element(By.CSS_SELECTOR, css)
            option.click()

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

def switch_window_by_driver(driver):
    driver.execute_script("window.focus();")

# 每个问题的概率列表
bili_list = [
    [99, 1], [40, 60], [50, 25, 25], [20, 20, 20, 20, 10, 10], [60, 40],
    [7, 20, 63, 6, 3, 1], [41, 64, 82, 48], [10, 35, 45, 55], [10, 35, 45, 55],
    [10, 35, 45, 55], [10, 35, 45, 55], [10, 35, 45, 55], [10, 35, 45, 55],
    [10, 35, 45, 55], [10, 35, 45, 55], [10, 35, 45, 55], [10, 35, 45, 55],
    [10, 35, 45, 55], [10, 35, 45, 55], [10, 35, 45, 55], [10, 35, 45, 55],
    [10, 35, 45, 55], [20, 80], [20, 80], [70, 30], [50, 80, 70, 20, 10, 60],
    [55, 52, 5, 15], [53, 56, 0], [75, 25], [6, 12, 30, 40, 12], [55, 15, 40, 35],
    [80, 20], [40, 60], [40, 60]
]

# 问卷链接
url = 'https://www.wjx.cn/vj/tm808uX.aspx'

# 退出程序标志
exit_flag = False

def fill_form():

    try:
        global exit_flag
        logger.info("正在打开浏览器...")
        # 启动浏览器（自动管理）
        driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))
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
            for index, bili in enumerate(bili_list):
                if index == 25:  # 第26题是多选题
                    duoxuan(driver, bili, index + 1)
                else:
                    danxuan(driver, bili, index + 1)
                time.sleep(0.2)  # 没填写一个问题等待0.2秒

            # 提交问卷
            driver.find_element(By.ID, "submit_button").click()
            logger.info("提交问卷...({})".format(fill_form_num))
            time.sleep(2) # 等2秒，看表单是否已经提交，表单已提交，则URL会改变

            # 如果链接没有改变说明触发了智能验证
            if url_has_changed(url)(driver) is False:
                # 找到智能验证的文本对应的标签元素
                element = driver.find_element(By.CLASS_NAME, "sm-txt")
                if element is not None:
                    # 获取智能验证文本对应的屏幕坐标，后续使用pyautogui自动移动鼠标来点击智能验证
                    screen_x, screen_y = get_element_screen_pos(driver, element, ratio)

                    # 在点击智能验证之前先切换到问卷对应的窗口            
                    switch_window_to_edge(window_title)
                    # switch_window_by_driver(driver)
                    pyautogui.click((screen_x, screen_y))
                    logger.info("智能验证...({})".format(fill_form_num))
                    WebDriverWait(driver, 10).until(url_has_changed(url))
                else:
                    logger.error("元素不存在，代码可能有点问题\n")
                    exit_flag = True # 退出循环
                    break
            
            fill_form_num += 1

        # 关闭浏览器
        driver.quit()
        logger.info("浏览器已关闭.")
    except Exception as e:
        exit_flag = True # 退出循环
        logger.error(e.with_traceback())
        logger.error("程序出错，异常结束...")

def listen_for_exit():
    global exit_flag
    logger.info("按下 'ESC'键可退出程序...")
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