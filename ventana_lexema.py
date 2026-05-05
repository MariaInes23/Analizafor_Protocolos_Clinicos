from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt
from estilos import STYLE_DIALOGO
from config import cargar_lexemas_extra, guardar_lexemas_extra

CATEGORIAS = [
    "PALABRA_RESERVADA",
    "OPERADOR",
    "OPERADOR_RELACIONAL",
    "DELIMITADOR",
    "SIMBOLO_ESPECIAL",
    "IDENTIFICADOR",
]

_CLAVE = "admin"


class DialogoClave(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Autenticacion requerida")
        self.setFixedSize(320, 160)
        self.setStyleSheet(STYLE_DIALOGO)
        self.aprobado = False
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(12)
        lay.addWidget(QLabel("Ingresa la contrasena de administrador:"))
        self._campo = QLineEdit()
        self._campo.setEchoMode(QLineEdit.EchoMode.Password)
        self._campo.returnPressed.connect(self._verificar)
        lay.addWidget(self._campo)
        btns = QHBoxLayout()
        btn_ok = QPushButton("Aceptar")
        btn_ok.setObjectName("btn_ok")
        btn_ok.clicked.connect(self._verificar)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btns.addStretch()
        btns.addWidget(btn_cancel)
        btns.addWidget(btn_ok)
        lay.addLayout(btns)

    def _verificar(self):
        if self._campo.text() == _CLAVE:
            self.aprobado = True
            self.accept()
        else:
            QMessageBox.warning(self, "Acceso denegado", "Contrasena incorrecta.")
            self._campo.clear()


class DialogoAgregarLexema(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agregar Lexema")
        self.setFixedSize(380, 260)
        self.setStyleSheet(STYLE_DIALOGO)
        self.guardado = False
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(10)

        lay.addWidget(QLabel("Lexema:"))
        self._lexema = QLineEdit()
        self._lexema.setPlaceholderText("Ej: DIAGNOSTICO")
        lay.addWidget(self._lexema)

        lay.addWidget(QLabel("Categoria:"))
        self._categoria = QComboBox()
        self._categoria.addItems(CATEGORIAS)
        lay.addWidget(self._categoria)

        lay.addWidget(QLabel("Descripcion:"))
        self._descripcion = QLineEdit()
        self._descripcion.setPlaceholderText("Ej: Accion de diagnostico medico")
        lay.addWidget(self._descripcion)

        btns = QHBoxLayout()
        btn_guardar = QPushButton("Guardar")
        btn_guardar.setObjectName("btn_ok")
        btn_guardar.clicked.connect(self._guardar)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btns.addStretch()
        btns.addWidget(btn_cancel)
        btns.addWidget(btn_guardar)
        lay.addLayout(btns)

    def _guardar(self):
        lexema = self._lexema.text().strip().upper()
        descripcion = self._descripcion.text().strip()
        if not lexema:
            QMessageBox.warning(self, "Campo vacio", "El lexema no puede estar vacio.")
            return
        if not descripcion:
            QMessageBox.warning(self, "Campo vacio", "La descripcion no puede estar vacia.")
            return
        lista = cargar_lexemas_extra()
        for item in lista:
            if item["lexema"] == lexema:
                QMessageBox.warning(self, "Duplicado", f"El lexema '{lexema}' ya existe.")
                return
        lista.append({
            "lexema": lexema,
            "categoria": self._categoria.currentText(),
            "descripcion": descripcion,
        })
        guardar_lexemas_extra(lista)
        self.guardado = True
        self.accept()


def flujo_agregar_lexema(parent=None):
    dlg_clave = DialogoClave(parent)
    if not dlg_clave.exec() or not dlg_clave.aprobado:
        return False
    dlg_lex = DialogoAgregarLexema(parent)
    dlg_lex.exec()
    return dlg_lex.guardado
