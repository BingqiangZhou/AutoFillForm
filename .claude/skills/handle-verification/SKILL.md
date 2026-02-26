---
name: handle-verification
description: 处理问卷提交后的验证码（智能验证点击、滑块拖动）
---

# 验证码处理技能

## 使用场景

当用户需要：
- 处理问卷提交后的智能验证
- 处理滑块验证码
- 自动完成验证流程
- 配合问卷填写自动处理验证

## 执行步骤

### 步骤1: 初始化验证处理器

```python
from tools.screen_resolution import get_scale_ratio
import pyautogui

# 获取系统DPI缩放比例
ratio = get_scale_ratio()

# 设置pyautogui安全措施
pyautogui.PAUSE = 0.5
pyautogui.FAILSAFE = True
```

### 步骤2: 检测验证类型

```python
def detect_verification_type(page):
    """
    检测当前页面出现的验证类型

    Returns:
        str: 'intelligent', 'slider', 或 'none'
    """
    # 检测智能验证
    locator = page.locator(".sm-txt")
    if locator.count() > 0:
        text = locator.inner_text()
        if "点击按钮开始智能验证" in text or "智能验证" in text:
            return 'intelligent'

    # 检测滑块验证
    locator_slide = page.locator("span", has_text="请按住滑块")
    if locator_slide.count() > 0:
        return 'slider'

    # 检测其他可能的滑块验证
    locator_slide2 = page.locator(".slider_container")
    if locator_slide2.count() > 0:
        return 'slider'

    return 'none'
```

### 步骤3: 智能验证处理

```python
def handle_intelligent_verification(page, locator, ratio):
    """
    处理智能验证（点击验证按钮）

    Args:
        page: Playwright页面对象
        locator: 验证按钮的定位器
        ratio: DPI缩放比例
    """
    # 获取元素位置
    box = locator.bounding_box()

    if not box:
        print("无法获取验证按钮位置")
        return False

    # 计算屏幕坐标（考虑DPI缩放）
    x = int(box['x'] + box['width'] / 2) * ratio
    y = int(box['y'] + box['height'] / 2) * ratio

    # 切换到浏览器窗口
    window_title = page.title()
    switch_to_browser_window(window_title)

    # 点击验证按钮
    import time
    time.sleep(0.5)  # 等待窗口切换

    try:
        pyautogui.click(x, y)
        print(f"已点击智能验证按钮: ({x}, {y})")
        time.sleep(2)  # 等待验证处理
        return True
    except Exception as e:
        print(f"智能验证点击失败: {e}")
        return False

def switch_to_browser_window(window_title):
    """
    切换到浏览器窗口（Edge）
    将浏览器窗口置于前台以便pyautogui操作
    """
    import subprocess

    # 使用PowerShell激活窗口
    ps_script = f'''
    $process = Get-Process | Where-Object {{$_.MainWindowTitle -like "*{window_title}*" -or $_.ProcessName -like "*msedge*"}}
    if ($process) {{
        [Microsoft.VisualBasic.Interaction]::AppActivate($process.Id)
    }}
    '''

    try:
        subprocess.run(['powershell', '-Command', ps_script], check=False)
    except Exception as e:
        print(f"窗口切换失败: {e}")
```

### 步骤4: 滑块验证处理

```python
def handle_slider_verification(page, locator, ratio):
    """
    处理滑块验证（拖动滑块到最右边）

    Args:
        page: Playwright页面对象
        locator: 滑块容器的定位器
        ratio: DPI缩放比例
    """
    import time

    # 获取滑块位置
    box = locator.bounding_box()

    if not box:
        print("无法获取滑块位置")
        return False

    # 计算拖动距离
    start_x = int(box['x'] + box['width'] / 2) * ratio
    start_y = int(box['y'] + box['height'] / 2) * ratio
    drag_distance = int(box['width'] * ratio) - 20  # 减去一些边距

    # 切换到浏览器窗口
    window_title = page.title()
    switch_to_browser_window(window_title)

    time.sleep(0.5)  # 等待窗口切换

    try:
        # 模拟人工拖动（带抖动）
        perform_human_drag(start_x, start_y, drag_distance)
        print(f"已拖动滑块: 起点({start_x}, {start_y}), 距离{drag_distance}")
        time.sleep(2)  # 等待验证处理
        return True
    except Exception as e:
        print(f"滑块拖动失败: {e}")
        return False

def perform_human_drag(start_x, start_y, distance):
    """
    模拟人类拖动滑块的行为（带随机抖动）
    """
    import random
    import time

    # 鼠标按下
    pyautogui.moveTo(start_x, start_y, duration=0.2)
    time.sleep(random.uniform(0.1, 0.3))
    pyautogui.mouseDown()

    # 分段拖动，模拟人类行为
    segments = random.randint(5, 10)
    segment_distance = distance / segments

    current_distance = 0
    for i in range(segments):
        # 每段有轻微的速度变化和抖动
        speed = random.uniform(0.05, 0.15)
        jitter_x = random.randint(-2, 2)
        jitter_y = random.randint(-2, 2)

        move_x = start_x + current_distance + segment_distance + jitter_x
        move_y = start_y + jitter_y

        pyautogui.moveTo(move_x, move_y, duration=speed)
        current_distance += segment_distance

        # 偶尔暂停
        if random.random() < 0.2:
            time.sleep(random.uniform(0.05, 0.15))

    # 鼠标释放
    time.sleep(random.uniform(0.1, 0.2))
    pyautogui.mouseUp()
```

