"""
Workflow view - integrated analyze + configure + fill workflow.
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QLineEdit, QSpinBox, QPushButton, QProgressBar,
                              QTextEdit, QMessageBox, QGroupBox,
                              QTreeWidget, QTreeWidgetItem, QHeaderView)
from PySide6.QtCore import Signal, QObject, QMutex, QMutexLocker, Qt
from PySide6.QtGui import QFont


class WorkflowViewSignals(QObject):
    """Signals for thread-safe updates from worker threads."""

    log_append = Signal(str)
    progress_update = Signal(int)
    status_update = Signal(str)
    running_state_changed = Signal(bool)
    analysis_complete = Signal(object)


class WorkflowView(QWidget):
    """View for the integrated workflow tab (analyze + configure + fill)."""

    def __init__(self, parent_widget):
        super().__init__(parent_widget)

        parent_layout = QVBoxLayout(parent_widget)
        parent_layout.setContentsMargins(0, 0, 0, 0)
        parent_layout.addWidget(self)

        self.signals = WorkflowViewSignals()
        self._mutex = QMutex()
        self._running_state = False
        self.setup_ui()

    def setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Step 1: URL Input
        url_group = QGroupBox("Step 1: 问卷链接")
        url_layout = QHBoxLayout(url_group)
        url_layout.addWidget(QLabel("链接:"))
        self.link_edit = QLineEdit()
        self.link_edit.setPlaceholderText("请输入问卷链接...")
        url_layout.addWidget(self.link_edit)
        self.analyze_button = QPushButton("分析问卷")
        url_layout.addWidget(self.analyze_button)
        layout.addWidget(url_group)

        # Step 2: Questions Tree
        tree_group = QGroupBox("Step 2: 问题配置")
        tree_layout = QVBoxLayout(tree_group)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["#", "类型", "内容", "概率"])
        self.tree.setColumnCount(4)
        header = self.tree.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.tree.setColumnWidth(0, 70)
        self.tree.setColumnWidth(1, 100)
        self.tree.setColumnWidth(3, 120)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tree.setMinimumHeight(200)
        tree_layout.addWidget(self.tree)

        # Toolbar
        toolbar_layout = QHBoxLayout()
        self.equalize_button = QPushButton("均分概率")
        self.equalize_button.setFixedWidth(100)
        toolbar_layout.addWidget(self.equalize_button)
        self.reset_button = QPushButton("重置")
        self.reset_button.setFixedWidth(80)
        toolbar_layout.addWidget(self.reset_button)
        toolbar_layout.addStretch()
        tree_layout.addLayout(toolbar_layout)

        layout.addWidget(tree_group, 1)

        # Step 3: Fill Execution
        fill_group = QGroupBox("Step 3: 填写执行")
        fill_layout = QVBoxLayout(fill_group)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("填写数量:"))
        self.count_spinbox = QSpinBox()
        self.count_spinbox.setRange(1, 1000)
        self.count_spinbox.setValue(1)
        controls_layout.addWidget(self.count_spinbox)
        controls_layout.addStretch()
        self.start_button = QPushButton("开始填写")
        controls_layout.addWidget(self.start_button)
        self.stop_button = QPushButton("停止")
        self.stop_button.setEnabled(False)
        controls_layout.addWidget(self.stop_button)
        fill_layout.addLayout(controls_layout)

        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        self.status_label = QLabel("就绪")
        progress_layout.addWidget(self.status_label)
        fill_layout.addLayout(progress_layout)

        layout.addWidget(fill_group)

        # Log
        log_group = QGroupBox("日志")
        log_layout = QVBoxLayout(log_group)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setMaximumHeight(150)
        log_layout.addWidget(self.log_text)
        layout.addWidget(log_group)

        # Connect signals to slots
        self.signals.log_append.connect(self._append_log_slot)
        self.signals.progress_update.connect(self._set_progress_slot)
        self.signals.status_update.connect(self._set_status_slot)
        self.signals.running_state_changed.connect(self._set_running_state_slot)
        self.signals.analysis_complete.connect(self._analysis_complete_slot)

    # --- Command setters ---

    def set_analyze_command(self, command):
        self.analyze_button.clicked.connect(command)

    def set_start_command(self, command):
        self.start_button.clicked.connect(command)

    def set_stop_command(self, command):
        self.stop_button.clicked.connect(command)

    def set_equalize_command(self, command):
        self.equalize_button.clicked.connect(command)

    def set_reset_command(self, command):
        self.reset_button.clicked.connect(command)

    # --- Getters ---

    def get_survey_link(self):
        return self.link_edit.text().strip()

    def get_fill_count(self):
        return self.count_spinbox.value()

    def set_fill_count(self, count):
        self.count_spinbox.setValue(count)

    # --- Tree methods ---

    def populate_tree(self, parsed_questions, rules=None):
        """Populate the tree widget with parsed question data.

        Args:
            parsed_questions: List of parsed question dicts.
            rules: Optional list of rule dicts with saved probabilities.
                   When provided, restores saved probabilities instead of defaults.
        """
        self.clear_tree()

        type_to_rule = {
            '3': 'radio_selection',
            '7': 'dropdown_selection',
            '4': 'multiple_selection',
            '6': 'matrix_radio_selection',
            '1': 'blank_filling',
        }

        rule_index = 0  # Tracks position in rules list

        for q in parsed_questions:
            topic = q.get('topic', '?')
            q_type_code = q.get('type_code', '')
            q_type_name = q.get('type', '未知')
            q_text = q.get('text', '')
            rule_key = type_to_rule.get(q_type_code)

            if not rule_key:
                continue

            # Get saved rule for this question if available
            saved_rule = None
            if rules and rule_index < len(rules):
                saved_rule = rules[rule_index]
            rule_index += 1

            # Create question-level item
            q_item = QTreeWidgetItem(self.tree)
            q_item.setText(0, str(topic))
            q_item.setText(1, q_type_name)
            q_item.setText(2, q_text)
            q_item.setData(0, Qt.ItemDataRole.UserRole, {
                'role': 'question',
                'type_code': q_type_code,
                'rule_key': rule_key
            })

            if rule_key in ('radio_selection', 'multiple_selection', 'dropdown_selection'):
                options = q.get('options', [])
                count = len(options)

                # Extract saved probabilities if available
                saved_probs = None
                if saved_rule and rule_key in saved_rule:
                    saved_probs = saved_rule[rule_key]

                for idx, opt_text in enumerate(options):
                    opt_item = QTreeWidgetItem(q_item)
                    opt_item.setText(0, f"  选项{idx + 1}")
                    opt_item.setText(2, opt_text)
                    opt_item.setData(0, Qt.ItemDataRole.UserRole, {'role': 'option'})

                    spinbox = QSpinBox()
                    spinbox.setRange(0, 100)
                    spinbox.setSuffix("%")

                    if saved_probs and idx < len(saved_probs):
                        spinbox.setValue(saved_probs[idx])
                    elif rule_key in ('radio_selection', 'dropdown_selection') and count > 0:
                        base = 100 // count
                        rem = 100 % count
                        spinbox.setValue(base + (1 if idx < rem else 0))
                    else:
                        spinbox.setValue(50)
                    self.tree.setItemWidget(opt_item, 3, spinbox)

            elif rule_key == 'matrix_radio_selection':
                sub_questions = q.get('sub_questions', [])

                # Extract saved sub-probabilities if available
                saved_sub_probs = None
                if saved_rule and 'matrix_radio_selection' in saved_rule:
                    saved_sub_probs = saved_rule['matrix_radio_selection']

                for si, sub_q in enumerate(sub_questions):
                    sub_item = QTreeWidgetItem(q_item)
                    sub_item.setText(0, f"  子题{si + 1}")
                    sub_item.setText(2, sub_q.get('sub_question', ''))
                    sub_item.setData(0, Qt.ItemDataRole.UserRole, {'role': 'sub_question'})

                    opts = sub_q.get('options', [])
                    opt_count = len(opts)

                    # Get saved probs for this sub-question
                    saved_opts = None
                    if saved_sub_probs and si < len(saved_sub_probs):
                        saved_opts = saved_sub_probs[si]

                    for oi, opt_val in enumerate(opts):
                        opt_item = QTreeWidgetItem(sub_item)
                        opt_item.setText(0, f"    选项{opt_val}")
                        opt_item.setData(0, Qt.ItemDataRole.UserRole, {'role': 'matrix_option'})

                        spinbox = QSpinBox()
                        spinbox.setRange(0, 100)
                        spinbox.setSuffix("%")

                        if saved_opts and oi < len(saved_opts):
                            spinbox.setValue(saved_opts[oi])
                        elif opt_count > 0:
                            base = 100 // opt_count
                            rem = 100 % opt_count
                            spinbox.setValue(base + (1 if oi < rem else 0))
                        else:
                            spinbox.setValue(50)
                        self.tree.setItemWidget(opt_item, 3, spinbox)

                    sub_item.setExpanded(True)

            elif rule_key == 'blank_filling':
                # Check for saved text entries
                saved_texts = None
                saved_probs = None
                if saved_rule and 'blank_filling' in saved_rule:
                    data = saved_rule['blank_filling']
                    if isinstance(data, list) and len(data) == 2:
                        saved_texts, saved_probs = data

                if saved_texts and saved_probs:
                    for ti, (text, prob) in enumerate(zip(saved_texts, saved_probs)):
                        self._add_text_entry(q_item, text, prob)
                else:
                    # Default: 2 example entries
                    self._add_text_entry(q_item, '示例文本1', 50)
                    self._add_text_entry(q_item, '示例文本2', 50)

                # Add "add text" button
                add_item = QTreeWidgetItem(q_item)
                add_item.setData(0, Qt.ItemDataRole.UserRole, {'role': 'add_button'})
                add_btn = QPushButton("+ 添加文本")
                add_btn.setFlat(True)
                self.tree.setItemWidget(add_item, 2, add_btn)
                add_btn.clicked.connect(lambda checked, qi=q_item: self._add_text_entry(qi))

            q_item.setExpanded(True)

    def _add_text_entry(self, q_item, text='示例文本', prob=50):
        """Add a text entry child to a blank-filling question item."""
        # Count existing text entries
        text_count = 0
        add_btn_index = q_item.childCount()
        for i in range(q_item.childCount()):
            child_data = q_item.child(i).data(0, Qt.ItemDataRole.UserRole)
            if child_data and child_data.get('role') == 'text_entry':
                text_count += 1
            if child_data and child_data.get('role') == 'add_button':
                add_btn_index = i

        entry_item = QTreeWidgetItem()
        entry_item.setText(0, f"  文本{text_count + 1}")
        entry_item.setData(0, Qt.ItemDataRole.UserRole, {'role': 'text_entry'})

        q_item.insertChild(add_btn_index, entry_item)

        line_edit = QLineEdit(text)
        self.tree.setItemWidget(entry_item, 2, line_edit)

        spinbox = QSpinBox()
        spinbox.setRange(0, 100)
        spinbox.setValue(prob)
        spinbox.setSuffix("%")
        self.tree.setItemWidget(entry_item, 3, spinbox)

    def build_rules_from_tree(self):
        """Build rules list from the current tree widget state."""
        rules = []
        for i in range(self.tree.topLevelItemCount()):
            q_item = self.tree.topLevelItem(i)
            data = q_item.data(0, Qt.ItemDataRole.UserRole)
            if not data:
                continue
            rule_key = data.get('rule_key', '')

            if rule_key in ('radio_selection', 'multiple_selection', 'dropdown_selection'):
                probs = []
                for j in range(q_item.childCount()):
                    child = q_item.child(j)
                    spinbox = self.tree.itemWidget(child, 3)
                    if spinbox:
                        probs.append(spinbox.value())
                rules.append({rule_key: probs})

            elif rule_key == 'matrix_radio_selection':
                sub_probs = []
                for j in range(q_item.childCount()):
                    sub_item = q_item.child(j)
                    sub_data = sub_item.data(0, Qt.ItemDataRole.UserRole)
                    if sub_data and sub_data.get('role') == 'sub_question':
                        probs = []
                        for k in range(sub_item.childCount()):
                            opt_item = sub_item.child(k)
                            spinbox = self.tree.itemWidget(opt_item, 3)
                            if spinbox:
                                probs.append(spinbox.value())
                        sub_probs.append(probs)
                rules.append({'matrix_radio_selection': sub_probs})

            elif rule_key == 'blank_filling':
                texts = []
                probs = []
                for j in range(q_item.childCount()):
                    child = q_item.child(j)
                    child_data = child.data(0, Qt.ItemDataRole.UserRole)
                    if child_data and child_data.get('role') == 'text_entry':
                        line_edit = self.tree.itemWidget(child, 2)
                        spinbox = self.tree.itemWidget(child, 3)
                        if line_edit and spinbox:
                            texts.append(line_edit.text())
                            probs.append(spinbox.value())
                rules.append({'blank_filling': [texts, probs]})

        return rules

    def clear_tree(self):
        """Clear the tree widget."""
        self.tree.clear()

    def equalize_probabilities(self):
        """Set all probabilities to equal distribution."""
        for i in range(self.tree.topLevelItemCount()):
            q_item = self.tree.topLevelItem(i)
            data = q_item.data(0, Qt.ItemDataRole.UserRole)
            if not data:
                continue
            rule_key = data.get('rule_key', '')

            if rule_key in ('radio_selection', 'blank_filling', 'dropdown_selection'):
                spinboxes = []
                for j in range(q_item.childCount()):
                    child = q_item.child(j)
                    child_data = child.data(0, Qt.ItemDataRole.UserRole)
                    if child_data and child_data.get('role') in ('option', 'text_entry'):
                        spinbox = self.tree.itemWidget(child, 3)
                        if spinbox:
                            spinboxes.append(spinbox)
                if spinboxes:
                    base = 100 // len(spinboxes)
                    rem = 100 % len(spinboxes)
                    for idx, sb in enumerate(spinboxes):
                        sb.setValue(base + (1 if idx < rem else 0))

            elif rule_key == 'multiple_selection':
                for j in range(q_item.childCount()):
                    child = q_item.child(j)
                    spinbox = self.tree.itemWidget(child, 3)
                    if spinbox:
                        spinbox.setValue(50)

            elif rule_key == 'matrix_radio_selection':
                for j in range(q_item.childCount()):
                    sub_item = q_item.child(j)
                    sub_data = sub_item.data(0, Qt.ItemDataRole.UserRole)
                    if sub_data and sub_data.get('role') == 'sub_question':
                        spinboxes = []
                        for k in range(sub_item.childCount()):
                            opt_item = sub_item.child(k)
                            spinbox = self.tree.itemWidget(opt_item, 3)
                            if spinbox:
                                spinboxes.append(spinbox)
                        if spinboxes:
                            base = 100 // len(spinboxes)
                            rem = 100 % len(spinboxes)
                            for idx, sb in enumerate(spinboxes):
                                sb.setValue(base + (1 if idx < rem else 0))

    # --- Thread-safe update methods via signals ---

    def set_progress(self, value):
        self.signals.progress_update.emit(int(value))

    def _set_progress_slot(self, value):
        self.progress_bar.setValue(value)

    def set_status(self, status):
        self.signals.status_update.emit(status)

    def _set_status_slot(self, status):
        self.status_label.setText(status)

    def append_log(self, message):
        self.signals.log_append.emit(message)

    def _append_log_slot(self, message):
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(message + "\n")
        self.log_text.setTextCursor(cursor)
        self.log_text.ensureCursorVisible()

    def clear_log(self):
        self.log_text.clear()

    def set_running_state(self, is_running):
        self.signals.running_state_changed.emit(is_running)

    def _set_running_state_slot(self, is_running):
        with QMutexLocker(self._mutex):
            self._running_state = is_running
        if is_running:
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.analyze_button.setEnabled(False)
            self.link_edit.setEnabled(False)
        else:
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.analyze_button.setEnabled(True)
            self.link_edit.setEnabled(True)

    def check_is_running(self):
        with QMutexLocker(self._mutex):
            return self._running_state

    def _analysis_complete_slot(self, questions):
        self.populate_tree(questions)

    # --- Dialogs ---

    def show_info(self, title, message):
        QMessageBox.information(self, title, message)

    def show_error(self, title, message):
        QMessageBox.critical(self, title, message)

    def after(self, ms, callback):
        """Schedule a callback on the main thread (compatibility helper)."""
        from PySide6.QtCore import QTimer
        QTimer.singleShot(ms, callback)
