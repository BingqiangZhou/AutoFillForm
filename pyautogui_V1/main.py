import pyautogui
import random
import time

wait_click_or_key_press = 0.1 # 等待点击和按钮响应时间
wait_page_load = 3 # 等待页面加载时间
wait_page_load = 3 # 

time.sleep(3)
for z in range(400):
    print("准备启动小程序")
    pyautogui.click((1686, 789)) # 启动小程序
    time.sleep(3) # 等待加载
    print("准备填写问卷")
    pyautogui.scroll(-160)  # 滑动到第一个问题
    # for j in range(6):
    #     pyautogui.press('down')
    #     time.sleep(0.1)  # 等待反应
    print("滑动到第一个问题")
    # 填写非收入问题
    pos = [1032, 240]
    for i in range(18):
        time.sleep(wait_click_or_key_press)  # 等待反应
        pyautogui.click(pos)
        print(f"选择第{i+1}问题")
        time.sleep(wait_click_or_key_press)  # 等待反应
        # pyautogui.scroll(-360)  # 向下滚动10行
        for j in range(5):
            pyautogui.press('down')
            time.sleep(wait_click_or_key_press)  # 等待反应
        pos[1] += 45 # 补充y方向偏移
    pyautogui.scroll(-1000)  # 滑动到最下面
    # 填写岁数
    pos = (1032, 300)
    print("填写岁数")
    pyautogui.click(pos)
    time.sleep(wait_click_or_key_press)  # 等待反应
    # 填写收入
    print("填写收入")
    pos = [1032, 710]
    y_delta = random.randrange(0, 4) * 80 # 随机选取收入
    pos[1] += y_delta
    pyautogui.click(pos)
    time.sleep(wait_click_or_key_press)  # 等待反应
    # 提交问卷
    pos = [1032, 1170]
    pyautogui.click(pos)
    time.sleep(0.5)  # 等待反应
    # 关闭窗口
    pos = [1550, 150]
    pyautogui.click(pos)
    time.sleep(0.5)
    # break
    print("填写了{}次问卷了", z+1)