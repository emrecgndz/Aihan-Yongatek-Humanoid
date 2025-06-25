# =======================
# modules/gui/styles/qt_styles.py - PyQt5 Stilleri
# =======================

# Dark Theme Stylesheet
DARK_THEME = """
/* Ana renk paleti */
QMainWindow {
    background-color: #2b2b2b;
    color: #ffffff;
}

/* Grup kutuları */
QGroupBox {
    font-weight: bold;
    border: 2px solid #555555;
    border-radius: 8px;
    margin: 8px;
    padding-top: 15px;
    color: #ffffff;
    background-color: #353535;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 8px 0 8px;
    color: #ffffff;
    font-size: 11pt;
}

/* Butonlar */
QPushButton {
    background-color: #404040;
    border: 2px solid #555555;
    padding: 8px 16px;
    border-radius: 6px;
    color: #ffffff;
    font-weight: bold;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #505050;
    border-color: #777777;
}

QPushButton:pressed {
    background-color: #606060;
    border-color: #888888;
}

QPushButton:disabled {
    background-color: #2a2a2a;
    border-color: #3a3a3a;
    color: #666666;
}

/* Özel buton stilleri */
QPushButton[buttonStyle="success"] {
    background-color: #2d5a2d;
    border-color: #4a7c4a;
}

QPushButton[buttonStyle="success"]:hover {
    background-color: #3d6a3d;
}

QPushButton[buttonStyle="warning"] {
    background-color: #7a5a2d;
    border-color: #9a7a4a;
}

QPushButton[buttonStyle="warning"]:hover {
    background-color: #8a6a3d;
}

QPushButton[buttonStyle="danger"] {
    background-color: #7a2d2d;
    border-color: #9a4a4a;
}

QPushButton[buttonStyle="danger"]:hover {
    background-color: #8a3d3d;
}

/* Checkbox'lar */
QCheckBox {
    color: #ffffff;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #555555;
    border-radius: 3px;
    background-color: #2b2b2b;
}

QCheckBox::indicator:checked {
    background-color: #4a7c4a;
    border-color: #6a9c6a;
}

QCheckBox::indicator:hover {
    border-color: #777777;
}

/* Radio butonlar */
QRadioButton {
    color: #ffffff;
    spacing: 8px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #555555;
    border-radius: 9px;
    background-color: #2b2b2b;
}

QRadioButton::indicator:checked {
    background-color: #4a7c4a;
    border-color: #6a9c6a;
}

/* Slider'lar */
QSlider::groove:horizontal {
    border: 1px solid #555555;
    height: 8px;
    background: #2b2b2b;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: #4a7c4a;
    border: 2px solid #6a9c6a;
    width: 20px;
    margin: -6px 0;
    border-radius: 10px;
}

QSlider::handle:horizontal:hover {
    background: #5a8c5a;
}

QSlider::sub-page:horizontal {
    background: #4a7c4a;
    border: 1px solid #555555;
    height: 8px;
    border-radius: 4px;
}

QSlider::add-page:horizontal {
    background: #555555;
    border: 1px solid #555555;
    height: 8px;
    border-radius: 4px;
}

/* Progress bar */
QProgressBar {
    border: 2px solid #555555;
    border-radius: 6px;
    text-align: center;
    background-color: #2b2b2b;
    color: #ffffff;
}

QProgressBar::chunk {
    background-color: #4a7c4a;
    border-radius: 4px;
}

/* SpinBox'lar */
QSpinBox, QDoubleSpinBox {
    padding: 4px;
    border: 2px solid #555555;
    border-radius: 4px;
    background-color: #2b2b2b;
    color: #ffffff;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #4a7c4a;
}

QSpinBox::up-button, QDoubleSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 20px;
    border-left: 1px solid #555555;
    border-bottom: 1px solid #555555;
    background-color: #404040;
}

QSpinBox::down-button, QDoubleSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 20px;
    border-left: 1px solid #555555;
    border-top: 1px solid #555555;
    background-color: #404040;
}

/* ComboBox */
QComboBox {
    border: 2px solid #555555;
    border-radius: 4px;
    padding: 4px 8px;
    background-color: #2b2b2b;
    color: #ffffff;
    min-width: 80px;
}

QComboBox:focus {
    border-color: #4a7c4a;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left: 1px solid #555555;
    background-color: #404040;
}

QComboBox::down-arrow {
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #ffffff;
}

QComboBox QAbstractItemView {
    border: 2px solid #555555;
    background-color: #2b2b2b;
    color: #ffffff;
    selection-background-color: #4a7c4a;
}

/* Text Edit ve Line Edit */
QTextEdit, QPlainTextEdit, QLineEdit {
    border: 2px solid #555555;
    border-radius: 4px;
    padding: 4px;
    background-color: #1e1e1e;
    color: #ffffff;
    selection-background-color: #4a7c4a;
}

QTextEdit:focus, QPlainTextEdit:focus, QLineEdit:focus {
    border-color: #4a7c4a;
}

/* Labels */
QLabel {
    color: #ffffff;
    background-color: transparent;
}

QLabel[labelStyle="title"] {
    font-size: 14pt;
    font-weight: bold;
    color: #ffffff;
}

QLabel[labelStyle="subtitle"] {
    font-size: 12pt;
    font-weight: bold;
    color: #cccccc;
}

QLabel[labelStyle="info"] {
    color: #4a7c4a;
}

QLabel[labelStyle="warning"] {
    color: #cc9900;
}

QLabel[labelStyle="error"] {
    color: #cc4444;
}

/* List Widget */
QListWidget {
    border: 2px solid #555555;
    border-radius: 4px;
    background-color: #1e1e1e;
    color: #ffffff;
    outline: none;
}

QListWidget::item {
    padding: 4px;
    border-bottom: 1px solid #333333;
}

QListWidget::item:selected {
    background-color: #4a7c4a;
}

QListWidget::item:hover {
    background-color: #3a3a3a;
}

/* Tree Widget */
QTreeWidget {
    border: 2px solid #555555;
    border-radius: 4px;
    background-color: #1e1e1e;
    color: #ffffff;
    outline: none;
}

QTreeWidget::item {
    padding: 2px;
}

QTreeWidget::item:selected {
    background-color: #4a7c4a;
}

QTreeWidget::item:hover {
    background-color: #3a3a3a;
}

/* Table Widget */
QTableWidget {
    border: 2px solid #555555;
    border-radius: 4px;
    background-color: #1e1e1e;
    color: #ffffff;
    gridline-color: #555555;
    outline: none;
}

QTableWidget::item {
    padding: 4px;
}

QTableWidget::item:selected {
    background-color: #4a7c4a;
}

QHeaderView::section {
    background-color: #404040;
    color: #ffffff;
    padding: 6px;
    border: 1px solid #555555;
    font-weight: bold;
}

/* Tab Widget */
QTabWidget::pane {
    border: 2px solid #555555;
    border-radius: 4px;
    background-color: #353535;
}

QTabBar::tab {
    background-color: #404040;
    border: 2px solid #555555;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    color: #ffffff;
}

QTabBar::tab:selected {
    background-color: #353535;
    border-bottom-color: #353535;
}

QTabBar::tab:hover {
    background-color: #505050;
}

/* Scroll Bar */
QScrollBar:vertical {
    background-color: #2b2b2b;
    width: 15px;
    border: none;
    border-radius: 7px;
}

QScrollBar::handle:vertical {
    background-color: #555555;
    border-radius: 7px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #666666;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}

QScrollBar:horizontal {
    background-color: #2b2b2b;
    height: 15px;
    border: none;
    border-radius: 7px;
}

QScrollBar::handle:horizontal {
    background-color: #555555;
    border-radius: 7px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #666666;
}

/* Menu Bar */
QMenuBar {
    background-color: #2b2b2b;
    color: #ffffff;
    border-bottom: 1px solid #555555;
}

QMenuBar::item {
    background-color: transparent;
    padding: 6px 12px;
}

QMenuBar::item:selected {
    background-color: #4a7c4a;
}

QMenu {
    background-color: #2b2b2b;
    color: #ffffff;
    border: 2px solid #555555;
    border-radius: 4px;
}

QMenu::item {
    padding: 6px 20px;
}

QMenu::item:selected {
    background-color: #4a7c4a;
}

/* Status Bar */
QStatusBar {
    background-color: #2b2b2b;
    color: #ffffff;
    border-top: 1px solid #555555;
}

/* Tool Tip */
QToolTip {
    background-color: #404040;
    color: #ffffff;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 4px;
}

/* Splitter */
QSplitter::handle {
    background-color: #555555;
}

QSplitter::handle:horizontal {
    width: 3px;
}

QSplitter::handle:vertical {
    height: 3px;
}

QSplitter::handle:pressed {
    background-color: #4a7c4a;
}
"""

