"""
AutoFillForm – Modern Dark Theme Stylesheet (QSS)

Provides a unified color palette and get_global_stylesheet() that returns
ready-to-use QSS applied once in app.py.
"""

# ── Color Palette ──────────────────────────────────────────────────────
BG_DARKEST   = "#16161E"   # window / main background
BG_DARK      = "#1E1E2E"   # cards, group boxes
BG_MID       = "#2A2A3C"   # input fields, tree items
BG_LIGHT     = "#363649"   # hover states
BORDER       = "#3E3E52"   # subtle borders
BORDER_FOCUS = "#3B82F6"   # focused input border

TEXT_PRIMARY   = "#E4E4EF"
TEXT_SECONDARY = "#9898AD"
TEXT_DISABLED  = "#5C5C72"

PRIMARY        = "#3B82F6"
PRIMARY_HOVER  = "#2563EB"
PRIMARY_PRESS  = "#1D4ED8"

SUCCESS        = "#10B981"
SUCCESS_HOVER  = "#059669"
SUCCESS_PRESS  = "#047857"

DANGER         = "#EF4444"
DANGER_HOVER   = "#DC2626"
DANGER_PRESS   = "#B91C1C"

WARNING        = "#F59E0B"

ACCENT         = "#8B5CF6"

SCROLLBAR_BG   = "#1E1E2E"
SCROLLBAR_FG   = "#4A4A5E"
SCROLLBAR_HOVER = "#5E5E76"

import os
import tempfile

# Cache generated arrow icon paths
_arrow_icon_cache = {}


def _generate_arrow_icons():
    """Generate small triangle arrow PNG images for QSpinBox buttons."""
    if _arrow_icon_cache:
        return _arrow_icon_cache

    from PySide6.QtGui import QPainter, QColor, QPolygonF, QImage
    from PySide6.QtCore import QPointF, Qt

    icon_dir = os.path.join(tempfile.gettempdir(), "autofillform_icons")
    os.makedirs(icon_dir, exist_ok=True)

    def _make_arrow(filename, color_hex, direction):
        img = QImage(10, 8, QImage.Format.Format_ARGB32)
        img.fill(Qt.GlobalColor.transparent)
        painter = QPainter(img)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(color_hex))
        painter.setPen(Qt.PenStyle.NoPen)
        if direction == "up":
            poly = QPolygonF([QPointF(5, 1), QPointF(9, 7), QPointF(1, 7)])
        else:
            poly = QPolygonF([QPointF(1, 1), QPointF(9, 1), QPointF(5, 7)])
        painter.drawPolygon(poly)
        painter.end()
        path = os.path.join(icon_dir, filename)
        img.save(path, "PNG")
        return path.replace("\\", "/")

    _arrow_icon_cache["up"] = _make_arrow("arrow_up.png", TEXT_SECONDARY, "up")
    _arrow_icon_cache["down"] = _make_arrow("arrow_down.png", TEXT_SECONDARY, "down")
    _arrow_icon_cache["up_hover"] = _make_arrow("arrow_up_hover.png", PRIMARY, "up")
    _arrow_icon_cache["down_hover"] = _make_arrow("arrow_down_hover.png", PRIMARY, "down")
    return _arrow_icon_cache


