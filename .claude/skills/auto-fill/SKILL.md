---
name: auto-fill
description: 交互式问卷填写 - 自动分析、确认规则、批量填写并处理验证码
usage: auto-fill <问卷链接> [填写数量]
example: auto-fill https://www.wjx.cn/jq/12345678.aspx
---

# 交互式问卷填写技能

统一的问卷自动化填写流程，通过交互式确认完成从分析到提交的全过程。

## 交互流程概览

```
用户输入: auto-fill <问卷链接> [数量]
    |
    v
步骤1: 分析问卷
    - 访问链接并解析题目结构
    - 显示题目数量和类型分布
    - 询问: 是否继续？
    |
    v
步骤2: 生成并展示规则
    - 根据题目类型生成默认概率规则
    - 显示每题的规则详情
    - 询问: 使用默认规则？(Y/n)
    |
    v (如果用户选择 n)
步骤2.5: 规则调整
    - 允许用户修改特定题目的概率
    - 支持多次调整直到满意
    |
    v
步骤3: 确认填写数量
    - 询问: 填写多少份？[默认: 1]
    - 如果命令行已指定则跳过
    |
    v
步骤4: 执行填写
    - 显示进度 (1/10, 2/10...)
    - 实时状态更新
    |
    v (如遇验证)
步骤5: 验证处理
    - 自动检测验证类型
    - 尝试自动处理
    - 如失败则提示用户
    |
    v
步骤6: 完成总结
    - 显示成功/失败统计
    - 询问: 是否保存规则？
```

## 执行步骤

### 步骤1: 初始化并分析问卷

```python
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from automation.browser_setup import BrowserSetup
from automation.form_filler import FormFiller
from automation.verification import VerificationHandler
from bs4 import BeautifulSoup
from tools.url_change_judge import wait_for_url_change
from tools.screen_resolution import get_scale_ratio

def analyze_survey(url):
    """分析问卷结构"""
    print("📊 开始分析问卷...")

    # 使用无头模式进行分析
    playwright_instance, browser, context, page = BrowserSetup.setup_browser_for_analysis()

    try:
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_selector('#divQuestion', timeout=10000)
        page_content = page.content()

        soup = BeautifulSoup(page_content, 'html.parser')
        form = soup.find('div', id='divQuestion')

        if not form:
            raise ValueError("未找到问卷主体元素，请确认链接是否为有效的问卷星链接")

        questions = parse_questions(form)

        print(f"✅ 问卷分析完成：共 {len(questions)} 道题目")

        # 统计类型分布
        type_counts = {}
        for q in questions:
            q_type = q['type']
            type_counts[q_type] = type_counts.get(q_type, 0) + 1

        for q_type, count in type_counts.items():
            print(f"   • {q_type}: {count}")

        return questions

    finally:
        page.close()
        context.close()
        browser.close()
        playwright_instance.stop()

def parse_questions(form):
    """解析题目结构"""
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
                'type': question_types.get(q_type, '未知类型'),
                'text': div.find('div', class_='topichtml').text.strip()
            }

            if q_type in ['3', '4']:
                options = []
                for label in div.find_all('div', class_='label'):
                    options.append(label.text.strip())
                question['options'] = options
                question['option_count'] = len(options)

            elif q_type == '7':
                options = []
                select_el = div.find('select')
                if select_el:
                    for option in select_el.find_all('option'):
                        val = option.get('value', '').strip()
                        if val:
                            options.append(option.text.strip())
                question['options'] = options
                question['option_count'] = len(options)

            elif q_type == '6':
                sub_questions = []
                for row in div.find_all('tr', class_='rowtitle'):
                    sub_question = row.find('span', class_='itemTitleSpan').text.strip()
                    options = []
                    next_row = row.find_next_sibling('tr')
                    if next_row:
                        for opt in next_row.find_all('a'):
                            options.append(opt.get('dval'))
                    sub_questions.append({
                        'sub_question': sub_question,
                        'options': options,
                        'option_count': len(options)
                    })
                question['sub_questions'] = sub_questions
                question['sub_question_count'] = len(sub_questions)

            questions.append(question)

    return questions
```

