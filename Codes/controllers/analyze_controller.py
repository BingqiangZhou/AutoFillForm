"""
Survey analysis controller - Migrated to Playwright.
"""
import threading
from bs4 import BeautifulSoup
from automation.browser_setup import BrowserSetup


class AnalyzeController:
    """Controller for survey analysis operations using Playwright."""

    def __init__(self, model, view, rule_model):
        """
        Initialize the analyze controller.

        Args:
            model: SurveyModel instance.
            view: AnalyzeView instance.
            rule_model: RuleModel instance (for export to YAML).
        """
        self.model = model
        self.view = view
        self.rule_model = rule_model
        self.browser = None
        self.context = None
        self.page = None

        # Setup view callbacks
        self.setup_view_callbacks()

    def setup_view_callbacks(self):
        """Set up view button callbacks."""
        self.view.set_analyze_command(self.analyze_survey)
        self.view.set_export_text_command(self.export_text)
        self.view.set_export_yaml_command(self.export_yaml)
        self.view.set_clear_command(self.clear_results)

    def analyze_survey(self):
        """Analyze the survey structure."""
        link = self.view.get_survey_link().strip()
        if not link:
            self.view.show_error("错误", "请输入问卷链接")
            return

        # Save link for next time
        self.model.set_survey_link(link)

        # Run analysis in background thread
        thread = threading.Thread(target=self._analyze_worker, args=(link,))
        thread.daemon = True
        thread.start()

    def _analyze_worker(self, link):
        """Worker thread for survey analysis with Playwright."""
        try:
            # Setup browser
            if self.page is None:
                self.browser, self.context, self.page = BrowserSetup.setup_browser_for_analysis()

            # Open survey
            self.page.goto(link, wait_until="domcontentloaded")

            # Wait for question div to load
            self.page.wait_for_selector('#divQuestion', timeout=10000)

            # Analyze
            page_content = self.page.content()
            results = self._analyze_survey_page(page_content)

            # Update UI (must be on main thread)
            self.view.after(0, lambda: self.view.display_results(results))

        except Exception as e:
            error_msg = f"分析问卷时出错: {e}"
            self.view.after(0, lambda: self.view.show_error("分析错误", error_msg))

    def _analyze_survey_page(self, page_content):
        """Analyze the survey page structure."""
        soup = BeautifulSoup(page_content, 'html.parser')
        form = soup.find('div', id='divQuestion')

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
                question['type_code'] = q_type
                question['text'] = div.find('div', class_='topichtml').text.strip()

                if q_type in ['3', '4']:
                    options = []
                    for label in div.find_all('div', class_='label'):
                        options.append(label.text.strip())
                    question['options'] = options
                    question['option_count'] = len(options)

                elif q_type == '7':
                    options = []
                    for option in div.find('select').find_all('option'):
                        options.append(option.text.strip())
                    question['options'] = options
                    question['option_count'] = len(options)

                elif q_type in ['1', '6']:
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

        # Format results
        results = ""
        for q in questions:
            results += f"问题 {q['topic']} ({q['type']}): {q['text']}\n"

            if 'options' in q:
                results += f"  选项数量: {q['option_count']}\n"

            if 'sub_questions' in q:
                results += f"  子问题数量: {q['sub_question_count']}\n"

            results += "\n"

        # Store parsed questions for YAML export
        self.parsed_questions = questions

        return results

    def export_text(self):
        """Export analysis results to text file."""
        results = self.view.get_results()
        if not results:
            self.view.show_info("提示", "没有可导出的内容")
            return

        file_path = self.view.ask_to_save_text()
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(results)
                self.view.show_info("导出成功", f"分析结果已保存到:\n{file_path}")
            except Exception as e:
                self.view.show_error("导出失败", f"保存文件时出错:\n{e}")

    def export_yaml(self):
        """Export analysis as YAML template."""
        if not hasattr(self, 'parsed_questions') or not self.parsed_questions:
            self.view.show_info("提示", "请先分析问卷")
            return

        # Generate YAML rules from parsed questions
        rules = []
        for q in self.parsed_questions:
            q_type = q['type_code']
            if q_type == '3':  # 单选题
                count = q.get('option_count', 2)
                probs = [100 // count] * count
                probs[-1] += 100 - sum(probs)  # Add remainder to last
                rules.append({'radio_selection': probs})

            elif q_type == '4':  # 多选题
                count = q.get('option_count', 2)
                probs = [50] * count
                rules.append({'multiple_selection': probs})

            elif q_type == '6':  # 矩阵题
                sub_count = q.get('sub_question_count', 1)
                option_count = 5  # Default for matrix
                probs = [0] * option_count
                probs[0] = probs[1] = 50
                rules.append({'matrix_radio_selection': [probs] * sub_count})

            elif q_type == '1':  # 填空题
                rules.append({'blank_filling': [['示例1', '示例2'], [50, 50]]})

            elif q_type == '7':  # 下拉题
                count = q.get('option_count', 2)
                probs = [100 // count] * count
                probs[-1] += 100 - sum(probs)
                rules.append({'radio_selection': probs})

        # Create template
        import yaml
        template = {
            'url': self.view.get_survey_link(),
            'number_of_questionnaires_to_be_filled_out': 1,
            'rules': rules
        }

        file_path = self.view.ask_to_save_yaml()
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(template, f, allow_unicode=True, default_flow_style=False)
                self.view.show_info("导出成功", f"YAML模板已保存到:\n{file_path}")
            except Exception as e:
                self.view.show_error("导出失败", f"保存文件时出错:\n{e}")

    def clear_results(self):
        """Clear the results display."""
        self.view.clear_results()

    def cleanup(self):
        """Clean up resources."""
        if self.page:
            try:
                self.page.close()
            except:
                pass
            self.page = None

        if self.context:
            try:
                self.context.close()
            except:
                pass
            self.context = None

        if self.browser:
            try:
                self.browser.close()
            except:
                pass
            self.browser = None

    def has_unsaved_changes(self):
        """Return False - analyze controller doesn't have persistent state."""
        return False
