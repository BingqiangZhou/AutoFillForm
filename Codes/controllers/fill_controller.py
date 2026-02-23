"""
Form filling controller - coordinates form filling automation with Playwright.
Migrated from Selenium to Playwright.
"""
import threading
import time
from tools.url_change_judge import wait_for_url_change
from automation.form_filler import FormFiller
from automation.verification import VerificationHandler
from automation.browser_setup import BrowserSetup


class FillController:
    """Controller for form filling operations using Playwright."""

    def __init__(self, model, view, rule_model, history_model, logger, rule_editor_controller=None):
        """
        Initialize the fill controller.

        Args:
            model: SurveyModel instance.
            view: FillView instance.
            rule_model: RuleModel instance.
            history_model: HistoryModel instance.
            logger: GuiLogger instance.
            rule_editor_controller: RuleEditorController instance (optional).
        """
        self.model = model
        self.view = view
        self.rule_model = rule_model
        self.history_model = history_model
        self.logger = logger
        self.rule_editor_controller = rule_editor_controller

        # State
        self.is_running = False
        self.stop_flag = threading.Event()
        self.current_session_id = None
        self.browser = None
        self.context = None
        self.page = None

        # Setup view callbacks
        self.setup_view_callbacks()

        # Get DPI ratio (lazy import to avoid win32 setting DPI awareness before Qt)
        from tools.windows_resolution import get_windows_scale_ratio
        self.ratio = get_windows_scale_ratio()

    def setup_view_callbacks(self):
        """Set up view button callbacks."""
        self.view.set_browse_command(self.browse_rule_file)
        self.view.set_start_command(self.start_fill)
        self.view.set_stop_command(self.stop_fill)

    def browse_rule_file(self):
        """Handle browse button click."""
        rules_dir = self.rule_model.get_rules_dir()
        file_path = self.view.ask_to_browse_rule_file(rules_dir)
        if file_path:
            # Get just the file name
            import os
            file_name = os.path.basename(file_path)
            self.load_rule_file(file_name)

    def load_rule_file(self, file_name):
        """Load a rule file and update the view."""
        rule_data = self.rule_model.load_rule(file_name)
        if rule_data:
            self.view.set_rule_file(file_name)
            self.view.set_url(self.rule_model.get_rule_url())
            self.view.set_fill_count(self.rule_model.get_rule_fill_count())
            self.model.set_last_rule_file(file_name)
            self.logger.info(f"已加载规则文件: {file_name}")

            # Also load the rule content into the rule editor for viewing/editing
            if self.rule_editor_controller:
                self.rule_editor_controller.load_rule_by_name(file_name)

            return True
        else:
            self.view.show_error("加载失败", f"无法加载规则文件: {file_name}")
            return False

    def log_callback(self, message):
        """Callback for logging to GUI."""
        self.view.append_log(message)

    def start_fill(self):
        """Start the form filling process."""
        # Validate configuration
        rule_file = self.view.get_rule_file()
        if not rule_file:
            self.view.show_error("错误", "请先选择规则文件")
            return

        url = self.view.get_url()
        if not url:
            self.view.show_error("错误", "规则文件中没有URL")
            return

        fill_count = self.view.get_fill_count()
        if fill_count < 1:
            self.view.show_error("错误", "填写数量必须大于0")
            return

        # Reset state
        self.stop_flag.clear()
        self.is_running = True
        self.view.set_running_state(True)
        self.view.clear_log()
        self.view.set_progress(0)

        # Set up logger callback
        self.logger.set_gui_callback(self.log_callback)

        # Create session
        self.current_session_id = self.history_model.add_session(
            rule_file, url, fill_count, "running"
        )

        # Start filling in background thread
        self.fill_thread = threading.Thread(target=self._fill_worker)
        self.fill_thread.daemon = True
        self.fill_thread.start()

    def stop_fill(self):
        """Stop the form filling process."""
        if self.is_running:
            self.stop_flag.set()
            self.logger.info("正在停止...")

    def check_is_running(self):
        """Check if filling is currently running."""
        return self.is_running

    def _fill_worker(self):
        """Worker thread for form filling with Playwright."""
        try:
            url = self.view.get_url()
            fill_count = self.view.get_fill_count()
            question_infos = self.rule_model.get_rule_rules()

            # Initialize form filler and verification handler
            form_filler = FormFiller(log_callback=self.logger.info)
            verification_handler = VerificationHandler(ratio=self.ratio)

            # Setup browser with Playwright
            self.logger.info("正在打开浏览器...")
            self.browser, self.context, self.page = BrowserSetup.setup_browser_for_fill()

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
                    # URL hasn't changed, might be verification
                    self.logger.info(f"触发了验证... ({fill_form_num}/{fill_count})")
                    self._handle_verification(verification_handler, window_title, old_url, fill_form_num)

                # Update progress
                progress = (fill_form_num / fill_count) * 100
                self.view.after(0, lambda p=progress: self.view.set_progress(p))

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
            # Clean up
            self._cleanup_browser()

            self.is_running = False
            self.logger.save_session_logs(self.current_session_id, self.history_model)
            self.view.after(0, lambda: self.view.set_running_state(False))

    def _cleanup_browser(self):
        """Clean up browser resources."""
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

                    # Wait for URL change
                    if not wait_for_url_change(self.page, old_url, timeout=5000):
                        # Check for slider verification
                        locator_slide = self.page.locator("span", has_text="请按住滑块，拖动到最右边")
                        if locator_slide.count() > 0:
                            handler.switch_window_to_edge(window_title)
                            self.logger.info(f"滑块验证... ({fill_num})")
                            handler.slider_verification(self.page, locator_slide)
                            wait_for_url_change(self.page, old_url, timeout=10000)

        except Exception as e:
            self.logger.error(f"验证处理失败: {e}")

    def has_unsaved_changes(self):
        """Return False - fill controller doesn't have persistent state."""
        return False
