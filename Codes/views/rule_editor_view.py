"""
YAML rule editor view - Migrated to PyQt6 with syntax highlighting.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTextEdit, QPlainTextEdit,
                             QFileDialog, QMessageBox, QFrame, QSplitter)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import (QFont, QTextCharFormat, QColor, QSyntaxHighlighter,
                         QTextDocument, QPainter, QTextCursor, QTextFormat)


class YamlSyntaxHighlighter(QSyntaxHighlighter):
    """Simple YAML syntax highlighter."""

    def __init__(self, document):
        super().__init__(document)

    def highlightBlock(self, text):
        """Apply syntax highlighting to a block of text."""
        # Key format (before colon)
        key_format = QTextCharFormat()
        key_format.setForeground(QColor("#0000ff"))  # Blue

        # Value format (after colon)
        value_format = QTextCharFormat()
        value_format.setForeground(QColor("#008000"))  # Green

        # Comment format
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#808080"))  # Gray

        # Check for comments
        if '#' in text:
            comment_pos = text.indexOf('#')
            # Check if # is inside a string (escaped or quoted)
            in_string = False
            escape_next = False
            for i in range(comment_pos):
                if text[i] == '\\' and not escape_next:
                    escape_next = True
                    continue
                if text[i] == '"' or text[i] == "'":
                    in_string = not in_string
                    escape_next = False
                    continue
                escape_next = False

            if not in_string:
                self.setFormat(comment_pos, len(text) - comment_pos, comment_format)
                text = text[:comment_pos]  # Only process text before comment

        # Check for key: value pairs
        colon_pos = text.indexOf(':')
        if colon_pos > 0:
            # Highlight key
            key = text[:colon_pos].strip()
            if key:
                self.setFormat(text.indexOf(key), len(key), key_format)

            # Highlight value (after colon)
            value_start = colon_pos + 1
            if value_start < len(text):
                value = text[value_start:].strip()
                if value and value not in ('|', '>', '-', '---'):
                    value_pos = text.indexOf(value, value_start)
                    if value_pos >= 0:
                        self.setFormat(value_pos, len(value), value_format)


class LineNumberArea(QWidget):
    """Line numbers sidebar widget."""

    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        """Return the recommended size."""
        return self.editor.line_number_area_width(), 0

    def paintEvent(self, event):
        """Paint the line numbers."""
        self.editor.line_number_area_paint_event(event)


class YamlEditor(QPlainTextEdit):
    """Text editor with line numbers for YAML."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        self.setFont(QFont("Consolas", 10))
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

        self.update_line_number_area_width(0)
        self.highlight_current_line()

    def line_number_area_width(self):
        """Calculate the width needed for line numbers."""
        digits = 1
        max_value = max(1, self.blockCount())
        while max_value >= 10:
            max_value /= 10
            digits += 1
        space = 3 + digits * self.fontMetrics().horizontalAdvance('9')
        return space

    def update_line_number_area_width(self, _):
        """Update the line number area width."""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        """Update the line number area."""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(),
                                       self.line_number_area.width(),
                                       rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        """Handle resize event."""
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            cr.left(), cr.top(),
            self.line_number_area_width(), cr.height()
        )

    def line_number_area_paint_event(self, event):
        """Paint the line numbers."""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#f0f0f0"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#666666"))
                painter.drawText(0, int(top), self.line_number_area.width(),
                               self.fontMetrics().height(), Qt.AlignmentFlag.AlignRight,
                               number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    def highlight_current_line(self):
        """Highlight the current line."""
        extra_selections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor QColor("#ffffcc")
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

        self.setExtraSelections(extra_selections)


class RuleEditorView(QWidget):
    """View for the YAML rule editor tab using PyQt6."""

    def __init__(self, parent_widget):
        """
        Initialize the rule editor view.

        Args:
            parent_widget: Parent widget to contain this view.
        """
        super().__init__(parent_widget)
        self._current_file = None
        self._modified = False
        self.setup_ui()

    @property
    def current_file(self):
        """Get the current file path."""
        return self._current_file

    @property
    def modified(self):
        """Get the modified flag."""
        return self._modified

    def setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Top toolbar
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(0, 0, 0, 5)

        self.new_button = QPushButton("新建")
        self.new_button.setFixedWidth(80)
        toolbar_layout.addWidget(self.new_button)

        self.open_button = QPushButton("打开")
        self.open_button.setFixedWidth(80)
        toolbar_layout.addWidget(self.open_button)

        self.save_button = QPushButton("保存")
        self.save_button.setFixedWidth(80)
        toolbar_layout.addWidget(self.save_button)

        self.save_as_button = QPushButton("另存为")
        self.save_as_button.setFixedWidth(80)
        toolbar_layout.addWidget(self.save_as_button)

        toolbar_layout.addSpacing(20)

        self.validate_button = QPushButton("验证语法")
        self.validate_button.setFixedWidth(80)
        toolbar_layout.addWidget(self.validate_button)

        self.template_button = QPushButton("从模板新建")
        self.template_button.setFixedWidth(100)
        toolbar_layout.addWidget(self.template_button)

        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)

        # File info
        info_layout = QHBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 5)

        self.file_label = QLabel("未打开文件")
        self.file_label.setStyleSheet("color: #666;")
        info_layout.addWidget(self.file_label)

        self.modified_label = QLabel()
        self.modified_label.setStyleSheet("color: red;")
        info_layout.addWidget(self.modified_label)

        info_layout.addStretch()
        layout.addLayout(info_layout)

        # Editor with line numbers
        self.editor = YamlEditor()
        self.highlighter = YamlSyntaxHighlighter(self.editor.document())
        self.editor.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.editor, 1)

        # Status bar
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("border-top: 1px solid #ccc; padding-top: 5px;")
        layout.addWidget(self.status_label)

    def set_button_command(self, button_name, command):
        """Set command for a toolbar button."""
        button_map = {
            "new": self.new_button,
            "open": self.open_button,
            "save": self.save_button,
            "save_as": self.save_as_button,
            "validate": self.validate_button,
            "template": self.template_button
        }
        if button_name in button_map:
            button_map[button_name].clicked.connect(command)

    def on_text_changed(self):
        """Handle text changed event."""
        if not self._modified:
            self._modified = True
            self.modified_label.setText("*")

    def get_content(self):
        """Get the editor content."""
        return self.editor.toPlainText()

    def set_content(self, content):
        """Set the editor content."""
        self.editor.setPlainText(content)
        self._modified = False
        self.modified_label.setText("")

    def new_file(self):
        """Create a new file."""
        if self._modified and not self.confirm_discard():
            return False
        self.editor.clear()
        self._current_file = None
        self._modified = False
        self.modified_label.setText("")
        self.file_label.setText("未打开文件")
        return True

    def open_file(self, file_path=None):
        """Open a file."""
        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "打开规则文件",
                "",
                "YAML files (*.yaml *.yml);;All files (*.*)"
            )
            if not file_path:
                return False

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.set_content(content)
            self._current_file = file_path
            self.file_label.setText(file_path)
            return True
        except Exception as e:
            QMessageBox.critical(self, "打开文件错误", f"无法打开文件:\n{e}")
            return False

    def save_file(self, file_path=None):
        """Save the current file."""
        if not file_path:
            if self.current_file:
                file_path = self.current_file
            else:
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "保存规则文件",
                    "",
                    "YAML files (*.yaml);;All files (*.*)"
                )
                if not file_path:
                    return False

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.get_content())
            self._current_file = file_path
            self._modified = False
            self.modified_label.setText("")
            self.file_label.setText(file_path)
            return True
        except Exception as e:
            QMessageBox.critical(self, "保存文件错误", f"无法保存文件:\n{e}")
            return False

    def confirm_discard(self):
        """Ask user to confirm discarding changes."""
        reply = QMessageBox.question(
            self,
            "未保存的更改",
            "当前文件有未保存的更改，是否继续？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes

    def set_status(self, message):
        """Set the status bar message."""
        self.status_label.setText(message)

    def show_validation_result(self, is_valid, message):
        """Show validation result in status bar."""
        if is_valid:
            self.set_status("验证通过 - " + message)
            QMessageBox.information(self, "验证结果", "YAML语法正确！")
        else:
            self.set_status("验证失败 - " + message)
            QMessageBox.critical(self, "验证结果", f"YAML语法错误:\n{message}")
