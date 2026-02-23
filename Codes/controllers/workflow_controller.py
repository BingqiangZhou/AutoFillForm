"""
Workflow controller - merges analyze + fill into an integrated workflow.
"""
import threading
import time
from bs4 import BeautifulSoup
from tools.url_change_judge import wait_for_url_change
from automation.form_filler import FormFiller
from automation.verification import VerificationHandler
from automation.browser_setup import BrowserSetup


class WorkflowController:
    """Controller for the integrated workflow: analyze -> configure -> fill."""

    def __init__(self, model, view, rule_model, history_model, logger):
        self.model = model
        self.view = view
        self.rule_model = rule_model
        self.history_model = history_model
        self.logger = logger

        # Analysis state
        self.analysis_playwright_instance = None
        self.analysis_browser = None
        self.analysis_context = None
        self.analysis_page = None
        self.parsed_questions = []

        # Fill state
        self.is_running = False
        self.stop_flag = threading.Event()
        self.current_session_id = None
        self.current_rules = None
        self.playwright_instance = None
        self.browser = None
        self.context = None
        self.page = None

        # DPI ratio
        from tools.screen_resolution import get_scale_ratio
        self.ratio = get_scale_ratio()

        # Load saved link if available
        saved_link = self.model.get_survey_link()
        if saved_link:
            self.view.link_edit.setText(saved_link)

        self.setup_view_callbacks()

    def setup_view_callbacks(self):
        """Set up view button callbacks."""
        self.view.set_analyze_command(self.analyze_survey)
        self.view.set_start_command(self.start_fill)
        self.view.set_stop_command(self.stop_fill)
        self.view.set_equalize_command(self.equalize_probabilities)
        self.view.set_reset_command(self.reset_tree)

    # --- Analysis ---

    def analyze_survey(self):
        """Start survey analysis in a background thread."""
        link = self.view.get_survey_link()
        if not link:
            self.view.show_error("错误", "请输入问卷链接")
            return

        self.model.set_survey_link(link)
        self.view.analyze_button.setEnabled(False)
        self.view.set_status("正在分析问卷...")
        self.view.append_log("开始分析问卷...")

        thread = threading.Thread(target=self._analyze_worker, args=(link,))
        thread.daemon = True
        thread.start()

    def _analyze_worker(self, link):
        """Worker thread for survey analysis with Playwright."""
        try:
            if self.analysis_page is None:
                self.analysis_playwright_instance, self.analysis_browser, self.analysis_context, self.analysis_page = \
                    BrowserSetup.setup_browser_for_analysis()

            self.analysis_page.goto(link, wait_until="domcontentloaded")
            self.analysis_page.wait_for_selector('#divQuestion', timeout=10000)
            page_content = self.analysis_page.content()
            questions = self._analyze_survey_page(page_content)
            self.parsed_questions = questions

            if questions:
                self.view.signals.analysis_complete.emit(questions)
                self.view.append_log(f"分析完成，共发现 {len(questions)} 个问题")
            else:
                self.view.append_log("未找到问题，请确认链接是否正确")

        except Exception as e:
            error_msg = str(e)
            self.view.after(0, lambda: self.view.show_error("分析错误", f"分析问卷时出错: {error_msg}"))
            self.view.append_log(f"分析失败: {error_msg}")

        finally:
            try:
                self._cleanup_analysis_browser()
            except Exception:
                pass
            self.view.after(0, lambda: self.view.analyze_button.setEnabled(True))
            self.view.set_status("就绪")

    def _analyze_survey_page(self, page_content):
        """Analyze the survey page structure using BeautifulSoup."""
        soup = BeautifulSoup(page_content, 'html.parser')
        form = soup.find('div', id='divQuestion')

        if not form:
            return []

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
                    select_el = div.find('select')
                    if select_el:
                        for option in select_el.find_all('option'):
                            val = option.get('value', '').strip()
                            if val:  # 过滤掉 value 为空的占位选项
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

                elif q_type == '1':
                    pass  # Fill-in-blank: no options to parse from HTML

                questions.append(question)

        return questions

    # --- Fill ---

    def log_callback(self, message):
        """Callback for logging to GUI."""
        self.view.append_log(message)

    def start_fill(self):
        """Start the form filling process."""
        url = self.view.get_survey_link()
        if not url:
            self.view.show_error("错误", "请输入问卷链接")
            return

        rules = self.view.build_rules_from_tree()
        if not rules:
            self.view.show_error("错误", "请先分析问卷并配置规则")
            return

        fill_count = self.view.get_fill_count()
        if fill_count < 1:
            self.view.show_error("错误", "填写数量必须大于0")
            return

        # Snapshot values for worker thread (thread safety)
        self._fill_url = url
        self._fill_count = fill_count
        self.current_rules = rules

        # Reset state
        self.stop_flag.clear()
        self.is_running = True
        self.view.set_running_state(True)
        self.view.clear_log()
        self.view.set_progress(0)

        # Set up logger callback
        self.logger.set_gui_callback(self.log_callback)

        # Create history session with parsed questions and rules
        self.current_session_id = self.history_model.add_session(
            "workflow", url, fill_count, "running",
            parsed_questions=self.parsed_questions,
            rules=rules,
        )

        # Start filling in background thread
        self.fill_thread = threading.Thread(target=self._fill_worker)
        self.fill_thread.daemon = True
        self.fill_thread.start()

    def _fill_worker(self):
        """Worker thread for form filling with Playwright."""
        try:
            url = self._fill_url
            fill_count = self._fill_count
            question_infos = self.current_rules

            form_filler = FormFiller(log_callback=self.logger.info)
            verification_handler = VerificationHandler(ratio=self.ratio)

            self.logger.info("正在打开浏览器...")
            self.playwright_instance, self.browser, self.context, self.page = BrowserSetup.setup_browser_for_fill()

            fill_form_num = 0
            window_title = None

            while fill_form_num < fill_count and not self.stop_flag.is_set():
                fill_form_num += 1

                self.logger.info(f"正在打开网页... ({fill_form_num}/{fill_count})")
                self.page.goto(url, wait_until="domcontentloaded")

                if window_title is None:
                    window_title = self.page.title()

                self.logger.info(f"填写问题... ({fill_form_num}/{fill_count})")
                success = form_filler.fill_questions(
                    self.page,
                    question_infos,
                    delay=0.2
                )

                if not success:
                    self.logger.warning(f"第{fill_form_num}份问卷填写时出现问题")
                    continue

                # Submit form
                self.page.locator('.submitbtn').click()
                self.logger.info(f"提交问卷... ({fill_form_num}/{fill_count})")
                time.sleep(2)

                # Check for verification
                old_url = url
                if not wait_for_url_change(self.page, old_url, timeout=3000):
                    self.logger.info(f"触发了验证... ({fill_form_num}/{fill_count})")
                    self._handle_verification(verification_handler, window_title, old_url, fill_form_num)

                # Update progress
                progress = (fill_form_num / fill_count) * 100
                self.view.set_progress(progress)

            # Update final status
            if self.stop_flag.is_set():
                self.logger.info(f"填写已停止，已完成{fill_form_num}/{fill_count}份问卷")
                self.history_model.update_session_status(self.current_session_id, "stopped")
            else:
                self.logger.info(f"问卷已填写{fill_count}份，任务完成")
                self.history_model.update_session_status(self.current_session_id, "completed")

        except Exception as e:
            self.logger.error(f"填写过程中出错: {e}")
            self.history_model.update_session_status(self.current_session_id, "error")

        finally:
            self._cleanup_fill_browser()
            self.is_running = False
            self.logger.save_session_logs(self.current_session_id, self.history_model)
            self.view.set_running_state(False)

    def stop_fill(self):
        """Stop the form filling process."""
        if self.is_running:
            self.stop_flag.set()
            self.logger.info("正在停止...")

    def _handle_verification(self, handler, window_title, old_url, fill_num):
        """Handle verification challenges."""
        try:
            locator = self.page.locator(".sm-txt")
            if locator.count() > 0:
                text = locator.inner_text()
                if text == "点击按钮开始智能验证":
                    handler.switch_window_to_edge(window_title)
                    self.logger.info(f"智能验证... ({fill_num})")
                    handler.intelligent_verification(self.page, locator)

                    if not wait_for_url_change(self.page, old_url, timeout=5000):
                        locator_slide = self.page.locator("span", has_text="请按住滑块，拖动到最右边")
                        if locator_slide.count() > 0:
                            handler.switch_window_to_edge(window_title)
                            self.logger.info(f"滑块验证... ({fill_num})")
                            handler.slider_verification(self.page, locator_slide)
                            wait_for_url_change(self.page, old_url, timeout=10000)

        except Exception as e:
            self.logger.error(f"验证处理失败: {e}")

    def _cleanup_fill_browser(self):
        """Clean up fill browser resources."""
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

        if self.playwright_instance:
            try:
                self.playwright_instance.stop()
            except:
                pass
            self.playwright_instance = None

    def _cleanup_analysis_browser(self):
        """Clean up analysis browser resources."""
        if self.analysis_page:
            try:
                self.analysis_page.close()
            except:
                pass
            self.analysis_page = None

        if self.analysis_context:
            try:
                self.analysis_context.close()
            except:
                pass
            self.analysis_context = None

        if self.analysis_browser:
            try:
                self.analysis_browser.close()
            except:
                pass
            self.analysis_browser = None

        if self.analysis_playwright_instance:
            try:
                self.analysis_playwright_instance.stop()
            except:
                pass
            self.analysis_playwright_instance = None

    # --- Restore ---

    def restore_session(self, session):
        """Restore a saved session's survey configuration into the workflow."""
        parsed_questions = session.get("parsed_questions")
        rules = session.get("rules")
        url = session.get("url", "")

        if url:
            self.view.link_edit.setText(url)
            self.model.set_survey_link(url)

        self.parsed_questions = parsed_questions
        self.view.populate_tree(parsed_questions, rules)
        self.view.append_log(f"已恢复会话 {session.get('id', '')} 的问卷配置")

    # --- Tree helpers ---

    def equalize_probabilities(self):
        """Equalize all probabilities in the tree."""
        self.view.equalize_probabilities()

    def reset_tree(self):
        """Reset the tree to the last analysis results."""
        if self.parsed_questions:
            self.view.populate_tree(self.parsed_questions)
        else:
            self.view.show_info("提示", "没有可重置的数据，请先分析问卷")

    # --- Lifecycle ---

    def cleanup(self):
        """Clean up all browser resources."""
        self._cleanup_analysis_browser()
        self._cleanup_fill_browser()

    def check_is_running(self):
        """Check if filling is currently running."""
        return self.is_running

    def has_unsaved_changes(self):
        """Return False - workflow controller doesn't have persistent state."""
        return False
