"""
Survey Auto-Filler Script for Claude Skill
Bundled script that integrates form filling functionality.
"""
import random
import time
import os
import sys
import platform
import subprocess
import shutil
from typing import List, Dict, Tuple, Callable, Optional, Any

# Fix UTF-8 encoding on Windows
if platform.system() == "Windows":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add the Codes directory to the path
# Script is at: .claude/skills/auto-fill-survey/scripts/survey_auto_filler.py
# Codes is at: Codes/
# Navigate up from scripts to project root, then to Codes
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))
codes_dir = os.path.join(project_root, 'Codes')
if os.path.exists(codes_dir):
    sys.path.insert(0, codes_dir)

try:
    from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
    from bs4 import BeautifulSoup
    import pyautogui
    PLAYWRIGHT_AVAILABLE = True
except ImportError as e:
    PLAYWRIGHT_AVAILABLE = False
    IMPORT_ERROR = str(e)


class SurveyAnalyzer:
    """Analyzes survey structure using Playwright and BeautifulSoup."""

    QUESTION_TYPES = {
        '1': '填空题',
        '3': '单选题',
        '4': '多选题',
        '6': '矩阵单选题',
        '7': '下拉选择题'
    }

    def __init__(self):
        self.playwright_instance = None
        self.browser = None
        self.page = None

    def analyze(self, url: str) -> List[Dict]:
        """
        Analyze survey structure from URL.

        Args:
            url: Survey URL to analyze

        Returns:
            List of question dictionaries
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError(f"Required dependencies not available: {IMPORT_ERROR}")

        try:
            self.playwright_instance = sync_playwright().start()
            self.browser = self.playwright_instance.chromium.launch(headless=True)
            self.page = self.browser.new_page()

            self.page.goto(url, wait_until="domcontentloaded")
            self.page.wait_for_selector('#divQuestion', timeout=10000)
            content = self.page.content()

            questions = self._parse_survey_content(content)
            return questions

        except Exception as e:
            raise Exception(f"分析问卷失败: {e}")
        finally:
            self._cleanup()

    def _parse_survey_content(self, content: str) -> List[Dict]:
        """Parse survey HTML content using BeautifulSoup."""
        soup = BeautifulSoup(content, 'html.parser')
        form = soup.find('div', id='divQuestion')

        if not form:
            return []

        questions = []
        for fieldset in form.find_all('fieldset'):
            for div in fieldset.find_all('div', class_='field'):
                question = {}
                topic = div.get('topic')
                q_type = div.get('type')
                question['topic'] = topic
                question['type'] = self.QUESTION_TYPES.get(q_type, '未知类型')
                question['type_code'] = q_type
                question['text'] = div.find('div', class_='topichtml').text.strip()

                if q_type in ['3', '4']:  # Single/Multiple choice
                    options = []
                    for label in div.find_all('div', class_='label'):
                        options.append(label.text.strip())
                    question['options'] = options
                    question['option_count'] = len(options)

                elif q_type == '7':  # Dropdown
                    options = []
                    select_el = div.find('select')
                    if select_el:
                        for option in select_el.find_all('option'):
                            val = option.get('value', '').strip()
                            if val:
                                options.append(option.text.strip())
                    question['options'] = options
                    question['option_count'] = len(options)

                elif q_type == '6':  # Matrix
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

                elif q_type == '1':  # Fill-in-blank
                    pass

                questions.append(question)

        return questions

    def _cleanup(self):
        """Clean up browser resources."""
        if self.page:
            try:
                self.page.close()
            except:
                pass
        if self.browser:
            try:
                self.browser.close()
            except:
                pass
        if self.playwright_instance:
            try:
                self.playwright_instance.stop()
            except:
                pass


class FormFiller:
    """Handles form filling operations."""

    def __init__(self, log_callback: Optional[Callable] = None):
        self.log_callback = log_callback or (lambda msg: None)

    def log(self, message: str):
        """Log a message."""
        self.log_callback(message)

    def radio_selection(self, page, probabilities: List[int], question_index: int):
        """Handle single-choice questions."""
        total = sum(probabilities)
        rand = random.randint(1, total)
        cumulative = 0
        for i, prob in enumerate(probabilities):
            cumulative += prob
            if rand <= cumulative:
                option_id = f'q{question_index}_{i + 1}'
                css = f"#{option_id} + a.jqradio"
                page.locator(css).click()
                break

    def multiple_selection(self, page, probabilities: List[int], question_index: int):
        """Handle multi-choice questions."""
        select_option_num = 0
        for i, prob in enumerate(probabilities):
            if random.randint(1, 100) <= prob:
                option_id = f'q{question_index}_{i + 1}'
                css = f"#{option_id} + a.jqcheck"
                page.locator(css).click()
                select_option_num += 1

        if select_option_num == 0:
            max_value = max(probabilities)
            max_index = probabilities.index(max_value)
            option_id = f'q{question_index}_{max_index + 1}'
            css = f"#{option_id} + a.jqcheck"
            page.locator(css).click()

    def matrix_radio_selection(self, page, probabilities_list: List[List[int]], question_index: int):
        """Handle matrix single-choice questions."""
        for i, probabilities in enumerate(probabilities_list):
            total = sum(probabilities)
            rand = random.randint(1, total)
            cumulative = 0
            option_id = f'drv{question_index}_{i + 1}'
            for j, prob in enumerate(probabilities):
                cumulative += prob
                if rand <= cumulative:
                    css = f"#{option_id} a[dval='{j + 1}']"
                    page.locator(css).click()
                    break

    def blank_filling(self, page, info_list: List, question_index: int):
        """Handle fill-in-blank questions."""
        text_list = info_list[0]
        probabilities_list = info_list[1]
        total = sum(probabilities_list)
        rand = random.randint(1, total)
        cumulative = 0
        option_id = f'q{question_index}'
        css = f"#{option_id}"
        for j, prob in enumerate(probabilities_list):
            cumulative += prob
            if rand <= cumulative:
                page.locator(css).fill(text_list[j])
                break

    def dropdown_selection(self, page, probabilities: List[int], question_index: int):
        """Handle dropdown questions."""
        total = sum(probabilities)
        rand = random.randint(1, total)
        cumulative = 0
        for i, prob in enumerate(probabilities):
            cumulative += prob
            if rand <= cumulative:
                css = f"#q{question_index}"
                page.locator(css).select_option(value=str(i + 1))
                break

    def fill_questions(self, page, question_infos: List[Dict], delay: float = 0.2) -> bool:
        """Fill all questions based on configuration."""
        try:
            for index, dicts in enumerate(question_infos):
                key, value = list(dicts.items())[0]
                if key == "multiple_selection":
                    self.multiple_selection(page, value, index + 1)
                elif key == "radio_selection":
                    self.radio_selection(page, value, index + 1)
                elif key == "matrix_radio_selection":
                    self.matrix_radio_selection(page, value, index + 1)
                elif key == "blank_filling":
                    self.blank_filling(page, value, index + 1)
                elif key == "dropdown_selection":
                    self.dropdown_selection(page, value, index + 1)
                else:
                    self.log(f"Unknown question type: {key}")
                time.sleep(delay)
            return True
        except Exception as e:
            self.log(f"Error filling questions: {e}")
            return False


class BrowserSetup:
    """Browser configuration with anti-detection."""

    @staticmethod
    def _detect_channel() -> Optional[str]:
        """Auto-detect available browser."""
        system = platform.system()

        # Edge detection
        if system == "Windows":
            edge_paths = [
                os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
                os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
            ]
            if shutil.which("msedge") or any(os.path.isfile(p) for p in edge_paths):
                return "msedge"
        elif system == "Darwin":
            mac_edge = "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
            if os.path.isfile(mac_edge) or shutil.which("msedge"):
                return "msedge"
        else:  # Linux
            if shutil.which("microsoft-edge-stable") or shutil.which("microsoft-edge") or shutil.which("msedge"):
                return "msedge"

        # Chrome detection
        if system == "Windows":
            chrome_paths = [
                os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            ]
            if shutil.which("chrome") or any(os.path.isfile(p) for p in chrome_paths):
                return "chrome"
        elif system == "Darwin":
            mac_chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            if os.path.isfile(mac_chrome) or shutil.which("google-chrome"):
                return "chrome"
        else:  # Linux
            if shutil.which("google-chrome") or shutil.which("google-chrome-stable") or shutil.which("chromium-browser") or shutil.which("chromium"):
                return "chrome"

        return None

    @staticmethod
    def setup_browser(headless: bool = False, channel: str = "auto") -> Tuple:
        """Setup browser with anti-detection measures."""
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError(f"Required dependencies not available: {IMPORT_ERROR}")

        if channel == "auto":
            channel = BrowserSetup._detect_channel()

        playwright_instance = sync_playwright().start()

        launch_kwargs = dict(
            headless=headless,
            args=['--disable-blink-features=AutomationControlled'],
        )
        if channel is not None:
            launch_kwargs["channel"] = channel

        browser = playwright_instance.chromium.launch(**launch_kwargs)

        user_agent = (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36'
        )

        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=user_agent,
            locale='zh-CN'
        )

        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            window.chrome = {
                runtime: {}
            };
        """)

        page = context.new_page()
        page.set_default_timeout(10000)
        page.set_default_navigation_timeout(30000)

        return playwright_instance, browser, context, page


