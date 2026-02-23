"""
Lightweight Markdown to HTML renderer for Qt applications.

Supports common Markdown syntax:
- Headers (#, ##, ###, ####)
- Bold (**text**)
- Italic (*text*)
- Links ([text](url))
- Ordered/unordered lists
- Code blocks (```code``` and `inline code`)
- Horizontal rules (---)
"""
import html
import re


class MarkdownRenderer:
    """Lightweight Markdown to HTML converter with embedded CSS styles."""

    def __init__(self, text_color=None, background_color=None, link_color=None):
        """
        Initialize the renderer with optional custom colors.

        Args:
            text_color: Hex color code for text (e.g., "#000000")
            background_color: Hex color code for background (e.g., "#ffffff")
            link_color: Hex color code for links (e.g., "#0066cc")
        """
        self.text_color = text_color or "#000000"
        self.background_color = background_color or "#ffffff"
        self.link_color = link_color or "#0066cc"

    def _get_css_styles(self):
        """Generate CSS styles with configured colors."""
        return f"""
        <style>
            body {{
                font-family: 'Segoe UI', 'Microsoft YaHei UI', sans-serif;
                font-size: 13px;
                line-height: 1.7;
                color: {self.text_color};
                background-color: {self.background_color};
                margin: 0;
                padding: 8px;
            }}
            h1, h2, h3, h4, h5, h6 {{
                margin-top: 18px;
                margin-bottom: 10px;
                font-weight: 700;
                color: {self.text_color};
            }}
            h1 {{ font-size: 1.8em; border-bottom: 2px solid #cccccc; padding-bottom: 8px; margin-top: 8px; }}
            h2 {{ font-size: 1.5em; border-bottom: 1px solid #dddddd; padding-bottom: 6px; margin-top: 14px; }}
            h3 {{ font-size: 1.3em; margin-top: 12px; }}
            h4 {{ font-size: 1.15em; margin-top: 10px; }}
            p {{ margin: 10px 0; color: {self.text_color}; }}
            ul, ol {{ margin: 10px 0; padding-left: 28px; color: {self.text_color}; }}
            li {{ margin: 5px 0; }}
            code {{
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                background-color: #e8e8e8;
                color: #c7254e;
                padding: 3px 6px;
                border-radius: 4px;
                font-size: 0.9em;
                font-weight: 500;
            }}
            pre {{
                background-color: #f8f8f8;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 12px;
                margin: 12px 0;
                overflow-x: auto;
            }}
            pre code {{
                background-color: transparent;
                color: #333333;
                padding: 0;
                border-radius: 0;
                font-size: 0.9em;
                font-weight: 400;
            }}
            a {{
                color: {self.link_color};
                text-decoration: none;
                font-weight: 500;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            strong {{ font-weight: 700; color: {self.text_color}; }}
            em {{ font-style: italic; }}
            hr {{
                border: none;
                border-top: 1px solid #cccccc;
                margin: 18px 0;
            }}
            blockquote {{
                border-left: 4px solid #999999;
                margin: 12px 0;
                padding: 8px 0 8px 18px;
                background-color: #fafafa;
                color: {self.text_color};
            }}
        </style>
    """

    def render(self, markdown_text: str) -> str:
        """
        Convert Markdown text to HTML with embedded CSS.

        Args:
            markdown_text: Raw Markdown text from GitHub Releases API

        Returns:
            HTML string ready for QTextBrowser.setHtml()
        """
        if not markdown_text:
            return ""

        # Escape HTML entities first to prevent XSS
        text = html.escape(markdown_text)

        # Process in order to avoid conflicts
        text = self._render_code_blocks(text)
        text = self._render_headers(text)
        text = self._render_horizontal_rules(text)
        text = self._render_bold_italic(text)
        text = self._render_links(text)
        text = self._render_inline_code(text)
        text = self._render_lists(text)
        text = self._render_paragraphs(text)
        text = self._render_blockquotes(text)

        return f"<!DOCTYPE html><html><head>{self._get_css_styles()}</head><body>{text}</body></html>"

    def _render_code_blocks(self, text: str) -> str:
        """Render fenced code blocks (```code```)."""
        pattern = r'```(\w*)\n(.*?)```'

        def replace_code_block(match):
            lang = match.group(1)
            code = match.group(2)
            # Unescape HTML entities inside code blocks
            code = code.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
            return f'<pre><code>{code}</code></pre>'

        return re.sub(pattern, replace_code_block, text, flags=re.DOTALL)

    def _render_headers(self, text: str) -> str:
        """Render ATX-style headers (# ## ### ####)."""
        lines = text.split('\n')
        result = []

        for line in lines:
            # Check for header
            match = re.match(r'^(#{1,4})\s+(.*)$', line)
            if match:
                level = len(match.group(1))
                content = match.group(2).strip()
                result.append(f'<h{level}>{content}</h{level}>')
            else:
                result.append(line)

        return '\n'.join(result)

    def _render_horizontal_rules(self, text: str) -> str:
        """Render horizontal rules (---)."""
        return re.sub(r'^\s*-{3,}\s*$', '<hr>', text, flags=re.MULTILINE)

    def _render_bold_italic(self, text: str) -> str:
        """Render bold (**text**) and italic (*text*)."""
        # Bold first (must be before italic to avoid conflicts)
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        # Then italic
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        return text

    def _render_links(self, text: str) -> str:
        """Render links ([text](url))."""
        return re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', text)

    def _render_inline_code(self, text: str) -> str:
        """Render inline code (`code`)."""
        return re.sub(r'`([^`]+)`', r'<code>\1</code>', text)

    def _render_lists(self, text: str) -> str:
        """Render unordered (- *) and ordered (1.) lists."""
        lines = text.split('\n')
        result = []
        in_ul = False
        in_ol = False

        for line in lines:
            # Check for list item
            ul_match = re.match(r'^[\s]*[-*]\s+(.+)$', line)
            ol_match = re.match(r'^[\s]*(\d+)\.\s+(.+)$', line)

            if ul_match:
                if not in_ul:
                    if in_ol:
                        result.append('</ol>')
                        in_ol = False
                    result.append('<ul>')
                    in_ul = True
                content = ul_match.group(1)
                result.append(f'<li>{content}</li>')
            elif ol_match:
                if not in_ol:
                    if in_ul:
                        result.append('</ul>')
                        in_ul = False
                    result.append('<ol>')
                    in_ol = True
                content = ol_match.group(2)
                result.append(f'<li>{content}</li>')
            else:
                # Close any open lists
                if in_ul:
                    result.append('</ul>')
                    in_ul = False
                if in_ol:
                    result.append('</ol>')
                    in_ol = False
                result.append(line)

        # Close any remaining open lists
        if in_ul:
            result.append('</ul>')
        if in_ol:
            result.append('</ol>')

        return '\n'.join(result)

    def _render_paragraphs(self, text: str) -> str:
        """Wrap non-empty lines in <p> tags."""
        lines = text.split('\n')
        result = []

        for line in lines:
            stripped = line.strip()
            # Skip empty lines and HTML tags
            if not stripped or stripped.startswith('<'):
                result.append(line)
            else:
                result.append(f'<p>{line}</p>')

        return '\n'.join(result)

    def _render_blockquotes(self, text: str) -> str:
        """Render blockquotes (> text)."""
        lines = text.split('\n')
        result = []
        in_blockquote = False
        blockquote_content = []

        for line in lines:
            if line.startswith('&gt;') or (line.startswith('>')):
                content = line.lstrip('&gt;').lstrip('>').strip()
                blockquote_content.append(content)
                if not in_blockquote:
                    in_blockquote = True
            else:
                if in_blockquote:
                    result.append(f'<blockquote>{"".join(blockquote_content)}</blockquote>')
                    blockquote_content = []
                    in_blockquote = False
                result.append(line)

        if in_blockquote:
            result.append(f'<blockquote>{"".join(blockquote_content)}</blockquote>')

        return '\n'.join(result)
