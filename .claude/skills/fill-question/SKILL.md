---
name: fill-question
description: 根据题目类型自动填写问卷答案（单选、多选、下拉、矩阵、填空等）
---

# 题目填写技能

## 使用场景

当用户需要：
- 自动填写问卷题目
- 根据概率规则选择答案选项
- 批量填写多份问卷
- 处理各种题目类型（单选、多选、下拉、矩阵、填空）

## 执行步骤

### 步骤1: 获取页面和初始化

```python
from automation.browser_setup import BrowserSetup
from tools.screen_resolution import get_scale_ratio

playwright_instance, browser, context, page = BrowserSetup.setup_browser_for_fill()
ratio = get_scale_ratio()

# 导航到问卷
page.goto(url, wait_until="domcontentloaded")
page.wait_for_selector('#divQuestion', timeout=10000)
```

### 步骤2: 题目类型处理

#### 2.1 单选题 (Radio Selection)

```python
def fill_radio_question(page, topic, probabilities):
    """
    填写单选题

    Args:
        page: Playwright页面对象
        topic: 题目编号
        probabilities: 概率列表，如 [1, 2, 1] 表示第二个选项权重更高
    """
    import random

    # 计算权重选择
    total = sum(probabilities)
    rand_val = random.uniform(0, total)
    cumulative = 0

    for i, prob in enumerate(probabilities):
        cumulative += prob
        if rand_val <= cumulative:
            selected_index = i
            break
    else:
        selected_index = len(probabilities) - 1

    # 构建选择器并点击
    option_num = selected_index + 1
    selector = f"#{topic}_{option_num} + a.jqradio"

    try:
        page.locator(selector).click()
        return True
    except Exception as e:
        print(f"单选题填写失败: {e}")
        return False
```

#### 2.2 多选题 (Multiple Selection)

```python
def fill_multiple_question(page, topic, probabilities):
    """
    填写多选题

    Args:
        page: Playwright页面对象
        topic: 题目编号
        probabilities: 选择概率列表，如 [50, 50, 50] 表示每项50%概率选择
    """
    import random

    selected_indices = []

    for i, prob in enumerate(probabilities):
        if random.randint(0, 100) < prob:
            selected_indices.append(i)

    # 如果没有选中任何选项，选择概率最高的
    if not selected_indices:
        max_prob = max(probabilities)
        selected_indices = [i for i, p in enumerate(probabilities) if p == max_prob][:1]

    # 点击选中的选项
    for idx in selected_indices:
        option_num = idx + 1
        selector = f"#{topic}_{option_num} + a.jqcheckbox"

        try:
            page.locator(selector).click()
        except Exception as e:
            print(f"多选选项填写失败: {e}")

    return len(selected_indices) > 0
```

#### 2.3 下拉选择题 (Dropdown Selection)

```python
def fill_dropdown_question(page, topic, probabilities):
    """
    填写下拉选择题

    Args:
        page: Playwright页面对象
        topic: 题目编号
        probabilities: 概率列表
    """
    import random

    # 计算权重选择
    total = sum(probabilities)
    rand_val = random.uniform(0, total)
    cumulative = 0

    for i, prob in enumerate(probabilities):
        cumulative += prob
        if rand_val <= cumulative:
            selected_index = i
            break
    else:
        selected_index = len(probabilities) - 1

    # 下拉选项从1开始计数，跳过第一个默认选项
    option_value = selected_index + 1

    try:
        # 使用select选项
        page.select_selector(f"select[name='{topic}']", str(option_value))
        return True
    except Exception as e:
        print(f"下拉题填写失败: {e}")
        return False
```

#### 2.4 矩阵单选题 (Matrix Radio Selection)

```python
def fill_matrix_question(page, topic, probabilities_list):
    """
    填写矩阵单选题

    Args:
        page: Playwright页面对象
        topic: 题目编号
        probabilities_list: 二维概率列表，每个子问题对应一个概率列表
    """
    import random

    success_count = 0

    for sub_q_idx, probabilities in enumerate(probabilities_list):
        # 计算权重选择
        total = sum(probabilities)
        rand_val = random.uniform(0, total)
        cumulative = 0

        for i, prob in enumerate(probabilities):
            cumulative += prob
            if rand_val <= cumulative:
                selected_index = i
                break
        else:
            selected_index = len(probabilities) - 1

        # 矩阵题选项编号从1开始
        option_num = selected_index + 1
        sub_topic = f"{topic}_{sub_q_idx + 1}"

        try:
            selector = f"#{sub_topic}_{option_num} + a.jqradio"
            page.locator(selector).click()
            success_count += 1
        except Exception as e:
            print(f"矩阵子题填写失败: {e}")

    return success_count == len(probabilities_list)
```

#### 2.5 填空题 (Blank Filling)

```python
def fill_blank_question(page, topic, answers, probabilities=None):
    """
    填写填空题

    Args:
        page: Playwright页面对象
        topic: 题目编号
        answers: 答案列表，如 ["答案1", "答案2"]
        probabilities: 答案选择概率（可选）
    """
    import random

    # 选择答案
    if probabilities and len(probabilities) == len(answers):
        total = sum(probabilities)
        rand_val = random.uniform(0, total)
        cumulative = 0

        for i, prob in enumerate(probabilities):
            cumulative += prob
            if rand_val <= cumulative:
                answer = answers[i]
                break
        else:
            answer = answers[-1]
    else:
        answer = random.choice(answers) if len(answers) > 1 else answers[0]

    try:
        # 清空并填入答案
        selector = f"textarea[name='{topic}']"
        page.locator(selector).fill(answer)
        return True
    except Exception as e:
        print(f"填空题填写失败: {e}")
        return False
```

