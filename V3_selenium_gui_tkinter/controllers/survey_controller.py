# survey_controller.py

# controller.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from tkinter import messagebox
from views import LoadingWindow
import threading

class SurveyController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.set_analyze_command(self.analyze_survey)
        self.driver = None

    def setup_browser(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        # options.add_argument("--no-sandbox")
        # options.add_argument("--disable-dev-shm-usage")
        service = EdgeService(EdgeChromiumDriverManager().install())
        self.driver = webdriver.Edge(service=service, options=options)
        self.driver.implicitly_wait(10)  # 设置隐性等待时间为10秒

        # 不让网页发现是在模拟状态下，在模拟状态下，智能验证通不过
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        })

    def analyze_survey(self):
        loading_window = LoadingWindow(self.view.root, message="正在配置浏览器，请稍候...")

        def configure_browser_and_analyze():
            try:
                if self.driver is None:
                    self.setup_browser()
                link = self.view.get_survey_link().strip()
                self.model.set_survey_link(link)  # 保存新链接
                
                loading_window.update_message("正在分析问卷，请稍候...")
                # loading_window.update_message("正在打开问卷链接，请稍候...")
                page_source = self.open_survey_link(link)
                
                # loading_window.update_message("正在分析问卷，请稍候...")
                results = self.analyze_survey_page(page_source)
                
                self.view.display_results(results)
            except Exception as e:
                messagebox.showerror("错误", f"分析问卷时出错: {e}")
            finally:
                loading_window.close()
                if self.driver:
                    self.driver.quit()
                    self.driver = None

        threading.Thread(target=configure_browser_and_analyze).start()

    def open_survey_link(self, link):
        self.driver.get(link)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'divQuestion'))
        )
        return self.driver.page_source

    def analyze_survey_page(self, page_source):
        soup = BeautifulSoup(page_source, 'html.parser')
        form = soup.find('div', id='divQuestion')
        return self.extract_questions(form)

    def extract_questions(self, form):
        if not form:
            return "无法找到问卷内容。"

        question_types = {
            '1': '填空题',
            '3': '单选题',
            '4': '多选题',
            '6': '矩阵单选题/矩阵量表题',
            '7': '下拉选择题'
        }

        questions = []

        for fieldset in form.find_all('fieldset'):
            for div in fieldset.find_all('div', class_='field'):
                question = {}
                topic = div.get('topic')
                q_type = div.get('type')
                question['topic'] = topic
                question['type'] = question_types.get(q_type, '未知类型')
                question['text'] = div.find('div', class_='topichtml').text.strip()

                if q_type in ['3', '4']:
                    options = []
                    for label in div.find_all('div', class_='label'):
                        options.append(label.text.strip())
                    question['options'] = options
                elif q_type == '7':
                    options = []
                    for option in div.find('select').find_all('option'):
                        options.append(option.text.strip())
                    question['options'] = options
                elif q_type in ['1', '6']:
                    sub_questions = []
                    for row in div.find_all('tr', class_='rowtitle'):
                        sub_question = row.find('span', class_='itemTitleSpan').text.strip()
                        options = []
                        next_row = row.find_next_sibling('tr')
                        if next_row:
                            for opt in next_row.find_all('a'):
                                options.append(opt.get('dval'))
                        sub_questions.append({'sub_question': sub_question, 'options': options})
                    question['sub_questions'] = sub_questions

                questions.append(question)

        results = ""
        for question in questions:
            results += f"问题 {question['topic']} ({question['type']}): {question['text']}\n"
            if 'options' in question:
                for option in question['options']:
                    results += f"  - {option}\n"
            if 'sub_questions' in question:
                for sub_question in question['sub_questions']:
                    results += f"  - 子问题: {sub_question['sub_question']}\n"
                    for option in sub_question['options']:
                        results += f"    - {option}\n"
            results += "\n"

        return results
