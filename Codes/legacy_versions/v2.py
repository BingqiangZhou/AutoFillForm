from selenium import webdriver
# from webdriver_manager.microsoft import EdgeChromiumDriverManager
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
import random
import time

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

def duoxuan(driver, probabilities, question_index):
    for i, prob in enumerate(probabilities):
        if random.randint(1, 100) <= prob:
            option_id = f'q{question_index}_{i + 1}'
            css = "a[rel='{}']".format(option_id)
            option = driver.find_element(By.CSS_SELECTOR, css)
            option.click()

# 启动浏览器
# driver = webdriver.Edge(executable_path='./edgedriver_win64/msedgedriver.exe')
            
# driver = webdriver.Edge(EdgeChromiumDriverManager().install())
# chrome = webdriver.Chrome(ChromeDriverManager().install()) # 参考：https://stackoverflow.com/questions/70138159/open-edge-browser-with-selenium-path-error
driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))

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

for i in range(100):

    # 代码在这，放在get()之前
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
    })

    # 打开目标网页
    driver.get('https://www.wjx.cn/vj/tm808uX.aspx')

    driver.implicitly_wait(10)  # 隐性等待10秒

    # 遍历问题
    for index, bili in enumerate(bili_list):
        if index == 25:  # 第26题是多选题
            duoxuan(driver, bili, index + 1)
        else:
            danxuan(driver, bili, index + 1)
        time.sleep(0.2)  # 等待页面响应

    # 提交问卷
    option = driver.find_element(By.ID, "submit_button").click()
    # driver.find_element_by_css_selector('YOUR_SUBMIT_BUTTON_SELECTOR').click()

    if i > 5:
        time.sleep(2000000)

# 关闭浏览器
driver.quit()