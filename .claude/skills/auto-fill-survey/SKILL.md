---
name: auto-fill-survey
description: 自动填写问卷。当用户提供问卷链接（如问卷星、腾讯问卷等），或提到"填写问卷"、"自动填表"、"批量填写"等相关需求时触发此技能。支持单选、多选、矩阵题、填空题、下拉框等所有题型，自动处理智能验证和滑块验证。
compatibility: Requires Python 3.8+, Playwright, BeautifulSoup4, pyautogui, PyYAML
---

# 自动填写问卷技能

此技能基于 Playwright 和 BeautifulSoup 实现，能够自动分析问卷结构并批量填写。

## 工作流程

### 步骤 1: 分析问卷结构

当用户提供问卷链接后，首先使用 Playwright 访问问卷页面，解析所有问题：

```python
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# 获取问卷页面内容
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(survey_url, wait_until="domcontentloaded")
    page.wait_for_selector('#divQuestion', timeout=10000)
    content = page.content()
    browser.close()

# 使用 BeautifulSoup 解析问题
soup = BeautifulSoup(content, 'html.parser')
```

解析的问题类型包括：
- **type=1**: 填空题
- **type=3**: 单选题
- **type=4**: 多选题
- **type=6**: 矩阵单选题
- **type=7**: 下拉选择题

**向用户展示分析结果**，例如：
```
分析完成！发现 5 个问题：
1. [单选题] 您的性别是？
   选项: 男, 女
2. [单选题] 您的年龄段是？
   选项: 18岁以下, 18-25岁, 26-35岁, 36-45岁, 45岁以上
3. [多选题] 您的兴趣爱好是？
   选项: 阅读, 运动, 旅游, 游戏, 音乐
4. [矩阵单选题] 满意度调查
   子问题: 3个
5. [填空题] 请留下您的建议
```

### 步骤 2: 询问用户配置

**必须询问用户以下配置**：

#### a) 填写数量
```
需要填写多少份问卷？（默认: 1）
```

#### b) 答案概率策略
```
请选择答案概率策略：
1. 均匀分布 - 所有选项概率相等
2. 自定义 - 为每个选项设置概率权重
3. 默认策略 - 单选50/50分布，多选每项30%概率

请输入选项编号 (1/2/3):
```

如果用户选择自定义，需要为每个问题收集概率配置。

#### c) 填空题内容（如果有）
```
问题5是填空题，请提供可能的回答内容：
- 选项1的文本: 非常满意
- 选项1的概率: 50
- 选项2的文本: 比较满意
- 选项2的概率: 30
- 选项3的文本: 一般
- 选项3的概率: 20
[继续添加...输入q结束]
```

### 步骤 3: 生成规则配置

根据用户配置，生成 YAML 规则文件：

```yaml
url: https://www.wjx.cn/vm/XXXXXXXX
number_of_questionnaires_to_be_filled_out: 3
rules:
  - radio_selection: [50, 50]           # 单选题：两个选项各50%概率
  - radio_selection: [20, 30, 30, 10, 10]  # 单选题：5个选项带权重
  - multiple_selection: [30, 30, 25, 40, 35]  # 多选题：每项独立概率
  - matrix_radio_selection:             # 矩阵题
    - [50, 50, 0, 0]                    # 每个子问题的概率
    - [50, 50, 0, 0]
    - [50, 50, 0, 0]
  - blank_filling:                      # 填空题
    - ["非常满意", "比较满意", "一般"]   # 可选文本
    - [50, 30, 20]                      # 对应概率
```

### 步骤 4: 执行填写

使用 Playwright 执行填写过程：

