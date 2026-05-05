from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSlider, QSpinBox
)
from PyQt6.QtCore import Qt
from estilos import STYLE_DIALOGO
from config import cargar_config, guardar_config


class VentanaVista(QDialog):
    def __init__(self, font_size_actual, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuracion de Vista")
        self.setFixedSize(360, 200)
        self.setStyleSheet(STYLE_DIALOGO)
        self.font_size_elegido = font_size_actual
        self._construir(font_size_actual)

    def _construir(self, size_actual):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        lay.addWidget(QLabel("Tamano de fuente del editor y tablas:"))

        fila = QHBoxLayout()
        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setMinimum(9)
        self._slider.setMaximum(22)
        self._slider.setValue(size_actual)
        self._slider.setTickInterval(1)
        self._slider.setTickPosition(QSlider.TickPosition.TicksBelow)

        self._spin = QSpinBox()
        self._spin.setMinimum(9)
        self._spin.setMaximum(22)
        self._spin.setValue(size_actual)
        self._spin.setFixedWidth(54)

        self._slider.valueChanged.connect(self._spin.setValue)
        self._spin.valueChanged.connect(self._slider.setValue)

        fila.addWidget(self._slider)
        fila.addWidget(self._spin)
        lay.addLayout(fila)

        lbl_rango = QLabel("Rango: 9 pt  —  22 pt")
        lbl_rango.setStyleSheet("font-size:11px; color:#845162;")
        lay.addWidget(lbl_rango)

        btns = QHBoxLayout()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btn_aplicar = QPushButton("Aplicar")
        btn_aplicar.setObjectName("btn_ok")
        btn_aplicar.clicked.connect(self._aplicar)
        btns.addStretch()
        btns.addWidget(btn_cancel)
        btns.addWidget(btn_aplicar)
        lay.addLayout(btns)

    def _aplicar(self):
        self.font_size_elegido = self._spin.value()
        cfg = cargar_config()
        cfg["font_size"] = self.font_size_elegido
        guardar_config(cfg)
        self.accept()
