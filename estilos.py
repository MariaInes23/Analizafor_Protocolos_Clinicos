COLORES_TOKEN = {
    "PALABRA_RESERVADA":   "#E3B6B1",
    "IDENTIFICADOR":       "#FFE3D8",
    "NUM_ENTERO":          "#c9a0dc",
    "NUM_DECIMAL":         "#c9a0dc",
    "OPERADOR":            "#845162",
    "OPERADOR_RELACIONAL": "#845162",
    "DELIMITADOR":         "#E3B6B1",
    "FIN_SENTENCIA":       "#522C5D",
    "SIMBOLO_ESPECIAL":    "#845162",
    "BOOLEANO":            "#E3B6B1",
    "FECHA":               "#FFE3D8",
}

STYLE_DIALOGO = """
QDialog {
    background-color: #150016;
    color: #FFE3D8;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
    font-weight: 500;
}
QLabel {
    color: #E3B6B1;
    font-size: 12px;
    font-weight: 600;
}
QLineEdit, QComboBox, QSpinBox {
    background-color: #1e2030;
    color: #FFE3D8;
    border: 1px solid #522C5D;
    border-radius: 4px;
    padding: 5px 8px;
    font-size: 12px;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #E3B6B1;
}
QComboBox::drop-down {
    border: none;
}
QComboBox QAbstractItemView {
    background-color: #1e2030;
    color: #FFE3D8;
    selection-background-color: #522C5D;
    border: 1px solid #522C5D;
}
QSlider::groove:horizontal {
    background-color: #1e2030;
    height: 6px;
    border-radius: 3px;
    border: 1px solid #522C5D;
}
QSlider::handle:horizontal {
    background-color: #E3B6B1;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider::sub-page:horizontal {
    background-color: #522C5D;
    border-radius: 3px;
}
QPushButton {
    background-color: #1e2030;
    color: #E3B6B1;
    border: 1px solid #522C5D;
    border-radius: 5px;
    padding: 6px 18px;
    font-size: 12px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #522C5D;
    color: #FFE3D8;
}
QPushButton#btn_ok {
    background-color: #522C5D;
    color: #FFE3D8;
    border: none;
    font-weight: 700;
}
QPushButton#btn_ok:hover {
    background-color: #845162;
}
"""

STYLE_AYUDA = """
QDialog {
    background-color: #150016;
    color: #FFE3D8;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-weight: 500;
}
QTabWidget::pane {
    border: 1px solid #522C5D;
    background-color: #1e2030;
    border-radius: 4px;
}
QTabBar::tab {
    background-color: #150016;
    color: #845162;
    padding: 7px 16px;
    border: 1px solid #522C5D;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    font-size: 12px;
    font-weight: 600;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: #1e2030;
    color: #E3B6B1;
    border-bottom: 2px solid #E3B6B1;
}
QTabBar::tab:hover:!selected {
    background-color: #522C5D;
    color: #FFE3D8;
}
QScrollArea {
    background-color: #1e2030;
    border: none;
}
QScrollBar:vertical {
    background-color: #150016;
    width: 8px;
}
QScrollBar::handle:vertical {
    background-color: #522C5D;
    border-radius: 4px;
    min-height: 20px;
}
QLabel#seccion_ayuda {
    font-size: 13px;
    font-weight: 700;
    color: #E3B6B1;
    padding: 10px 0px 4px 0px;
}
QLabel#desc {
    font-size: 12px;
    font-weight: 500;
    color: #FFE3D8;
    padding: 2px 0px;
}
QLabel#mono {
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    font-weight: 600;
    color: #E3B6B1;
    background-color: #150016;
    padding: 8px 12px;
    border-radius: 4px;
    border: 1px solid #522C5D;
}
QPushButton#btn_cerrar {
    background-color: #522C5D;
    color: #FFE3D8;
    border: none;
    border-radius: 4px;
    padding: 6px 20px;
    font-size: 12px;
    font-weight: 700;
}
QPushButton#btn_cerrar:hover {
    background-color: #845162;
}
QTableWidget {
    background-color: #150016;
    border: 1px solid #522C5D;
    border-radius: 4px;
    gridline-color: #1e2030;
    font-size: 12px;
    font-weight: 500;
    color: #FFE3D8;
    alternate-background-color: #1e2030;
}
QTableWidget::item { padding: 4px 8px; border: none; }
QTableWidget::item:selected { background-color: #522C5D; color: #FFE3D8; }
QHeaderView::section {
    background-color: #1e2030;
    color: #E3B6B1;
    font-weight: 700;
    font-size: 11px;
    padding: 5px 8px;
    border: none;
    border-right: 1px solid #522C5D;
    border-bottom: 1px solid #522C5D;
}
"""