### 步骤5: 完整验证流程

```python
def handle_verification(page, url, ratio):
    """
    完整的验证处理流程

    Args:
        page: Playwright页面对象
        url: 问卷URL（用于检测是否提交成功）
        ratio: DPI缩放比例

    Returns:
        bool: 是否验证成功
    """
    import time
    from tools.url_change_judge import wait_for_url_change

    # 首先尝试检测URL变化（可能不需要验证）
    if wait_for_url_change(page, url, timeout=3000):
        print("提交成功，无需验证")
        return True

    # 循环处理验证
    max_attempts = 5
    window_title = page.title()

    for attempt in range(max_attempts):
        print(f"验证处理尝试 {attempt + 1}/{max_attempts}")

        # 检测验证类型
        v_type = detect_verification_type(page)

        if v_type == 'none':
            # 再次检测URL变化
            if wait_for_url_change(page, url, timeout=2000):
                print("验证成功：URL已变化")
                return True
            time.sleep(1)
            continue

        # 处理智能验证
        elif v_type == 'intelligent':
            locator = page.locator(".sm-txt")
            if handle_intelligent_verification(page, locator, ratio):
                print("智能验证处理完成")
                time.sleep(2)

        # 处理滑块验证
        elif v_type == 'slider':
            locator = page.locator("span", has_text="请按住滑块")
            if locator.count() == 0:
                locator = page.locator(".slider_container")
            if handle_slider_verification(page, locator, ratio):
                print("滑块验证处理完成")
                time.sleep(2)

        # 检测是否成功
        if wait_for_url_change(page, url, timeout=3000):
            print("验证成功：URL已变化")
            return True

    print("验证处理失败：已达到最大尝试次数")
    return False
```

### 步骤6: 提交并验证集成

```python
def submit_and_verify(page, url, ratio):
    """
    提交问卷并处理验证码

    Args:
        page: Playwright页面对象
        url: 问卷URL
        ratio: DPI缩放比例
    """
    import time

    # 点击提交按钮
    try:
        page.locator('.submitbtn').click()
        print("已点击提交按钮")
    except Exception as e:
        print(f"提交按钮点击失败: {e}")
        return False

    time.sleep(2)

    # 处理验证
    success = handle_verification(page, url, ratio)

    return success
```

## 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| 无法获取元素位置 | 检查定位器是否正确，增加等待时间 |
| 点击/拖动无响应 | 确保浏览器窗口在前台，检查DPI比例 |
| 验证失败重试 | 最多重试5次，每次间隔2秒 |
| 窗口切换失败 | 使用PowerShell激活窗口 |
| pyautogui超时 | 检查是否有程序阻止鼠标操作 |

## 配置参数

```python
# DPI缩放比例（通常为1.0, 1.25, 1.5, 2.0等）
ratio = get_scale_ratio()

# pyautogui设置
pyautogui.PAUSE = 0.5  # 每个操作后暂停（秒）
pyautogui.FAILSAFE = True  # 鼠标移到左上角时中止

# 验证参数
MAX_VERIFICATION_ATTEMPTS = 5
VERIFICATION_WAIT_TIMEOUT = 3000  # 毫秒
VERIFICATION_RETRY_DELAY = 2  # 秒
```

## 示例

### 示例1: 智能验证

```
场景: 提交问卷后出现"点击按钮开始智能验证"

执行流程:
1. 检测到智能验证按钮
2. 获取按钮屏幕坐标
3. 切换到浏览器窗口
4. 模拟鼠标点击
5. 等待验证处理
6. 检测URL变化确认成功

输出:
已点击智能验证按钮: (1200, 450)
验证成功：URL已变化
```

### 示例2: 滑块验证

```
场景: 提交问卷后出现滑块验证码

执行流程:
1. 检测到滑块容器
2. 计算滑块位置和拖动距离
3. 切换到浏览器窗口
4. 模拟人工拖动（带抖动）
5. 等待验证处理
6. 检测URL变化确认成功

输出:
已拖动滑块: 起点(1000, 500), 距离300
验证成功：URL已变化
```

### 示例3: 组合验证

```
场景: 先智能验证后滑块验证

执行流程:
第1次检测: 智能验证
-> 点击智能验证按钮
第2次检测: 滑块验证
-> 拖动滑块到右边
第3次检测: URL已变化
-> 验证成功

输出:
验证处理尝试 1/5
智能验证处理完成
验证处理尝试 2/5
滑块验证处理完成
验证成功：URL已变化
```

## 注意事项

1. **窗口置顶**: 验证处理需要浏览器窗口在前台
2. **DPI缩放**: 必须正确获取系统DPI缩放比例
3. **人工模拟**: 拖动滑块时添加随机抖动避免检测
4. **安全措施**: 启用pyautogui的failsafe功能
5. **重试机制**: 验证可能失败，建议多次重试
6. **检测间隔**: 每次验证后等待2秒再检测状态
7. **坐标计算**: 屏幕坐标需要乘以DPI缩放比例

## 相关文件

- `tools/screen_resolution.py` - DPI缩放比例获取
- `tools/url_change_judge.py` - URL变化检测
- `automation/verification.py` - 验证处理器实现