# Light Theme Stylesheet
LIGHT_THEME = """
/* Ana renk paleti */
QMainWindow {
    background-color: #f5f5f5;
    color: #333333;
}

QGroupBox {
    font-weight: bold;
    border: 2px solid #cccccc;
    border-radius: 8px;
    margin: 8px;
    padding-top: 15px;
    color: #333333;
    background-color: #ffffff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 8px 0 8px;
    color: #333333;
    font-size: 11pt;
}

QPushButton {
    background-color: #ffffff;
    border: 2px solid #cccccc;
    padding: 8px 16px;
    border-radius: 6px;
    color: #333333;
    font-weight: bold;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #f0f0f0;
    border-color: #aaaaaa;
}

QPushButton:pressed {
    background-color: #e0e0e0;
    border-color: #999999;
}

/* Diğer kontroller için light theme stilleri buraya eklenebilir */
"""

# macOS Native Style (minimal custom styling)
MACOS_THEME = """
/* macOS için minimal özelleştirme */
QMainWindow {
    background-color: #ececec;
}

QGroupBox {
    font-weight: bold;
    border: 1px solid #cccccc;
    border-radius: 6px;
    margin: 6px;
    padding-top: 12px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px 0 5px;
}

QPushButton {
    border-radius: 4px;
    padding: 6px 12px;
    min-height: 16px;
}
"""

def apply_theme(app, theme_name="dark"):
    """Tema uygula"""
    if theme_name.lower() == "dark":
        app.setStyleSheet(DARK_THEME)
    elif theme_name.lower() == "light":
        app.setStyleSheet(LIGHT_THEME)
    elif theme_name.lower() == "macos":
        app.setStyleSheet(MACOS_THEME)
    else:
        # Varsayılan sistem teması
        app.setStyleSheet("")

def get_theme_list():
    """Mevcut temaları döndür"""
    return ["dark", "light", "macos", "system"]