STYLE = """
QMainWindow, QWidget {
    background-color: #150016;
    color: #FFE3D8;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
    font-weight: 500;
}
QLabel#titulo {
    font-size: 19px;
    font-weight: 700;
    color: #E3B6B1;
    padding: 4px 0px;
}
QLabel#seccion {
    font-size: 12px;
    font-weight: 700;
    color: #E3B6B1;
    padding: 6px 0px 2px 0px;
}
QPlainTextEdit {
    background-color: #1e2030;
    border: 1px solid #522C5D;
    border-radius: 6px;
    padding: 8px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 13px;
    font-weight: 600;
    color: #FFE3D8;
    selection-background-color: #522C5D;
}
QPlainTextEdit:focus {
    border: 1px solid #E3B6B1;
}
QPushButton {
    background-color: #1e2030;
    color: #E3B6B1;
    border: 1px solid #522C5D;
    border-radius: 5px;
    padding: 7px 18px;
    font-size: 12px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #522C5D;
    color: #FFE3D8;
}
QPushButton#btn_analizar {
    background-color: #522C5D;
    color: #FFE3D8;
    border: none;
    padding: 7px 24px;
    font-weight: 700;
}
QPushButton#btn_analizar:hover {
    background-color: #845162;
}
QPushButton#btn_limpiar {
    color: #E3B6B1;
    border: 1px solid #845162;
}
QPushButton#btn_limpiar:hover {
    background-color: #1e2030;
    border-color: #E3B6B1;
}
QPushButton#btn_ayuda {
    background-color: #FFE3D8;
    color: #150016;
    border: none;
    border-radius: 5px;
    padding: 5px 14px;
    font-size: 12px;
    font-weight: 700;
}
QPushButton#btn_ayuda:hover {
    background-color: #E3B6B1;
    color: #150016;
}
QPushButton#btn_lexema {
    background-color: #1e2030;
    color: #E3B6B1;
    border: 1px solid #522C5D;
    border-radius: 5px;
    padding: 5px 14px;
    font-size: 12px;
    font-weight: 700;
}
QPushButton#btn_lexema:hover {
    background-color: #522C5D;
    color: #FFE3D8;
}
QPushButton#btn_vista {
    background-color: #1e2030;
    color: #E3B6B1;
    border: 1px solid #522C5D;
    border-radius: 5px;
    padding: 5px 14px;
    font-size: 12px;
    font-weight: 700;
}
QPushButton#btn_vista:hover {
    background-color: #522C5D;
    color: #FFE3D8;
}
QPushButton#btn_abrir {
    background-color: #1e2030;
    color: #E3B6B1;
    border: 1px solid #522C5D;
    border-radius: 5px;
    padding: 5px 14px;
    font-size: 12px;
    font-weight: 700;
}
QPushButton#btn_abrir:hover {
    background-color: #522C5D;
    color: #FFE3D8;
}
QTableWidget {
    background-color: #1e2030;
    border: 1px solid #522C5D;
    border-radius: 6px;
    gridline-color: #150016;
    font-size: 12px;
    font-weight: 600;
    color: #FFE3D8;
    selection-background-color: #522C5D;
    alternate-background-color: #1e0a30;
}
QTableWidget::item {
    padding: 4px 8px;
    border: none;
}
QTableWidget::item:selected {
    background-color: #522C5D;
    color: #FFE3D8;
}
QHeaderView::section {
    background-color: #150016;
    color: #E3B6B1;
    font-weight: 700;
    font-size: 12px;
    padding: 5px 8px;
    border: none;
    border-right: 1px solid #522C5D;
    border-bottom: 1px solid #522C5D;
}
QSplitter::handle {
    background-color: #522C5D;
    width: 2px;
}
QStatusBar {
    background-color: transparent;
    color: transparent;
    max-height: 0px;
    padding: 0px;
    border: none;
}
QFrame#linea {
    color: #522C5D;
}
QTabWidget#tabs_resultado::pane {
    border: 1px solid #522C5D;
    background-color: #1e2030;
    border-radius: 4px;
}
QTabWidget#tabs_resultado > QTabBar::tab {
    background-color: #150016;
    color: #845162;
    padding: 6px 18px;
    border: 1px solid #522C5D;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    font-size: 12px;
    font-weight: 600;
    margin-right: 2px;
}
QTabWidget#tabs_resultado > QTabBar::tab:selected {
    background-color: #1e2030;
    color: #E3B6B1;
    border-bottom: 2px solid #E3B6B1;
}
QTabWidget#tabs_resultado > QTabBar::tab:hover:!selected {
    background-color: #522C5D;
    color: #FFE3D8;
}
QPlainTextEdit#txt_arbol {
    background-color: #150016;
    border: 1px solid #522C5D;
    border-radius: 6px;
    padding: 10px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    color: #c9a0dc;
    selection-background-color: #522C5D;
}
QPlainTextEdit#txt_arbol:focus {
    border: 1px solid #E3B6B1;
}
"""
