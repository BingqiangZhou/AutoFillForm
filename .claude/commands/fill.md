---
name: /fill
description: 自动填写问卷 - 分析问卷结构、生成规则并自动填写
usage: /fill <问卷链接> [填写数量]
example: /fill https://www.wjx.cn/jq/xxxx.aspx 10
---

# 自动问卷填写命令

当收到 `/fill <问卷链接> [填写数量]` 命令时，按以下步骤自动执行：

## 步骤1: 参数验证

1. 验证问卷链接格式（应为有效的WJX链接）
2. 验证填写数量（默认为1，必须为正整数）

## 步骤2: 初始化浏览器

```python
from automation.browser_setup import BrowserSetup
from tools.screen_resolution import get_scale_ratio

playwright_instance, browser, context, page = BrowserSetup.setup_browser_for_fill()
ratio = get_scale_ratio()
```

## 步骤3: 分析问卷结构

```python
from bs4 import BeautifulSoup

page.goto(url, wait_until="domcontentloaded")
page.wait_for_selector('#divQuestion', timeout=10000)

html = page.content()
soup = BeautifulSoup(html, 'html.parser')
form = soup.find('div', id='divQuestion')
```

### 问题类型映射

| type值 | 问题类型 |
|--------|---------|
| 1 | 填空题 |
| 3 | 单选题 |
| 4 | 多选题 |
| 6 | 矩阵单选题 |
| 7 | 下拉选择题 |

### 解析逻辑

```python
question_types = {
    '1': '填空题',
    '3': '单选题',
    '4': '多选题',
    '6': '矩阵单选题',
    '7': '下拉选择题'
}

questions = []
for fieldset in form.find_all('fieldset'):
    for div in fieldset.find_all('div', class_='field'):
        topic = div.get('topic')
        q_type = div.get('type')
        question = {
            'topic': topic,
            'type_code': q_type,
            'type': question_types.get(q_type, '未知类型')
        }

        if q_type in ['3', '4']:
            options = div.find_all('div', class_='label')
            question['option_count'] = len(options)

        elif q_type == '7':
            select_el = div.find('select')
            options = [opt for opt in select_el.find_all('option') if opt.get('value', '').strip()]
            question['option_count'] = len(options)

        elif q_type == '6':
            sub_questions = div.find_all('tr', class_='rowtitle')
            question['sub_question_count'] = len(sub_questions)

        questions.append(question)
```

## 步骤4: 生成默认填写规则

```python
def generate_default_rules(questions):
    """根据分析的问题生成默认填写规则"""
    rules = []

    for q in questions:
        q_type = q['type_code']

        if q_type == '3':  # 单选题 - 平均概率
            option_count = q['option_count']
            probabilities = [1] * option_count
            rules.append({'radio_selection': probabilities})

        elif q_type == '4':  # 多选题 - 每项50%
            option_count = q['option_count']
            probabilities = [50] * option_count
            rules.append({'multiple_selection': probabilities})

        elif q_type == '6':  # 矩阵单选题 - 每个子题平均概率
            sub_count = q['sub_question_count']
            probabilities_list = [[1] * 5 for _ in range(sub_count)]  # 默认5个选项
            rules.append({'matrix_radio_selection': probabilities_list})

        elif q_type == '1':  # 填空题 - 跳过
            rules.append({'blank_filling': [["默认答案"], [1]]})

        elif q_type == '7':  # 下拉题 - 平均概率
            option_count = q['option_count']
            probabilities = [1] * option_count
            rules.append({'dropdown_selection': probabilities})

    return rules
```

## 步骤5: 执行填写

```python
from automation.form_filler import FormFiller
from automation.verification import VerificationHandler
from tools.url_change_judge import wait_for_url_change
import time

form_filler = FormFiller()
verification_handler = VerificationHandler(ratio=ratio)

fill_form_num = 0
window_title = None

while fill_form_num < fill_count:
    fill_form_num += 1

    # 5.1 打开问卷
    page.goto(url, wait_until="domcontentloaded")
    if window_title is None:
        window_title = page.title()

    # 5.2 填写问题
    form_filler.fill_questions(page, rules, delay=0.2)

    # 5.3 提交问卷
    page.locator('.submitbtn').click()
    time.sleep(2)

    # 5.4 检测并处理验证码
    if not wait_for_url_change(page, url, timeout=3000):
        # 检测智能验证
        locator = page.locator(".sm-txt")
        if locator.count() > 0:
            text = locator.inner_text()
            if text == "点击按钮开始智能验证":
                verification_handler.switch_window_to_edge(window_title)
                verification_handler.intelligent_verification(page, locator)

                if not wait_for_url_change(page, url, timeout=5000):
                    # 检测滑块验证
                    locator_slide = page.locator("span", has_text="请按住滑块，拖动到最右边")
                    if locator_slide.count() > 0:
                        verification_handler.switch_window_to_edge(window_title)
                        verification_handler.slider_verification(page, locator_slide)
                        wait_for_url_change(page, url, timeout=10000)
```

## 步骤6: 记录历史

```python
from models.history_model import HistoryModel

history_model = HistoryModel()
session_id = history_model.add_session(
    rule_file="/fill_auto",
    url=url,
    fill_count=fill_count,
    status="completed",
    parsed_questions=questions,
    rules=rules
)
```

## 步骤7: 清理资源

```python
page.close()
context.close()
browser.close()
playwright_instance.stop()
```

## 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| 问卷链接无效 | 提示用户提供正确的WJX链接 |
| 问卷加载超时 | 提示网络问题或问卷已失效 |
| 未找到问题元素 | 提示确认链接是否为问卷星链接 |
| 填写失败 | 记录详细错误信息，继续下一份 |
| 验证失败 | 提示用户手动处理 |

## 示例

### 示例1: 单次填写

```
输入: /fill https://www.wjx.cn/jq/12345678.aspx

执行流程:
1. 初始化浏览器（非headless）
2. 访问问卷链接
3. 分析问卷结构: 发现5个问题
   - 单选题×3
   - 多选题×1
   - 填空题×1
4. 生成规则:
   - 单选题: [1, 1, 1] 平均概率
   - 多选题: [50, 50, 50] 每项50%
   - 填空题: ["默认答案"]
5. 执行填写: 1份
6. 提交成功
7. 记录历史并清理资源
```

### 示例2: 批量填写

```
输入: /fill https://www.wjx.cn/jq/12345678.aspx 10

执行流程:
1. 分析问卷并生成规则（同上）
2. 循环填写10份问卷
3. 每份间隔约2秒
4. 自动处理验证码（如有）
5. 结果: 10份全部成功
```

### 示例3: 带验证码的问卷

```
输入: /fill https://www.wjx.cn/jq/87654321.aspx

执行流程:
1. 分析问卷并生成规则
2. 执行填写
3. 提交后触发验证
4. 检测到智能验证 → 点击验证按钮
5. 检测到滑块验证 → 拖动滑块到最右边
6. 验证通过，提交成功
```

## 注意事项

1. **浏览器窗口**: 填写过程中会打开非headless浏览器窗口，请勿手动关闭
2. **验证码处理**: 使用pyautogui进行屏幕坐标点击，确保浏览器窗口在前台
3. **DPI比例**: 自动获取系统DPI比例用于坐标计算
4. **填写延迟**: 每个问题填写后延迟0.2秒，模拟人工填写速度
5. **填空题**: 默认使用"默认答案"作为填写内容，用户如需自定义需使用GUI版本