def get_global_stylesheet() -> str:
    """Return the complete QSS stylesheet string."""
    arrows = _generate_arrow_icons()
    up_arrow_path = arrows["up"]
    down_arrow_path = arrows["down"]
    up_arrow_hover_path = arrows["up_hover"]
    down_arrow_hover_path = arrows["down_hover"]
    return f"""
    /* ── Global ────────────────────────────────────────────── */
    QMainWindow, QWidget {{
        background-color: {BG_DARKEST};
        color: {TEXT_PRIMARY};
        font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
        font-size: 13px;
    }}

    /* ── QTabWidget ────────────────────────────────────────── */
    QTabWidget::pane {{
        border: none;
        background-color: {BG_DARKEST};
    }}
    QTabBar {{
        background-color: {BG_DARKEST};
    }}
    QTabBar::tab {{
        background-color: transparent;
        color: {TEXT_SECONDARY};
        padding: 10px 24px;
        margin-right: 2px;
        border: none;
        border-bottom: 3px solid transparent;
        font-size: 13px;
        font-weight: 500;
    }}
    QTabBar::tab:selected {{
        color: {PRIMARY};
        border-bottom: 3px solid {PRIMARY};
        background-color: transparent;
    }}
    QTabBar::tab:hover:!selected {{
        color: {TEXT_PRIMARY};
        background-color: rgba(59, 130, 246, 0.08);
    }}

    /* ── QGroupBox ─────────────────────────────────────────── */
    QGroupBox {{
        background-color: {BG_DARK};
        border: 1px solid {BORDER};
        border-radius: 8px;
        margin-top: 14px;
        padding: 16px 12px 12px 12px;
        font-weight: 600;
        font-size: 13px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 2px 12px;
        color: {TEXT_SECONDARY};
    }}

    /* ── QPushButton (default / secondary) ─────────────────── */
    QPushButton {{
        background-color: {BG_MID};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 6px 14px;
        font-size: 13px;
        min-height: 20px;
    }}
    QPushButton:hover {{
        background-color: {BG_LIGHT};
        border-color: #4E4E66;
    }}
    QPushButton:pressed {{
        background-color: {BG_MID};
    }}
    QPushButton:disabled {{
        background-color: {BG_DARK};
        color: {TEXT_DISABLED};
        border-color: {BORDER};
    }}
    QPushButton:flat {{
        background-color: transparent;
        border: none;
        color: {PRIMARY};
    }}
    QPushButton:flat:hover {{
        color: {PRIMARY_HOVER};
        background-color: rgba(59, 130, 246, 0.12);
        border-radius: 6px;
    }}

    /* ── Primary button ────────────────────────────────────── */
    QPushButton[class="primary"] {{
        background-color: {PRIMARY};
        color: #FFFFFF;
        border: none;
        font-weight: 600;
    }}
    QPushButton[class="primary"]:hover {{
        background-color: {PRIMARY_HOVER};
    }}
    QPushButton[class="primary"]:pressed {{
        background-color: {PRIMARY_PRESS};
    }}
    QPushButton[class="primary"]:disabled {{
        background-color: #1E3A5F;
        color: #5A7A9F;
    }}

    /* ── Success button ────────────────────────────────────── */
    QPushButton[class="success"] {{
        background-color: {SUCCESS};
        color: #FFFFFF;
        border: none;
        font-weight: 600;
    }}
    QPushButton[class="success"]:hover {{
        background-color: {SUCCESS_HOVER};
    }}
    QPushButton[class="success"]:pressed {{
        background-color: {SUCCESS_PRESS};
    }}
    QPushButton[class="success"]:disabled {{
        background-color: #1A3A2A;
        color: #5A9A7A;
    }}

    /* ── Danger button ─────────────────────────────────────── */
    QPushButton[class="danger"] {{
        background-color: {DANGER};
        color: #FFFFFF;
        border: none;
        font-weight: 600;
    }}
    QPushButton[class="danger"]:hover {{
        background-color: {DANGER_HOVER};
    }}
    QPushButton[class="danger"]:pressed {{
        background-color: {DANGER_PRESS};
    }}
    QPushButton[class="danger"]:disabled {{
        background-color: #3A1A1A;
        color: #9A5A5A;
    }}

    /* ── QLineEdit ─────────────────────────────────────────── */
    QLineEdit {{
        background-color: {BG_MID};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 13px;
        selection-background-color: {PRIMARY};
    }}
    QLineEdit:focus {{
        border-color: {PRIMARY};
    }}
    QLineEdit:disabled {{
        background-color: {BG_DARK};
        color: {TEXT_DISABLED};
    }}

    /* ── QSpinBox ──────────────────────────────────────────── */
    QSpinBox {{
        background-color: {BG_MID};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 4px 24px 4px 8px;
        font-size: 13px;
    }}
    QSpinBox:focus {{
        border-color: {PRIMARY};
    }}
    QSpinBox::up-button {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        background-color: transparent;
        border: none;
        border-left: 1px solid {BORDER};
        border-top-right-radius: 5px;
        width: 20px;
    }}
    QSpinBox::down-button {{
        subcontrol-origin: padding;
        subcontrol-position: bottom right;
        background-color: transparent;
        border: none;
        border-left: 1px solid {BORDER};
        border-bottom-right-radius: 5px;
        width: 20px;
    }}
    QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
        background-color: rgba(59, 130, 246, 0.15);
    }}
    QSpinBox::up-arrow {{
        image: url({up_arrow_path});
        width: 8px;
        height: 6px;
    }}
    QSpinBox::down-arrow {{
        image: url({down_arrow_path});
        width: 8px;
        height: 6px;
    }}
    QSpinBox::up-arrow:hover {{
        image: url({up_arrow_hover_path});
    }}
    QSpinBox::down-arrow:hover {{
        image: url({down_arrow_hover_path});
    }}

    /* ── QTextEdit / QPlainTextEdit ────────────────────────── */
    QTextEdit, QPlainTextEdit {{
        background-color: {BG_MID};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 6px;
        selection-background-color: {PRIMARY};
    }}
    QTextEdit:focus, QPlainTextEdit:focus {{
        border-color: {PRIMARY};
    }}

    /* ── QTextBrowser ──────────────────────────────────────── */
    QTextBrowser {{
        background-color: {BG_MID};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 8px;
    }}

    /* ── QProgressBar ──────────────────────────────────────── */
    QProgressBar {{
        background-color: {BG_MID};
        border: none;
        border-radius: 5px;
        min-height: 10px;
        max-height: 10px;
        text-align: center;
        color: transparent;
        font-size: 1px;
    }}
    QProgressBar::chunk {{
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:0,
            stop:0 {PRIMARY}, stop:1 {ACCENT}
        );
        border-radius: 5px;
    }}

    /* ── QTreeWidget ───────────────────────────────────────── */
    QTreeWidget {{
        background-color: {BG_MID};
        alternate-background-color: {BG_DARK};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 6px;
        outline: none;
        font-size: 13px;
    }}
    QTreeWidget::item {{
        padding: 4px 2px;
        border: none;
    }}
    QTreeWidget::item:selected {{
        background-color: rgba(59, 130, 246, 0.2);
        color: {TEXT_PRIMARY};
    }}
    QTreeWidget::item:hover:!selected {{
        background-color: rgba(59, 130, 246, 0.08);
    }}
    QTreeWidget::branch {{
        background-color: transparent;
    }}

    /* ── QHeaderView ───────────────────────────────────────── */
    QHeaderView::section {{
        background-color: {BG_DARK};
        color: {TEXT_SECONDARY};
        border: none;
        border-bottom: 1px solid {BORDER};
        padding: 6px 8px;
        font-weight: 600;
        font-size: 12px;
    }}
    QHeaderView::section:first {{
        border-top-left-radius: 6px;
    }}
    QHeaderView::section:last {{
        border-top-right-radius: 6px;
    }}

    /* ── QScrollBar (Vertical) ─────────────────────────────── */
    QScrollBar:vertical {{
        background-color: {SCROLLBAR_BG};
        width: 8px;
        margin: 0;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background-color: {SCROLLBAR_FG};
        border-radius: 4px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background-color: {SCROLLBAR_HOVER};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: none;
    }}

    /* ── QScrollBar (Horizontal) ───────────────────────────── */
    QScrollBar:horizontal {{
        background-color: {SCROLLBAR_BG};
        height: 8px;
        margin: 0;
        border-radius: 4px;
    }}
    QScrollBar::handle:horizontal {{
        background-color: {SCROLLBAR_FG};
        border-radius: 4px;
        min-width: 30px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background-color: {SCROLLBAR_HOVER};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0;
    }}
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
        background: none;
    }}

    /* ── QStatusBar ────────────────────────────────────────── */
    QStatusBar {{
        background-color: {BG_DARK};
        color: {TEXT_SECONDARY};
        border-top: 1px solid {BORDER};
        font-size: 12px;
        padding: 2px 8px;
    }}
    QStatusBar QLabel {{
        color: {TEXT_SECONDARY};
        font-size: 12px;
    }}

    /* ── QLabel ─────────────────────────────────────────────── */
    QLabel {{
        color: {TEXT_PRIMARY};
        background-color: transparent;
    }}

    /* ── QScrollArea ───────────────────────────────────────── */
    QScrollArea {{
        background-color: transparent;
        border: none;
    }}

    /* ── QMessageBox ───────────────────────────────────────── */
    QMessageBox {{
        background-color: {BG_DARK};
    }}
    QMessageBox QLabel {{
        color: {TEXT_PRIMARY};
    }}

    /* ── QDialog ───────────────────────────────────────────── */
    QDialog {{
        background-color: {BG_DARK};
        border-radius: 12px;
    }}

    /* ── Tooltip ───────────────────────────────────────────── */
    QToolTip {{
        background-color: {BG_LIGHT};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 4px;
        padding: 4px 8px;
    }}

    /* ── QFileDialog ───────────────────────────────────────── */
    QFileDialog {{
        background-color: {BG_DARK};
    }}
    """
