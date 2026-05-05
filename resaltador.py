import re
from PyQt6.QtGui import QColor, QTextCharFormat, QSyntaxHighlighter
from tokens import PALABRAS_RESERVADAS


class Resaltador(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.reglas = []

        fmt_res = QTextCharFormat()
        fmt_res.setForeground(QColor("#E3B6B1"))
        fmt_res.setFontWeight(700)
        self.reglas.append((re.compile(r"\b(" + "|".join(PALABRAS_RESERVADAS) + r")\b"), fmt_res))

        fmt_bool = QTextCharFormat()
        fmt_bool.setForeground(QColor("#E3B6B1"))
        fmt_bool.setFontWeight(700)
        self.reglas.append((re.compile(r"\b(verdadero|falso)\b"), fmt_bool))

        fmt_num = QTextCharFormat()
        fmt_num.setForeground(QColor("#c9a0dc"))
        self.reglas.append((re.compile(r"\b\d+(\.\d+)?\b"), fmt_num))

        fmt_str = QTextCharFormat()
        fmt_str.setForeground(QColor("#FFE3D8"))
        self.reglas.append((re.compile(r'"[^"]*"'), fmt_str))

        fmt_op = QTextCharFormat()
        fmt_op.setForeground(QColor("#845162"))
        fmt_op.setFontWeight(700)
        self.reglas.append((re.compile(r"[+\-*/%%><!=]"), fmt_op))

        fmt_sim = QTextCharFormat()
        fmt_sim.setForeground(QColor("#E3B6B1"))
        self.reglas.append((re.compile(r"[();,.{}]"), fmt_sim))

    def highlightBlock(self, text):
        for patron, fmt in self.reglas:
            for m in patron.finditer(text):
                self.setFormat(m.start(), m.end() - m.start(), fmt)