### 步骤2: 生成默认规则

```python
def generate_default_rules(questions):
    """根据题目生成默认填写规则"""
    rules = []
    rule_descriptions = []

    for i, q in enumerate(questions):
        q_type = q['type_code']
        rule = {}
        desc = f"{i+1}. [{q['type']}] {q['text'][:40]}..."

        if q_type == '3':  # 单选题
            count = q.get('option_count', 1)
            probabilities = [1] * count
            rule = {'radio_selection': probabilities}
            desc += f"\n   → 概率: {probabilities} (平均分布)"

        elif q_type == '4':  # 多选题
            count = q.get('option_count', 1)
            probabilities = [50] * count  # 每项50%概率
            rule = {'multiple_selection': probabilities}
            desc += f"\n   → 概率: {probabilities} (每项50%)"

        elif q_type == '7':  # 下拉选择题
            count = q.get('option_count', 1)
            probabilities = [1] * count
            rule = {'dropdown_selection': probabilities}
            desc += f"\n   → 概率: {probabilities} (平均分布)"

        elif q_type == '6':  # 矩阵单选题
            sub_count = q.get('sub_question_count', 1)
            sub_qs = q.get('sub_questions', [])
            probabilities_list = []
            for sub_q in sub_qs:
                opt_count = sub_q.get('option_count', 1)
                probabilities_list.append([1] * opt_count)
            rule = {'matrix_radio_selection': probabilities_list}
            desc += f"\n   → 每个子问题平均分布"

        elif q_type == '1':  # 填空题
            rule = {'blank_filling': [['默认答案'], [1]]}
            desc += f"\n   → 答案: '默认答案'"

        rules.append(rule)
        rule_descriptions.append(desc)

    return rules, rule_descriptions

def display_rules(rule_descriptions):
    """显示规则列表"""
    print("\n📋 默认填写规则:")
    print("=" * 60)
    for desc in rule_descriptions:
        print(desc)
    print("=" * 60)
```

### 步骤3: 交互式规则调整

```python
def adjust_rules_interactive(questions, rules, rule_descriptions):
    """允许用户交互式调整规则"""
    print("\n🔧 规则调整模式")
    print("输入格式: 题目号 新规则")
    print("示例:")
    print("  1 [2,1,1]        - 第1题使用概率[2,1,1]")
    print("  1 [50,50,50]     - 第1题(多选)使用百分比概率")
    print("  3 默认答案       - 第3题(填空)使用答案'默认答案'")
    print("  done             - 完成调整，使用当前规则")

    while True:
        user_input = input("\n请输入调整 (或 'done' 完成): ").strip()

        if user_input.lower() == 'done':
            break

        if not user_input:
            continue

        try:
            parts = user_input.split(None, 1)
            if len(parts) < 2:
                print("❌ 格式错误，请输入: 题目号 规则")
                continue

            q_num = int(parts[0]) - 1  # 转为0-based索引
            if q_num < 0 or q_num >= len(rules):
                print(f"❌ 题目号无效，请输入1-{len(rules)}")
                continue

            new_rule_str = parts[1]
            q = questions[q_num]

            # 解析新规则
            if q['type_code'] in ['3', '7']:  # 单选题/下拉题
                import json
                probabilities = json.loads(new_rule_str)
                if not isinstance(probabilities, list):
                    raise ValueError("概率必须是列表")
                rules[q_num] = {'radio_selection' if q['type_code'] == '3' else 'dropdown_selection': probabilities}
                print(f"✅ 第{q_num+1}题已更新")

            elif q['type_code'] == '4':  # 多选题
                import json
                probabilities = json.loads(new_rule_str)
                rules[q_num] = {'multiple_selection': probabilities}
                print(f"✅ 第{q_num+1}题已更新")

            elif q['type_code'] == '1':  # 填空题
                rules[q_num] = {'blank_filling': [[new_rule_str], [1]]}
                print(f"✅ 第{q_num+1}题已更新")

        except Exception as e:
            print(f"❌ 解析失败: {e}")

    return rules
```

