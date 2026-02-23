from bs4 import BeautifulSoup
import pandas as pd

# 读取HTML文件
file_path = 'test.html'
with open(file_path, 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file, 'html.parser')

# 存储问题数据
questions_data = []

# 查找所有问题的div元素
question_divs = soup.find_all('div', class_='question pc')

for question_div in question_divs:
    question = {}
    
    # 获取问题编号和题目
    question_no = question_div.find('span', class_='qstNo')
    q_title = question_div.find('span', class_='title-inner')
    if q_title is None:
        continue
    question_title = q_title.find('span', class_='title-text')
    
    if question_no and question_title:
        question['编号'] = question_no.text.strip()
        question['题目'] = question_title.text.strip()
    
    # 获取问题类型和选项
    if 'single-choice' in question_div['class']:
        question['类型'] = '单选题'
        choices = question_div.find_all('span', class_='rich-text choice-text')
        question['选项'] = [choice.text.strip() for choice in choices]
        
    elif 'multi-choice' in question_div['class']:
        question['类型'] = '多选题'
        choices = question_div.find_all('span', class_='rich-text choice-text')
        question['选项'] = [choice.text.strip() for choice in choices]
        
    elif 'pc-dropdown' in question_div['class']:
        question['类型'] = '下拉题'
        choices = question_div.find_all('li', class_='el-select-dropdown__item')
        question['选项'] = [choice.text.strip() for choice in choices]
    
    elif 'text-entry' in question_div['class']:
        question['类型'] = '填空题'
        question['选项'] = []
    
    elif 'multi-textentry' in question_div['class']:
        question['类型'] = '多项填空'
        choices = question_div.find_all('div', class_='choice_title')
        question['选项'] = [choice.text.strip() for choice in choices]
    
    elif 'scale' in question_div['class']:
        question['类型'] = '量表题'
        choices = question_div.find_all('div', class_='nps-item')
        question['选项'] = [choice.text.strip() for choice in choices]
    
    elif 'rank-order' in question_div['class']:
        question['类型'] = '排序题'
        choices = question_div.find_all('span', class_='rich-text choice-text')
        question['选项'] = [choice.text.strip() for choice in choices]
    
    elif 'pc-cascade' in question_div['class']:
        question['类型'] = '级联题'
        choices = question_div.find_all('li', class_='el-select-dropdown__item')
        question['选项'] = [choice.text.strip() for choice in choices]
    
    elif 'constant-sum' in question_div['class']:
        question['类型'] = '恒定总和题'
        choices = question_div.find_all('span', class_='rich-text inner-title')
        question['选项'] = [choice.text.strip() for choice in choices]
    
    elif 'slider' in question_div['class']:
        question['类型'] = '滑块题'
        choices = question_div.find_all('span', class_='slider-label')
        question['选项'] = [choice.text.strip() for choice in choices]
    
    elif 'position-container' in question_div['class']:
        question['类型'] = '定位题'
        question['选项'] = []
    
    elif 'pc' in question_div['class'] and 'common' in question_div['class']:
        question['类型'] = '分类题'
        choices = question_div.find_all('span', class_='common-item__text')
        question['选项'] = [choice.text.strip() for choice in choices]
    
    elif 'grade' in question_div['class']:
        question['类型'] = '评分题'
        choices = question_div.find_all('div', class_='grade-choice')
        question['选项'] = ['星星'] * len(choices)
    
    elif 'pc-matrix' in question_div['class']:
        question['类型'] = '矩阵量表'
        choices = question_div.find_all('span', class_='rich-text answer-text')
        question['选项'] = [choice.text.strip() for choice in choices]
    
    elif 'pc-sbs-matrix' in question_div['class']:
        question['类型'] = '矩阵下拉'
        choices = question_div.find_all('span', class_='rich-text answer-text')
        question['选项'] = [choice.text.strip() for choice in choices]
    
    # 添加问题数据到列表
    questions_data.append(question)

# 将数据转换为DataFrame并展示
questions_df = pd.DataFrame(questions_data)
# import ace_tools as tools; tools.display_dataframe_to_user(name="Question Analysis", dataframe=questions_df)
print(questions_df)
