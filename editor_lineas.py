from PyQt6.QtWidgets import QWidget, QPlainTextEdit, QTextEdit
from PyQt6.QtGui import QColor, QPainter, QFont, QTextFormat
from PyQt6.QtCore import Qt, QRect, QSize


class PanelLineas(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self._editor = editor

    def sizeHint(self):
        return QSize(self._editor._ancho_panel(), 0)

    def paintEvent(self, event):
        self._editor._pintar_panel(event)


class EditorConLineas(QPlainTextEdit):
    INDENT = "    "

    def __init__(self, parent=None):
        super().__init__(parent)
        self._panel = PanelLineas(self)
        self.blockCountChanged.connect(self._actualizar_ancho_panel)
        self.updateRequest.connect(self._actualizar_panel)
        self._actualizar_ancho_panel()

    def _ancho_panel(self):
        digitos = max(1, len(str(self.blockCount())))
        return 10 + self.fontMetrics().horizontalAdvance("9") * digitos

    def _actualizar_ancho_panel(self, _=0):
        self.setViewportMargins(self._ancho_panel(), 0, 0, 0)

    def _actualizar_panel(self, rect, dy):
        if dy:
            self._panel.scroll(0, dy)
        else:
            self._panel.update(0, rect.y(), self._panel.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self._actualizar_ancho_panel()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._panel.setGeometry(QRect(cr.left(), cr.top(), self._ancho_panel(), cr.height()))

    def _pintar_panel(self, event):
        painter = QPainter(self._panel)
        painter.fillRect(event.rect(), QColor("#150016"))
        bloque = self.firstVisibleBlock()
        num = bloque.blockNumber()
        top = int(self.blockBoundingGeometry(bloque).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(bloque).height())
        while bloque.isValid() and top <= event.rect().bottom():
            if bloque.isVisible() and bottom >= event.rect().top():
                painter.setPen(QColor("#522C5D"))
                painter.setFont(self.font())
                painter.drawText(
                    0, top,
                    self._panel.width() - 4, self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight,
                    str(num + 1)
                )
            bloque = bloque.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(bloque).height())
            num += 1

    def keyPressEvent(self, event):
        cursor = self.textCursor()
        key = event.key()

        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            linea = cursor.block().text()
            indent_actual = len(linea) - len(linea.lstrip(" "))
            espacios = " " * indent_actual
            if linea.rstrip().endswith("{"):
                espacios += self.INDENT
            super().keyPressEvent(event)
            self.textCursor().insertText(espacios)
            return

        if key == Qt.Key.Key_BraceRight:
            linea = cursor.block().text()
            solo_espacios = linea.strip() == ""
            if solo_espacios and len(linea) >= len(self.INDENT):
                cursor.movePosition(cursor.MoveOperation.StartOfBlock)
                cursor.movePosition(
                    cursor.MoveOperation.Right,
                    cursor.MoveMode.KeepAnchor,
                    len(self.INDENT)
                )
                cursor.removeSelectedText()
                self.setTextCursor(cursor)
            super().keyPressEvent(event)
            return

        super().keyPressEvent(event)