```python
from automation.form_filler import FormFiller
from automation.browser_setup import BrowserSetup
from automation.verification import VerificationHandler
from tools.screen_resolution import get_scale_ratio

# 设置浏览器（非无头模式，用户可看到进度）
playwright_instance, browser, context, page = BrowserSetup.setup_browser_for_fill()

# 创建填写器和验证处理器
form_filler = FormFiller(log_callback=print)
verification_handler = VerificationHandler(ratio=get_scale_ratio())

# 循环填写
for i in range(fill_count):
    page.goto(survey_url, wait_until="domcontentloaded")
    form_filler.fill_questions(page, question_infos, delay=0.2)
    page.locator('.submitbtn').click()
    # 处理验证...
```

## 题型处理说明

### 单选题 (radio_selection)
使用加权随机选择：
```python
total = sum(probabilities)
rand = random.randint(1, total)
cumulative = 0
for i, prob in enumerate(probabilities):
    cumulative += prob
    if rand <= cumulative:
        # 选择第i个选项
        break
```

### 多选题 (multiple_selection)
每个选项独立判断，概率范围为0-100：
```python
for i, prob in enumerate(probabilities):
    if random.randint(1, 100) <= prob:
        # 勾选第i个选项
```
如果全部未选，自动选择概率最高的选项。

### 矩阵单选题 (matrix_radio_selection)
每个子问题独立进行加权随机选择。

### 填空题 (blank_filling)
```python
info_list = [
    ["文本1", "文本2", ...],  # 可选文本列表
    [50, 30, ...]             # 对应概率权重
]
```

### 下拉选择题 (dropdown_selection)
类似单选题，使用加权随机选择。

## 验证处理

问卷平台可能触发验证：

### 智能验证
检测到 "点击按钮开始智能验证" 文本时：
1. 使用 pyautogui 进行模拟点击
2. 需要切换到浏览器窗口

### 滑块验证
检测到 "请按住滑块，拖动到最右边" 时：
1. 使用 pyautogui 拖动滑块
2. 模拟真实用户操作轨迹

**注意**: 验证处理可能失败，此时应暂停并提示用户手动处理。

## 浏览器配置

使用 Playwright 的 Chromium 浏览器，配置反检测措施：

```python
args=['--disable-blink-features=AutomationControlled']
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...'
locale='zh-CN'
```

注入反检测脚本隐藏 webdriver 属性。

## 错误处理

常见错误及处理方式：

1. **页面加载超时**
   - 检查网络连接
   - 确认问卷链接有效
   - 尝试增加超时时间

2. **元素未找到**
   - 问卷结构可能变化
   - 重新分析问卷结构

3. **验证处理失败**
   - 暂停自动化流程
   - 提示用户手动完成验证
   - 可选择继续或终止

4. **填写数量过多被限制**
   - 问卷平台可能有频率限制
   - 建议适当添加延迟
   - 或分批填写

## 示例对话

**用户**: 帮我填写这个问卷 https://www.wjx.cn/vm/abcd123

**助手**:
```
好的，让我先分析一下问卷结构...

[使用 Playwright 访问并分析]

分析完成！发现 3 个问题：
1. [单选题] 您的性别是？
   选项: 男, 女
2. [多选题] 您使用过的手机品牌是？
   选项: 华为, 小米, 苹果, OPPO, vivo
3. [填空题] 请留下您的建议

请回答以下配置问题：

1. 需要填写多少份问卷？(默认: 1)
```

**用户**: 5份

**助手**:
```
2. 请选择答案概率策略：
   1. 均匀分布 - 所有选项概率相等
   2. 自定义 - 为每个选项设置概率权重
   3. 默认策略
   请输入选项编号:
```

**用户**: 1

**助手**:
```
好的，配置完成：
- 填写数量: 5份
- 策略: 均匀分布

开始填写...
[显示进度]

填写完成！成功填写 5/5 份问卷。
```

## 依赖模块

技能使用以下模块（位于 Codes 目录）：

- `automation/browser_setup.py` - 浏览器配置
- `automation/form_filler.py` - 表单填写逻辑
- `automation/verification.py` - 验证处理
- `tools/screen_resolution.py` - DPI缩放比例
- `tools/url_change_judge.py` - URL变化检测

使用时需要确保这些模块在 Python 路径中可访问。
