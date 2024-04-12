

from tools.url_change_judge import url_has_changed
from tools.windows_resolution import get_windows_scale_ratio

# 后面包会影响windows DPI缩放比例的计算，所以放在最前面
#缩放比例用于计算智能验证真实的屏幕坐标，通过selenium计算出来的坐标是在缩放比例为1时的坐标
ratio = get_windows_scale_ratio()
print(ratio)

from selenium import webdriver
# from webdriver_manager.microsoft import EdgeChromiumDriverManager
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
import random
import time
import pyautogui

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


if __name__ == "__main__":
    # 启动浏览器（自动管理）
    # driver = webdriver.Edge(executable_path='./edgedriver_win64/msedgedriver.exe')
                
    # driver = webdriver.Edge(EdgeChromiumDriverManager().install())
    # chrome = webdriver.Chrome(ChromeDriverManager().install()) 
    # 参考：https://stackoverflow.com/questions/70138159/open-edge-browser-with-selenium-path-error
    driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))

    for i in range(100):

        # 代码在这，放在get()之前，不让网页发现是在模拟状态下，在模拟状态下，智能验证通不过 参考：https://blog.csdn.net/weixin_45895873/article/details/119811094
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        })

        # 打开目标网页
        driver.get(url)

        driver.implicitly_wait(10)  # 隐性等待10秒，最迟等10秒，网页加载完就结束

        # 遍历并填写问题
        for index, bili in enumerate(bili_list):
            if index == 25:  # 第26题是多选题
                duoxuan(driver, bili, index + 1)
            else:
                danxuan(driver, bili, index + 1)
            time.sleep(0.2)  # 等待页面响应

        # 提交问卷
        option = driver.find_element(By.ID, "submit_button").click()
        time.sleep(2) # 等两秒，看表单是否已经提交，表单已提交，则URL会改变
        # print(driver.current_url)
        # 如果链接没有改变说明
        if url_has_changed(url)(driver) is False:
        # try:
        #     WebDriverWait(driver, 10).until(url_has_changed(url))
        #     time.sleep(1)
        #     print("URL已更改")
        # except :
        #     print("在指定时间内URL未发生变化")
            element = driver.find_element(By.CLASS_NAME, "sm-txt")
            # print(element, element.location['x'], element.location['y'])

            screen_x, screen_y = get_element_screen_pos(driver, element, ratio)
            print(f"元素的屏幕坐标: X = {screen_x}, Y = {screen_y}")

            if element is not None:
                # element.click()
                pyautogui.click((screen_x, screen_y))
                WebDriverWait(driver, 10).until(url_has_changed(url))
        # else:
        #     # 提交问卷
        #     option = driver.find_element(By.ID, "submit_button").click()
        # driver.find_element_by_css_selector('YOUR_SUBMIT_BUTTON_SELECTOR').click()

    # 关闭浏览器
    driver.quit()