def get_scale_ratio() -> float:
    """Get Windows DPI scaling ratio."""
    try:
        import ctypes
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        dc = user32.GetDC(0)
        LOGPIXELSX = 88
        scale = ctypes.windll.gdi32.GetDeviceCaps(dc, LOGPIXELSX) / 96.0
        user32.ReleaseDC(0, dc)
        return scale
    except:
        return 1.0


def wait_for_url_change(page, old_url: str, timeout: int = 3000) -> bool:
    """Wait for URL to change after form submission."""
    try:
        start_time = time.time()
        while (time.time() - start_time) * 1000 < timeout:
            current_url = page.url
            if current_url != old_url:
                return True
            time.sleep(0.1)
        return False
    except:
        return False


class SurveyAutoFiller:
    """Main class for survey auto-filling workflow."""

    def __init__(self, log_callback: Optional[Callable] = None):
        self.log_callback = log_callback or print
        self.analyzer = SurveyAnalyzer()
        self.filler = FormFiller(log_callback=log_callback)
        self.ratio = get_scale_ratio()

    def analyze_survey(self, url: str) -> List[Dict]:
        """Analyze survey structure."""
        self.log_callback("正在分析问卷结构...")
        questions = self.analyzer.analyze(url)
        self.log_callback(f"分析完成，发现 {len(questions)} 个问题")
        return questions

    def format_questions(self, questions: List[Dict]) -> str:
        """Format questions for display."""
        lines = ["分析完成！发现以下问题：\n"]
        for i, q in enumerate(questions, 1):
            lines.append(f"{i}. [{q['type']}] {q['text']}")
            if 'options' in q:
                lines.append(f"   选项: {', '.join(q['options'])}")
            elif 'sub_questions' in q:
                lines.append(f"   子问题: {q['sub_question_count']}个")
            lines.append("")
        return "\n".join(lines)

    def create_default_rules(self, questions: List[Dict]) -> List[Dict]:
        """Create default probability rules from analyzed questions."""
        rules = []
        for q in questions:
            q_type = q['type_code']
            if q_type == '3':  # Single choice
                count = q.get('option_count', 2)
                rules.append({'radio_selection': [50] * count})
            elif q_type == '4':  # Multiple choice
                count = q.get('option_count', 2)
                rules.append({'multiple_selection': [30] * count})
            elif q_type == '6':  # Matrix
                sub_count = q.get('sub_question_count', 1)
                rules.append({'matrix_radio_selection': [[50, 50, 0, 0]] * sub_count})
            elif q_type == '1':  # Fill-in-blank
                rules.append({'blank_filling': [["满意", "一般", "不满意"], [50, 30, 20]]})
            elif q_type == '7':  # Dropdown
                count = q.get('option_count', 2)
                rules.append({'dropdown_selection': [50] * count})
        return rules

    def equalize_rules(self, rules: List[Dict]) -> List[Dict]:
        """Equalize all probabilities in rules."""
        result = []
        for rule in rules:
            for key, value in rule.items():
                if key == 'blank_filling':
                    text_list = value[0]
                    equal_prob = 100 // len(text_list)
                    result.append({key: [text_list, [equal_prob] * len(text_list)]})
                elif key == 'matrix_radio_selection':
                    equal_prob = 100 // len(value[0])
                    result.append({key: [[equal_prob] * len(v) for v in value]})
                else:
                    equal_prob = 100 // len(value)
                    result.append({key: [equal_prob] * len(value)})
        return result

    def fill_survey(self, url: str, rules: List[Dict], fill_count: int = 1,
                    progress_callback: Optional[Callable] = None) -> Dict:
        """
        Fill survey with given rules.

        Returns:
            Dict with success status and details
        """
        if not PLAYWRIGHT_AVAILABLE:
            return {
                'success': False,
                'error': f"Required dependencies not available: {IMPORT_ERROR}"
            }

        self.log_callback("正在启动浏览器...")
        playwright_instance, browser, context, page = BrowserSetup.setup_browser(headless=False)

        try:
            filled_count = 0
            errors = []

            for i in range(fill_count):
                current_num = i + 1
                self.log_callback(f"正在填写第 {current_num}/{fill_count} 份问卷...")

                try:
                    page.goto(url, wait_until="domcontentloaded")
                    time.sleep(1)

                    # Fill questions
                    success = self.filler.fill_questions(page, rules, delay=0.2)
                    if not success:
                        errors.append(f"第{current_num}份填写失败")
                        continue

                    # Submit
                    page.locator('.submitbtn').click()
                    self.log_callback(f"已提交第 {current_num}/{fill_count} 份问卷")
                    time.sleep(2)

                    # Check for verification
                    old_url = page.url
                    if not wait_for_url_change(page, old_url, timeout=3000):
                        self.log_callback(f"第{current_num}份触发验证，请手动处理...")
                        self.log_callback("按Enter键继续下一份...")
                        input()

                    filled_count += 1
                    if progress_callback:
                        progress_callback((current_num / fill_count) * 100)

                except Exception as e:
                    errors.append(f"第{current_num}份出错: {str(e)}")
                    self.log_callback(f"第{current_num}份出错: {e}")

            return {
                'success': True,
                'filled_count': filled_count,
                'total_count': fill_count,
                'errors': errors
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            # Cleanup
            try:
                page.close()
                context.close()
                browser.close()
                playwright_instance.stop()
            except:
                pass


# CLI interface for testing
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Survey Auto-Filler')
    parser.add_argument('url', help='Survey URL')
    parser.add_argument('--count', type=int, default=1, help='Number of surveys to fill')
    parser.add_argument('--analyze-only', action='store_true', help='Only analyze survey structure')

    args = parser.parse_args()

    filler = SurveyAutoFiller()

    if args.analyze_only:
        questions = filler.analyze_survey(args.url)
        print(filler.format_questions(questions))
    else:
        questions = filler.analyze_survey(args.url)
        print(filler.format_questions(questions))

        rules = filler.create_default_rules(questions)
        result = filler.fill_survey(args.url, rules, args.count)

        if result['success']:
            print(f"\n填写完成！成功: {result['filled_count']}/{result['total_count']}")
            if result['errors']:
                print("错误:", result['errors'])
        else:
            print(f"\n填写失败: {result.get('error', 'Unknown error')}")
