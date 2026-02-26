---
name: analyze-survey
description: 分析问卷页面结构，提取题目类型、选项和元数据
---

# 问卷分析技能

## 使用场景

当用户需要：
- 了解问卷的结构和题目类型
- 提取问卷的题目信息用于生成填写规则
- 检查问卷链接是否有效
- 获取问卷的题目数量和选项分布

## 执行步骤

### 步骤1: 初始化浏览器并导航

```python
from automation.browser_setup import BrowserSetup
from tools.screen_resolution import get_scale_ratio

playwright_instance, browser, context, page = BrowserSetup.setup_browser_for_fill()
ratio = get_scale_ratio()

# 导航到问卷链接
page.goto(url, wait_until="domcontentloaded")
page.wait_for_selector('#divQuestion', timeout=10000)
```

### 步骤2: 解析HTML结构

```python
from bs4 import BeautifulSoup

html = page.content()
soup = BeautifulSoup(html, 'html.parser')
form = soup.find('div', id='divQuestion')

if not form:
    raise ValueError("未找到问卷主体元素，请确认链接是否为有效的问卷星链接")
```

### 步骤3: 问题类型映射

```python
# 问卷星问题类型映射表
QUESTION_TYPE_MAP = {
    '1': '填空题',      # 单行文本输入
    '2': '多行填空题',   # 多行文本输入
    '3': '单选题',      # 单选按钮
    '4': '多选题',      # 复选框
    '5': '矩阵题',      # 矩阵单选
    '6': '矩阵单选题',  # 矩院单选网格
    '7': '下拉选择题',  # 下拉选择框
    '8': '排序题',      # 选项排序
    '9': '比重题',      # 分配比重
    '11': '多项填空题', # 多个填空
    '12': '多项单选题', # 多个单选题组
    '13': '评分题',     # 量表评分
    '14': '文件上传',   # 文件上传
    '21': '购物题',     # 购物选择
}
```

### 步骤4: 提取题目信息

```python
def extract_questions(form):
    """从问卷HTML中提取题目信息"""
    questions = []

    for fieldset in form.find_all('fieldset'):
        for div in fieldset.find_all('div', class_='field'):
            topic = div.get('topic')
            q_type = div.get('type')
            title = div.get('title', '')

            question = {
                'topic': topic,
                'type_code': q_type,
                'type': QUESTION_TYPE_MAP.get(q_type, '未知类型'),
                'title': title,
            }

            # 单选题和多选题 - 提取选项
            if q_type in ['3', '4']:
                options = div.find_all('div', class_='label')
                question['option_count'] = len(options)
                question['options'] = []
                for opt in options:
                    opt_input = opt.find('input')
                    if opt_input:
                        question['options'].append({
                            'value': opt_input.get('value'),
                            'text': opt.get_text(strip=True)
                        })

            # 下拉选择题 - 提取选项
            elif q_type == '7':
                select_el = div.find('select')
                if select_el:
                    options = [opt for opt in select_el.find_all('option')
                             if opt.get('value', '').strip()]
                    question['option_count'] = len(options)
                    question['options'] = []
                    for opt in options:
                        question['options'].append({
                            'value': opt.get('value'),
                            'text': opt.get_text(strip=True)
                        })

            # 矩阵单选题 - 提取子问题
            elif q_type == '6':
                sub_questions = div.find_all('tr', class_='rowtitle')
                question['sub_question_count'] = len(sub_questions)
                question['sub_questions'] = []
                for sub_q in sub_questions:
                    question['sub_questions'].append({
                        'topic': sub_q.get('topic'),
                        'title': sub_q.get_text(strip=True)
                    })

                # 提取矩阵列选项
                table_header = div.find('tr', class_='rowheader')
                if table_header:
                    columns = table_header.find_all('th')
                    question['column_count'] = len(columns) - 1  # 减去标题列

            questions.append(question)

    return questions
```

### 步骤5: 输出分析结果

```python
questions = extract_questions(form)

# 输出分析摘要
print(f"问卷分析完成：共 {len(questions)} 道题目")
print("-" * 50)

for i, q in enumerate(questions, 1):
    print(f"{i}. [{q['type']}] {q['title'][:30]}...")
    if 'option_count' in q:
        print(f"   选项数: {q['option_count']}")
    if 'sub_question_count' in q:
        print(f"   子问题数: {q['sub_question_count']}")

# 返回结构化数据
return {
    'url': url,
    'total_questions': len(questions),
    'questions': questions,
    'type_distribution': get_type_distribution(questions)
}

def get_type_distribution(questions):
    """统计题目类型分布"""
    distribution = {}
    for q in questions:
        q_type = q['type']
        distribution[q_type] = distribution.get(q_type, 0) + 1
    return distribution
```

### 步骤6: 清理资源

```python
page.close()
context.close()
browser.close()
playwright_instance.stop()
```

## 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| 链接无效或无法访问 | 提示用户检查网络和链接有效性 |
| 未找到 `#divQuestion` 元素 | 提示确认是否为问卷星链接 |
| 页面加载超时 | 增加超时时间或检查网络状况 |
| 无法解析HTML结构 | 检查问卷页面结构是否发生变化 |

## 返回结果格式

```python
{
    'success': True,
    'url': 'https://www.wjx.cn/jq/xxxxx.aspx',
    'total_questions': 10,
    'type_distribution': {
        '单选题': 5,
        '多选题': 2,
        '填空题': 2,
        '矩阵单选题': 1
    },
    'questions': [
        {
            'topic': '1',
            'type_code': '3',
            'type': '单选题',
            'title': '您的性别是？',
            'option_count': 2,
            'options': [
                {'value': '1', 'text': '男'},
                {'value': '2', 'text': '女'}
            ]
        },
        # ... 更多题目
    ]
}
```

## 示例

### 示例1: 分析简单问卷

```
用户输入: 分析这个问卷 https://www.wjx.cn/jq/12345678.aspx

执行流程:
1. 初始化浏览器
2. 访问问卷链接
3. 解析HTML结构
4. 提取题目信息

输出结果:
问卷分析完成：共 5 道题目
--------------------------------------------------
1. [单选题] 您的性别是？
   选项数: 2
2. [单选题] 您的年龄段是？
   选项数: 5
3. [多选题] 您的兴趣爱好是？
   选项数: 6
4. [填空题] 请留下您的建议：
5. [矩阵单选题] 请对以下服务进行评分：
   子问题数: 3

类型分布:
- 单选题: 2
- 多选题: 1
- 填空题: 1
- 矩阵单选题: 1
```

### 示例2: 分析复杂问卷

```
用户输入: 分析这个问卷并生成填写规则 https://www.wjx.cn/jq/87654321.aspx

执行流程:
1. 分析问卷结构
2. 根据题目类型生成默认概率规则
3. 输出规则JSON

生成规则:
[
  {"radio_selection": [1, 1, 1]},           # 单选题平均概率
  {"multiple_selection": [50, 50, 50]},     # 多选题每项50%
  {"dropdown_selection": [1, 1, 1, 1]},     # 下拉题平均概率
  {"blank_filling": [["默认答案"], [1]]},   # 填空题默认答案
  {"matrix_radio_selection": [[1,1,1,1,1], [1,1,1,1,1]]}  # 矩阵题
]
```

## 注意事项

1. **浏览器模式**: 使用非headless模式以便调试
2. **超时设置**: 默认等待时间为10秒，可根据网络状况调整
3. **类型识别**: 依赖问卷星的HTML结构，如果结构变化可能需要调整
4. **编码问题**: 使用BeautifulSoup自动处理编码
5. **隐私保护**: 分析过程不提交任何数据，只读取页面结构