### 步骤4: 执行批量填写

```python
def fill_survey_batch(url, rules, fill_count, log_callback=None):
    """批量填写问卷"""
    if log_callback is None:
        log_callback = print

    log_callback(f"\n🚀 开始填写...")

    # 初始化组件
    form_filler = FormFiller(log_callback=log_callback)
    verification_handler = VerificationHandler(ratio=get_scale_ratio())

    log_callback("正在打开浏览器...")
    playwright_instance, browser, context, page = BrowserSetup.setup_browser_for_fill()

    success_count = 0
    fail_count = 0
    window_title = None

    try:
        for i in range(fill_count):
            current = i + 1
            log_callback(f"\n[{current}/{fill_count}] 填写中...", end=" ")

            try:
                # 打开问卷
                page.goto(url, wait_until="domcontentloaded")

                if window_title is None:
                    window_title = page.title()

                # 填写问题
                success = form_filler.fill_questions(page, rules, delay=0.2)

                if not success:
                    log_callback("❌ 填写失败")
                    fail_count += 1
                    continue

                # 提交表单
                page.locator('.submitbtn').click()
                import time
                time.sleep(2)

                # 检查是否触发验证
                old_url = url
                if not wait_for_url_change(page, old_url, timeout=3000):
                    log_callback("⚠ 触发验证", end=" ")
                    if handle_verification(page, verification_handler, window_title, old_url):
                        log_callback("✓ 验证通过")
                    else:
                        log_callback("✗ 验证失败")
                        fail_count += 1
                        continue

                log_callback("✓ 提交成功")
                success_count += 1

            except Exception as e:
                log_callback(f"❌ 错误: {e}")
                fail_count += 1

    finally:
        # 清理资源
        page.close()
        context.close()
        browser.close()
        playwright_instance.stop()

    return success_count, fail_count

def handle_verification(page, handler, window_title, old_url):
    """处理验证码"""
    try:
        import time

        # 检测智能验证
        locator = page.locator(".sm-txt")
        if locator.count() > 0:
            text = locator.inner_text()
            if text == "点击按钮开始智能验证":
                handler.switch_window_to_edge(window_title)
                time.sleep(1)
                handler.intelligent_verification(page, locator)
                time.sleep(2)

                if not wait_for_url_change(page, old_url, timeout=5000):
                    # 检测滑块验证
                    locator_slide = page.locator("span", has_text="请按住滑块，拖动到最右边")
                    if locator_slide.count() > 0:
                        handler.switch_window_to_edge(window_title)
                        time.sleep(1)
                        handler.slider_verification(page, locator_slide)
                        return wait_for_url_change(page, old_url, timeout=10000)

                return True

        return False

    except Exception as e:
        print(f"验证处理异常: {e}")
        return False
```

### 步骤5: 完整交互流程

```python
def interactive_auto_fill(url, initial_count=None):
    """完整的交互式自动填写流程"""

    # 步骤1: 分析问卷
    try:
        questions = analyze_survey(url)
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        return

    # 确认继续
    confirm = input("\n❓ 是否继续？(Y/n): ").strip().lower()
    if confirm == 'n':
        print("已取消")
        return

    # 步骤2: 生成并展示规则
    rules, rule_descriptions = generate_default_rules(questions)
    display_rules(rule_descriptions)

    # 确认规则
    use_default = input("\n❓ 使用默认规则？(Y/n): ").strip().lower()

    if use_default == 'n':
        rules = adjust_rules_interactive(questions, rules, rule_descriptions)

    # 步骤3: 确认填写数量
    if initial_count is None:
        count_input = input("❓ 填写多少份？[默认: 1]: ").strip()
        fill_count = int(count_input) if count_input else 1
    else:
        fill_count = initial_count

    # 步骤4: 执行填写
    success_count, fail_count = fill_survey_batch(url, rules, fill_count)

    # 步骤5: 显示总结
    print("\n" + "=" * 50)
    print(f"✅ 完成！成功: {success_count}, 失败: {fail_count}")
    print("=" * 50)

    # 询问是否保存规则
    save_rules = input("\n💾 是否保存规则模板？(Y/n): ").strip().lower()
    if save_rules != 'n':
        # 可以添加保存规则的逻辑
        print("规则已保存到会话中")
```

