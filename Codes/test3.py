import pyautogui
import time
import random

# 尝试切换到标题完全是“微信”的窗口
windows = pyautogui.getWindowsWithTitle("微信")
for window in windows:
    if window.title == "微信":
        window.activate()
        time.sleep(2)  # 等待2秒确保窗口已经切换
        break

# 重复执行的次数
repeat_times = 400

for _ in range(repeat_times):
    # 第一步：开启小程序
    pyautogui.click(1686, 789)
    time.sleep(2)  # 等待2秒以加载页面

    # 定义age和salary的起始Y坐标
    age_start_y = 585
    salary_start_y = 1000

    # 随机选择一个age和salary选项
    age_choice_y = age_start_y + 80 * random.randint(0, 3)
    salary_choice_y = salary_start_y + 80 * random.randint(0, 4)

    # 一系列的坐标和操作
    steps = [
        (1032, 440), (1032, 783), (1032, 1128), 'pagedown', (1032, 477), (1032, 822), 
        (1032, 1161), 'pagedown', (1032, 513), (1032, 855), (1032, 1202), 'pagedown', 
        (1032, 549), (1032, 896), (1032, 1236), 'pagedown', (1032, 582), (1032, 927), 
        (1032, 1274), 'pagedown', (1032, 618), (1032, 966), 'pagedown', (1032, 312), 
        (1032, age_choice_y), (1032, salary_choice_y), 'pagedown', (1032, 1167)
    ]

    # 执行步骤，除了提交按钮
    for step in steps:
        if isinstance(step, tuple):
            # 如果是坐标，则点击
            pyautogui.click(step)
            time.sleep(0.2)  # 等待0.2秒
        elif step == 'pagedown':
            # 如果是页面向下滚动操作
            pyautogui.press('pagedown')
            time.sleep(0.2)  # 等待页面滚动完成

    # 点击提交按钮并等待2秒以确保提交完成
    pyautogui.click(1032, 1167)
    time.sleep(2)

    # 关闭窗口
    pyautogui.click(1547, 150)
    time.sleep(2)  # 每次运行完成后等待2秒

# 脚本结束
print("操作完成")