### 步骤3: 批量填写处理

```python
def fill_all_questions(page, rules, delay=0.2):
    """
    按照规则批量填写所有题目

    Args:
        page: Playwright页面对象
        rules: 填写规则列表
        delay: 每题填写后延迟（秒）
    """
    import time

    results = {'success': 0, 'failed': 0, 'details': []}

    for rule in rules:
        time.sleep(delay)

        # 单选题
        if 'radio_selection' in rule:
            topic = f"q{results['success'] + results['failed'] + 1}"
            success = fill_radio_question(page, topic, rule['radio_selection'])

        # 多选题
        elif 'multiple_selection' in rule:
            topic = f"q{results['success'] + results['failed'] + 1}"
            success = fill_multiple_question(page, topic, rule['multiple_selection'])

        # 下拉选择题
        elif 'dropdown_selection' in rule:
            topic = f"q{results['success'] + results['failed'] + 1}"
            success = fill_dropdown_question(page, topic, rule['dropdown_selection'])

        # 矩阵单选题
        elif 'matrix_radio_selection' in rule:
            topic = f"q{results['success'] + results['failed'] + 1}"
            success = fill_matrix_question(page, topic, rule['matrix_radio_selection'])

        # 填空题
        elif 'blank_filling' in rule:
            topic = f"q{results['success'] + results['failed'] + 1}"
            answers, probs = rule['blank_filling']
            success = fill_blank_question(page, topic, answers, probs)

        else:
            success = False

        if success:
            results['success'] += 1
        else:
            results['failed'] += 1

        results['details'].append({
            'topic': topic,
            'rule': rule,
            'success': success
        })

    return results
```

### 步骤4: 提交问卷

```python
def submit_survey(page):
    """提交问卷"""
    import time

    try:
        page.locator('.submitbtn').click()
        time.sleep(2)
        return True
    except Exception as e:
        print(f"提交失败: {e}")
        return False
```

### 步骤5: 批量填写循环

```python
def batch_fill(url, rules, count, delay_between=2):
    """
    批量填写多份问卷

    Args:
        url: 问卷链接
        rules: 填写规则
        count: 填写份数
        delay_between: 每份之间延迟（秒）
    """
    import time

    playwright_instance, browser, context, page = BrowserSetup.setup_browser_for_fill()

    try:
        for i in range(count):
            print(f"正在填写第 {i + 1}/{count} 份问卷...")

            # 访问问卷
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_selector('#divQuestion', timeout=10000)

            # 填写
            results = fill_all_questions(page, rules, delay=0.2)
            print(f"  成功: {results['success']}, 失败: {results['failed']}")

            # 提交
            submit_survey(page)

            # 等待
            if i < count - 1:
                time.sleep(delay_between)

        print(f"批量填写完成: {count} 份")

    finally:
        page.close()
        context.close()
        browser.close()
        playwright_instance.stop()
```

## 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| 元素未找到 | 检查选择器是否正确，等待元素加载 |
| 元素被遮挡 | 使用 force=True 强制点击 |
| 点击无响应 | 重试点击或使用JavaScript点击 |
| 问卷结构变化 | 更新选择器规则 |

## 规则格式示例

```python
rules = [
    # 单选题 - 平均概率
    {'radio_selection': [1, 1, 1, 1]},

    # 单选题 - 偏向第二个选项
    {'radio_selection': [1, 5, 1, 1]},

    # 多选题 - 每项50%概率
    {'multiple_selection': [50, 50, 50, 50, 50]},

    # 多选题 - 部分选项高概率
    {'multiple_selection': [80, 20, 80, 20, 80]},

    # 下拉题 - 平均概率
    {'dropdown_selection': [1, 1, 1, 1]},

    # 矩阵题 - 3个子问题，每个5个选项
    {'matrix_radio_selection': [[1,1,1,1,1], [1,1,1,1,1], [1,1,1,1,1]]},

    # 填空题 - 单个答案
    {'blank_filling': [["默认答案"], [1]]},

    # 填空题 - 多个随机答案
    {'blank_filling': [["答案1", "答案2", "答案3"], [1, 1, 1]]},
]
```

## 示例

### 示例1: 简单单选填写

```
用户输入: 填写这份问卷的单选题，用平均概率 https://www.wjx.cn/jq/12345.aspx

执行流程:
1. 分析问卷发现有3道单选题
2. 生成规则: [1,1,1] × 3
3. 依次点击选项
4. 提交问卷

结果: 成功填写并提交
```

### 示例2: 自定义概率填写

```
用户输入: 用这个规则填写 https://www.wjx.cn/jq/12345.aspx
规则:
- 第一题偏向A
- 第二题均匀分布
- 第三题多选BC选项

执行流程:
1. 第一题使用 [5, 1, 1] 概率
2. 第二题使用 [1, 1, 1, 1] 概率
3. 第三题使用 [20, 80, 80, 20] 多选概率

结果: 按自定义规则填写完成
```

### 示例3: 批量填写

```
用户输入: 批量填写10份 https://www.wjx.cn/jq/12345.aspx

执行流程:
1. 分析问卷结构
2. 生成默认规则
3. 循环10次:
   - 打开问卷
   - 填写题目
   - 提交
   - 等待2秒
4. 清理资源

结果: 10份问卷全部填写完成
```

## 注意事项

1. **填写延迟**: 每题之间建议延迟0.2-0.5秒，模拟人工填写
2. **验证码处理**: 填写完成后需要配合验证码处理技能
3. **网络稳定性**: 批量填写时注意网络稳定性
4. **浏览器模式**: 使用非headless模式可以更好地处理验证码
5. **异常处理**: 建议记录每次填写结果，失败时可重试
