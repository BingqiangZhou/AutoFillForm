from bs4 import BeautifulSoup

def analyze_html_file(file_path):
    # 读取HTML文件内容
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 找到所有的问题块
    questions = soup.find_all('div', class_='question')
    
    # 遍历每个问题块
    for question in questions:
        # 获取问题元素的id
        question_id = question.get('id')
        # print(question_id)
        q = question.find('div', class_='question-title')
        if q is None:
            continue
        # 获取问题标题
        title = q.text.strip()
        
        # 获取问题类型
        question_type = question.get('data-type')
        
        # 获取问题选项
        options = question.find_all('div', class_='option')
        option_texts = [option.text.strip() for option in options]
        
        # 打印问题标题、类型和选项
        print("问题id:", question_id)
        print("问题标题:", title)
        print("问题类型:", question_type)
        print("选项:", option_texts)
        print()


# 上传的HTML文件路径
file_path = 'test.html'

# 分析HTML文件
analyze_html_file(file_path)
