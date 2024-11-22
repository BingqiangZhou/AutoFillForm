from selenium import webdriver
# from webdriver_manager.microsoft import EdgeChromiumDriverManager
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import random
import time

# 启动浏览器
# driver = webdriver.Edge(executable_path='./edgedriver_win64/msedgedriver.exe')
            
# driver = webdriver.Edge(EdgeChromiumDriverManager().install())
# chrome = webdriver.Chrome(ChromeDriverManager().install()) # 参考：https://stackoverflow.com/questions/70138159/open-edge-browser-with-selenium-path-error
driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))

# 打开目标网页
driver.get('https://www.wjx.cn/vj/tm808uX.aspx')

def danxuan(driver, probabilities, question_index):
    total = sum(probabilities)
    rand = random.randint(1, total)
    cumulative = 0
    for i, prob in enumerate(probabilities):
        cumulative += prob
        if rand <= cumulative:
            # 选项的选择器可能需要根据您的网页结构进行调整
            option = driver.find_elements_by_css_selector(f'YOUR_SELECTOR_FOR_QUESTION_{question_index}_OPTIONS')[i]
            option.click()
            break

def duoxuan(driver, probabilities, question_index):
    for i, prob in enumerate(probabilities):
        if random.randint(1, 100) <= prob:
            # 选项的选择器可能需要根据您的网页结构进行调整
            option = driver.find_elements_by_css_selector(f'YOUR_SELECTOR_FOR_QUESTION_{question_index}_OPTIONS')[i]
            option.click()

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

# 遍历问题
for index, bili in enumerate(bili_list):
    if index == 25:  # 第26题是多选题
        duoxuan(driver, bili, index + 1)
    else:
        danxuan(driver, bili, index + 1)
    time.sleep(1)  # 等待页面响应，可根据实际情况调整

# 提交问卷
# driver.find_element_by_css_selector('YOUR_SUBMIT_BUTTON_SELECTOR').click()

# 关闭浏览器
# driver.quit()