## 用户交互示例

```
用户: auto-fill https://www.wjx.cn/jq/12345678.aspx

📊 开始分析问卷...
✅ 问卷分析完成：共 5 道题目
   • 单选题: 3
   • 多选题: 1
   • 填空题: 1

❓ 是否继续？(Y/n): Y

📋 默认填写规则:
============================================================
1. [单选题] 您的性别是？
   → 概率: [1, 1] (平均分布)
2. [单选题] 您的年龄段是？
   → 概率: [1, 1, 1, 1, 1] (平均分布)
3. [多选题] 您的兴趣爱好是？
   → 概率: [50, 50, 50, 50, 50] (每项50%)
4. [单选题] 您的职业是？
   → 概率: [1, 1, 1, 1] (平均分布)
5. [填空题] 请留下建议
   → 答案: '默认答案'
============================================================

❓ 使用默认规则？(Y/n): n

🔧 规则调整模式
输入格式: 题目号 新规则
示例:
  1 [2,1,1]        - 第1题使用概率[2,1,1]
  1 [50,50,50]     - 第1题(多选)使用百分比概率
  3 默认答案       - 第3题(填空)使用答案'默认答案'
  done             - 完成调整，使用当前规则

请输入调整 (或 'done' 完成): 1 [3,1]
✅ 第1题已更新

请输入调整 (或 'done' 完成): done

❓ 填写多少份？[默认: 1]: 5

🚀 开始填写...
正在打开浏览器...

[1/5] 填写中... ✓ 提交成功
[2/5] 填写中... ⚠ 触发验证 ✓ 验证通过
[3/5] 填写中... ✓ 提交成功
[4/5] 填写中... ✓ 提交成功
[5/5] 填写中... ✓ 提交成功

==================================================
✅ 完成！成功: 5, 失败: 0
==================================================

💾 是否保存规则模板？(Y/n): Y
规则已保存到会话中
```

## 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| 链接无效或无法访问 | 提示用户检查网络和链接有效性，询问是否重试 |
| 未找到 `#divQuestion` 元素 | 提示确认是否为问卷星链接 |
| 分析超时 | 增加超时时间或检查网络状况 |
| 填写失败 | 记录失败原因，继续下一份 |
| 验证失败 | 提示用户手动处理，询问是否继续 |
| 浏览器启动失败 | 检查Playwright和浏览器依赖 |

## 规则格式说明

### 单选题 (radio_selection)
```python
[1, 1, 1]  # 每个选项权重为1，平均分布
[2, 1, 1]  # 第一个选项权重为2，更大概率选中
```

### 多选题 (multiple_selection)
```python
[50, 50, 50]  # 每个选项有50%概率被选中
[80, 20, 30]  # 各选项独立概率
```

### 下拉选择题 (dropdown_selection)
```python
[1, 1, 1, 1]  # 每个选项权重为1
```

### 矩阵单选题 (matrix_radio_selection)
```python
[[1,1,1,1,1], [1,1,1,1,1]]  # 每个子问题的选项概率
```

### 填空题 (blank_filling)
```python
[['答案1', '答案2'], [1, 1]]  # 答案列表及其权重
```

## 注意事项

1. **浏览器模式**: 填写使用非headless模式以便处理验证码
2. **验证码处理**: 智能验证和滑块验证通过pyautogui模拟点击
3. **DPI设置**: 自动检测Windows DPI缩放比例
4. **资源清理**: 无论成功失败都会清理浏览器资源
5. **进度跟踪**: 实时显示填写进度和状态
6. **错误恢复**: 单份失败不影响后续填写
