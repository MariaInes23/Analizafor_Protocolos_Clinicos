from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QSplitter, QFrame, QStatusBar,
    QFileDialog, QMessageBox, QTabWidget, QPlainTextEdit
)
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtCore import Qt

from lexico import AnalizadorLexico
from sintactico import AnalizadorSintactico
from semantico import AnalizadorSemantico
from reporte import generar_reporte
from resaltador import Resaltador
from ventana_ayuda import VentanaAyuda
from ventana_lexema import flujo_agregar_lexema
from ventana_vista import VentanaVista
from editor_lineas import EditorConLineas
from estilos import STYLE, COLORES_TOKEN
from config import cargar_config


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analizador Lexico  -  Lenguaje de Protocolos Clinicos")
        self.setMinimumSize(1150, 700)
        cfg = cargar_config()
        self._font_size = cfg.get("font_size", 13)
        self._ultimo_arbol = None
        self._ultima_tabla = None
        self._construir_ui()
        self._aplicar_fuente(self._font_size)

    def _construir_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        raiz = QVBoxLayout(central)
        raiz.setContentsMargins(16, 12, 16, 8)
        raiz.setSpacing(8)

        cab = QHBoxLayout()
        titulo = QLabel("Analizador Lexico")
        titulo.setObjectName("titulo")
        cab.addWidget(titulo)
        cab.addStretch()

        self.btn_vista = QPushButton("Vista")
        self.btn_vista.setObjectName("btn_vista")
        self.btn_vista.clicked.connect(self._mostrar_vista)

        self.btn_reporte = QPushButton("📄 Generar Reporte")
        self.btn_reporte.setObjectName("btn_reporte")
        self.btn_reporte.clicked.connect(self._generar_reporte)
        self.btn_reporte.setEnabled(False)

        self.btn_abrir = QPushButton("📂 Abrir Archivo")
        self.btn_abrir.setObjectName("btn_abrir")
        self.btn_abrir.clicked.connect(self._abrir_archivo)

        self.btn_lexema = QPushButton("+ Agregar Lexema")
        self.btn_lexema.setObjectName("btn_lexema")
        self.btn_lexema.clicked.connect(self._agregar_lexema)

        self.btn_ayuda = QPushButton("? Ayuda")
        self.btn_ayuda.setObjectName("btn_ayuda")
        self.btn_ayuda.clicked.connect(self._mostrar_ayuda)

        cab.addWidget(self.btn_vista)
        cab.addWidget(self.btn_reporte)
        cab.addWidget(self.btn_abrir)
        cab.addWidget(self.btn_lexema)
        cab.addWidget(self.btn_ayuda)
        raiz.addLayout(cab)

        linea = QFrame()
        linea.setObjectName("linea")
        linea.setFrameShape(QFrame.Shape.HLine)
        raiz.addWidget(linea)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        raiz.addWidget(splitter)

        panel_izq = QWidget()
        lay_izq = QVBoxLayout(panel_izq)
        lay_izq.setContentsMargins(0, 0, 10, 0)
        lay_izq.setSpacing(4)

        lbl_editor = QLabel("Codigo fuente")
        lbl_editor.setObjectName("seccion")
        lay_izq.addWidget(lbl_editor)

        self.editor = EditorConLineas()
        self.editor.setPlaceholderText("Escribe aqui el codigo fuente del protocolo...")
        self.editor.setTabStopDistance(28)
        self._resaltador = Resaltador(self.editor.document())
        lay_izq.addWidget(self.editor)

        botones = QHBoxLayout()
        botones.setSpacing(8)
        self.btn_analizar = QPushButton("Analizar")
        self.btn_analizar.setObjectName("btn_analizar")
        self.btn_analizar.clicked.connect(self._ejecutar_analisis)
        self.btn_limpiar = QPushButton("Limpiar")
        self.btn_limpiar.setObjectName("btn_limpiar")
        self.btn_limpiar.clicked.connect(self._limpiar)
        botones.addWidget(self.btn_analizar)
        botones.addWidget(self.btn_limpiar)
        botones.addStretch()
        lay_izq.addLayout(botones)

        splitter.addWidget(panel_izq)

        panel_der = QWidget()
        lay_der = QVBoxLayout(panel_der)
        lay_der.setContentsMargins(10, 0, 0, 0)
        lay_der.setSpacing(4)

        self.tabs_resultado = QTabWidget()
        self.tabs_resultado.setObjectName("tabs_resultado")

        tab_lexico = QWidget()
        lay_lexico = QVBoxLayout(tab_lexico)
        lay_lexico.setContentsMargins(0, 8, 0, 0)
        lay_lexico.setSpacing(4)

        lbl_tokens = QLabel("Tokens reconocidos")
        lbl_tokens.setObjectName("seccion")
        lay_lexico.addWidget(lbl_tokens)

        self.tabla_tokens = QTableWidget(0, 4)
        self.tabla_tokens.setHorizontalHeaderLabels(["Lexema", "Token", "Linea", "Columna"])
        self.tabla_tokens.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tabla_tokens.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabla_tokens.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_tokens.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_tokens.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_tokens.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_tokens.setAlternatingRowColors(True)
        self.tabla_tokens.verticalHeader().setVisible(False)
        lay_lexico.addWidget(self.tabla_tokens, 3)

        lbl_err = QLabel("Errores lexicos")
        lbl_err.setObjectName("seccion")
        lay_lexico.addWidget(lbl_err)

        self.tabla_errores = QTableWidget(0, 4)
        self.tabla_errores.setHorizontalHeaderLabels(["Lexema", "Descripcion", "Linea", "Columna"])
        self.tabla_errores.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_errores.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabla_errores.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_errores.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_errores.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_errores.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_errores.verticalHeader().setVisible(False)
        lay_lexico.addWidget(self.tabla_errores, 1)

        self.tabs_resultado.addTab(tab_lexico, "Análisis Léxico")

        tab_sintactico = QWidget()
        lay_sint = QVBoxLayout(tab_sintactico)
        lay_sint.setContentsMargins(0, 8, 0, 0)
        lay_sint.setSpacing(4)

        self.lbl_estado_sint = QLabel("Sin analizar")
        self.lbl_estado_sint.setObjectName("lbl_estado_sint")
        self.lbl_estado_sint.setStyleSheet("font-size:12px; font-weight:700; color:#845162; padding:2px 0px;")
        lay_sint.addWidget(self.lbl_estado_sint)

        lbl_arbol = QLabel("Árbol sintáctico")
        lbl_arbol.setObjectName("seccion")
        lay_sint.addWidget(lbl_arbol)

        self.txt_arbol = QPlainTextEdit()
        self.txt_arbol.setReadOnly(True)
        self.txt_arbol.setObjectName("txt_arbol")
        self.txt_arbol.setPlaceholderText("El árbol sintáctico aparecerá aquí al analizar código válido...")
        self.txt_arbol.setFont(__import__("PyQt6.QtGui", fromlist=["QFont"]).QFont("Consolas", 12))
        lay_sint.addWidget(self.txt_arbol, 3)

        lbl_err_sint = QLabel("Errores sintácticos")
        lbl_err_sint.setObjectName("seccion")
        lay_sint.addWidget(lbl_err_sint)

        self.tabla_errores_sint = QTableWidget(0, 3)
        self.tabla_errores_sint.setHorizontalHeaderLabels(["Descripcion", "Linea", "Columna"])
        self.tabla_errores_sint.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tabla_errores_sint.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_errores_sint.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_errores_sint.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_errores_sint.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_errores_sint.verticalHeader().setVisible(False)
        lay_sint.addWidget(self.tabla_errores_sint, 1)

        self.tabs_resultado.addTab(tab_sintactico, "Análisis Sintáctico")

        # ── Pestaña Análisis Semántico ──────────────────────────────────────
        tab_semantico = QWidget()
        lay_sem = QVBoxLayout(tab_semantico)
        lay_sem.setContentsMargins(0, 8, 0, 0)
        lay_sem.setSpacing(4)

        self.lbl_estado_sem = QLabel("Sin analizar")
        self.lbl_estado_sem.setObjectName("lbl_estado_sem")
        self.lbl_estado_sem.setStyleSheet("font-size:12px; font-weight:700; color:#845162; padding:2px 0px;")
        lay_sem.addWidget(self.lbl_estado_sem)

        lbl_tabla_sim = QLabel("Tabla de Símbolos")
        lbl_tabla_sim.setObjectName("seccion")
        lay_sem.addWidget(lbl_tabla_sim)

        self.tabla_simbolos = QTableWidget(0, 6)
        self.tabla_simbolos.setHorizontalHeaderLabels(
            ["Identificador", "Tipo", "Valor", "Línea", "Columna", "Ámbito"]
        )
        self.tabla_simbolos.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tabla_simbolos.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_simbolos.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tabla_simbolos.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_simbolos.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_simbolos.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self.tabla_simbolos.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_simbolos.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_simbolos.setAlternatingRowColors(True)
        self.tabla_simbolos.verticalHeader().setVisible(False)
        lay_sem.addWidget(self.tabla_simbolos, 3)

        lbl_err_sem = QLabel("Errores semánticos")
        lbl_err_sem.setObjectName("seccion")
        lay_sem.addWidget(lbl_err_sem)

        self.tabla_errores_sem = QTableWidget(0, 4)
        self.tabla_errores_sem.setHorizontalHeaderLabels(["Código", "Descripción", "Línea", "Columna"])
        self.tabla_errores_sem.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_errores_sem.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabla_errores_sem.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_errores_sem.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_errores_sem.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_errores_sem.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_errores_sem.verticalHeader().setVisible(False)
        lay_sem.addWidget(self.tabla_errores_sem, 1)

        self.tabs_resultado.addTab(tab_semantico, "Análisis Semántico")

        # ── Pestaña Reporte Clínico ────────────────────────────────────────
        tab_reporte = QWidget()
        lay_rep = QVBoxLayout(tab_reporte)
        lay_rep.setContentsMargins(0, 8, 0, 0)
        lay_rep.setSpacing(4)

        cab_rep = QHBoxLayout()
        lbl_rep = QLabel("Reporte Clínico Generado")
        lbl_rep.setObjectName("seccion")
        cab_rep.addWidget(lbl_rep)
        cab_rep.addStretch()
        self.btn_guardar_rep = QPushButton("💾 Guardar .txt")
        self.btn_guardar_rep.setObjectName("btn_reporte")
        self.btn_guardar_rep.clicked.connect(self._guardar_reporte)
        self.btn_guardar_rep.setEnabled(False)
        cab_rep.addWidget(self.btn_guardar_rep)
        lay_rep.addLayout(cab_rep)

        self.txt_reporte = QPlainTextEdit()
        self.txt_reporte.setReadOnly(True)
        self.txt_reporte.setObjectName("txt_arbol")
        self.txt_reporte.setPlaceholderText(
            "El reporte clínico aparecerá aquí después de analizar un programa válido\n"
            "que contenga instrucciones INGRESAR, DIAGNOSTICO, TRATAMIENTO y/o DOSIS."
        )
        self.txt_reporte.setFont(__import__("PyQt6.QtGui", fromlist=["QFont"]).QFont("Consolas", 12))
        lay_rep.addWidget(self.txt_reporte)

        self.tabs_resultado.addTab(tab_reporte, "📄 Reporte")

        lay_der.addWidget(self.tabs_resultado)
        splitter.addWidget(panel_der)
        splitter.setSizes([430, 720])

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.setStyleSheet(STYLE)

    def _aplicar_fuente(self, size):
        self._font_size = size

        # — Editor de código —
        font_editor = QFont("Consolas", size)
        self.editor.setFont(font_editor)

        # Aplicar fuente al texto ya escrito en el documento
        from PyQt6.QtGui import QTextCursor, QTextCharFormat
        cursor = self.editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        fmt = QTextCharFormat()
        fmt.setFont(font_editor)
        cursor.mergeCharFormat(fmt)
        # Mover cursor al final sin selección para no dejar texto seleccionado
        cursor.clearSelection()
        self.editor.setTextCursor(cursor)

        self.editor._actualizar_ancho_panel()

        font_arbol = QFont("Consolas", max(10, size - 1))
        self.txt_arbol.setFont(font_arbol)
        self.txt_reporte.setFont(font_arbol)

        # Forzar que el formato por defecto del documento también use la fuente nueva,
        # de lo contrario setPlainText() posterior ignora el font del widget.
        from PyQt6.QtGui import QTextCharFormat
        fmt_rep = QTextCharFormat()
        fmt_rep.setFont(font_arbol)
        self.txt_reporte.document().setDefaultFont(font_arbol)
        # Si ya hay contenido, re-aplicar la fuente a todo el texto existente
        if self.txt_reporte.toPlainText():
            cur = self.txt_reporte.textCursor()
            from PyQt6.QtGui import QTextCursor
            cur.select(QTextCursor.SelectionType.Document)
            cur.mergeCharFormat(fmt_rep)
            cur.clearSelection()
            self.txt_reporte.setTextCursor(cur)

        # — Tablas: cuerpo, header y filas ya existentes —
        font_tabla = QFont("Segoe UI", max(10, size - 1))
        font_header = QFont("Segoe UI", max(10, size - 1))
        font_header.setBold(True)

        for tabla in (self.tabla_tokens, self.tabla_errores, self.tabla_errores_sint,
                      self.tabla_simbolos, self.tabla_errores_sem):
            tabla.setFont(font_tabla)

            # Header horizontal
            tabla.horizontalHeader().setFont(font_header)

            # Ajustar alto de fila para que quepa el texto
            tabla.verticalHeader().setDefaultSectionSize(max(22, size + 10))

            # Actualizar fuente en celdas ya existentes
            for fila in range(tabla.rowCount()):
                for col in range(tabla.columnCount()):
                    item = tabla.item(fila, col)
                    if item:
                        item.setFont(font_tabla)

    def _abrir_archivo(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir archivo de codigo fuente",
            "",
            "Archivos de texto (*.txt *.lpc *.src *.code);;Todos los archivos (*)"
        )
        if not ruta:
            return

        # Si ya hay contenido, preguntar antes de reemplazar
        if self.editor.toPlainText().strip():
            resp = QMessageBox.question(
                self,
                "Reemplazar contenido",
                "El editor ya tiene contenido.\n¿Deseas reemplazarlo con el archivo seleccionado?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if resp != QMessageBox.StandardButton.Yes:
                return

        # Intentar leer el archivo con distintas codificaciones
        contenido = None
        for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
            try:
                with open(ruta, "r", encoding=enc) as f:
                    contenido = f.read()
                break
            except (UnicodeDecodeError, OSError):
                continue

        if contenido is None:
            QMessageBox.critical(
                self,
                "Error al abrir",
                f"No se pudo leer el archivo:\n{ruta}\n\nVerifica que sea un archivo de texto valido."
            )
            return

        self.editor.setPlainText(contenido)
        self._aplicar_fuente(self._font_size)

        # Mostrar nombre del archivo en el título de la ventana
        import os
        nombre = os.path.basename(ruta)
        self.setWindowTitle(f"Analizador Lexico  -  {nombre}")

    def _mostrar_ayuda(self):
        dlg = VentanaAyuda(self)
        dlg.exec()

    def _agregar_lexema(self):
        guardado = flujo_agregar_lexema(self)
        if guardado:
            from tokens import PALABRAS_RESERVADAS
            from config import cargar_lexemas_extra
            for l in cargar_lexemas_extra():
                if l["categoria"] == "PALABRA_RESERVADA":
                    PALABRAS_RESERVADAS.add(l["lexema"])
            self._resaltador.rehighlight()

    def _mostrar_vista(self):
        dlg = VentanaVista(self._font_size, self)
        if dlg.exec():
            self._aplicar_fuente(dlg.font_size_elegido)

    def _ejecutar_analisis(self):
        codigo = self.editor.toPlainText()
        if not codigo.strip():
            return

        from config import cargar_lexemas_extra
        from tokens import PALABRAS_RESERVADAS
        for l in cargar_lexemas_extra():
            if l["categoria"] == "PALABRA_RESERVADA":
                PALABRAS_RESERVADAS.add(l["lexema"])

        analizador = AnalizadorLexico(codigo)
        tokens, errores = analizador.analizar()

        font_tabla = QFont("Segoe UI", max(10, self._font_size - 1))

        self.tabla_tokens.setRowCount(0)
        for tok in tokens:
            fila = self.tabla_tokens.rowCount()
            self.tabla_tokens.insertRow(fila)
            color = COLORES_TOKEN.get(tok.tipo, "#FFE3D8")
            for col, valor in enumerate([tok.lexema, tok.tipo, str(tok.linea), str(tok.columna)]):
                item = QTableWidgetItem(valor)
                item.setForeground(QColor(color))
                item.setFont(font_tabla)
                if col in (2, 3):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabla_tokens.setItem(fila, col, item)

        self.tabla_errores.setRowCount(0)
        for err in errores:
            fila = self.tabla_errores.rowCount()
            self.tabla_errores.insertRow(fila)
            for col, valor in enumerate([err["lexema"], err["descripcion"], str(err["linea"]), str(err["columna"])]):
                item = QTableWidgetItem(valor)
                item.setForeground(QColor("#f48771"))
                item.setFont(font_tabla)
                if col in (2, 3):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabla_errores.setItem(fila, col, item)

        self.txt_arbol.clear()
        self.tabla_errores_sint.setRowCount(0)
        self.tabla_simbolos.setRowCount(0)
        self.tabla_errores_sem.setRowCount(0)
        self.lbl_estado_sem.setText("Sin analizar")
        self.lbl_estado_sem.setStyleSheet("font-size:12px; font-weight:700; color:#845162; padding:2px 0px;")
        self.txt_reporte.clear()
        self.btn_reporte.setEnabled(False)
        self.btn_guardar_rep.setEnabled(False)
        self._ultimo_arbol = None
        self._ultima_tabla = None

        if errores:
            self.lbl_estado_sint.setText("⚠ Hay errores léxicos — corrígelos antes de analizar sintácticamente")
            self.lbl_estado_sint.setStyleSheet("font-size:12px; font-weight:700; color:#f48771; padding:2px 0px;")
            self.tabs_resultado.setCurrentIndex(0)
            return

        parser = AnalizadorSintactico(tokens)
        arbol, errores_sint = parser.analizar()

        if arbol:
            self.lbl_estado_sint.setText("✔ Cadena aceptada")
            self.lbl_estado_sint.setStyleSheet("font-size:12px; font-weight:700; color:#a8e6a3; padding:2px 0px;")
            self.txt_arbol.setPlainText(str(arbol))
        else:
            self.lbl_estado_sint.setText("✘ Error sintáctico detectado")
            self.lbl_estado_sint.setStyleSheet("font-size:12px; font-weight:700; color:#f48771; padding:2px 0px;")
            self.txt_arbol.setPlainText("")

        for err in errores_sint:
            fila = self.tabla_errores_sint.rowCount()
            self.tabla_errores_sint.insertRow(fila)
            linea_str = str(err["linea"]) if err["linea"] else "-"
            col_str = str(err["columna"]) if err["columna"] else "-"
            for c, valor in enumerate([err["mensaje"], linea_str, col_str]):
                item = QTableWidgetItem(valor)
                item.setForeground(QColor("#f48771"))
                item.setFont(font_tabla)
                if c in (1, 2):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabla_errores_sint.setItem(fila, c, item)

        # ── Análisis Semántico ─────────────────────────────────────────────
        if arbol and not errores_sint:
            sem = AnalizadorSemantico(arbol, tokens)
            tabla_sim, error_sem = sem.analizar()

            # Poblar tabla de símbolos
            COLOR_SIM = "#c3e8c3"
            for entrada in tabla_sim.registros():
                fila = self.tabla_simbolos.rowCount()
                self.tabla_simbolos.insertRow(fila)
                valores = [
                    entrada.identificador,
                    entrada.tipo,
                    str(entrada.valor),
                    str(entrada.linea)   if entrada.linea   else "-",
                    str(entrada.columna) if entrada.columna else "-",
                    entrada.ambito,
                ]
                for c, v in enumerate(valores):
                    item = QTableWidgetItem(v)
                    item.setForeground(QColor(COLOR_SIM))
                    item.setFont(font_tabla)
                    if c in (3, 4):
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tabla_simbolos.setItem(fila, c, item)

            if error_sem:
                self.lbl_estado_sem.setText(f"✘ Error semántico detectado [{error_sem.codigo}]")
                self.lbl_estado_sem.setStyleSheet("font-size:12px; font-weight:700; color:#f48771; padding:2px 0px;")
                fila = self.tabla_errores_sem.rowCount()
                self.tabla_errores_sem.insertRow(fila)
                linea_str = str(error_sem.linea)   if error_sem.linea   else "-"
                col_str   = str(error_sem.columna) if error_sem.columna else "-"
                for c, v in enumerate([error_sem.codigo, error_sem.mensaje, linea_str, col_str]):
                    item = QTableWidgetItem(v)
                    item.setForeground(QColor("#f48771"))
                    item.setFont(font_tabla)
                    if c in (2, 3):
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tabla_errores_sem.setItem(fila, c, item)
            else:
                sim_count = len(tabla_sim)
                self.lbl_estado_sem.setText(
                    f"✔ Análisis semántico exitoso — {sim_count} símbolo{'s' if sim_count != 1 else ''} registrado{'s' if sim_count != 1 else ''}"
                )
                self.lbl_estado_sem.setStyleSheet("font-size:12px; font-weight:700; color:#a8e6a3; padding:2px 0px;")
                # Generar reporte automáticamente
                self._ultimo_arbol = arbol
                self._ultima_tabla = tabla_sim
                texto_rep = generar_reporte(arbol, tabla_sim)
                # Asegurar que el reporte use la fuente actual del usuario
                from PyQt6.QtGui import QFont as _QFont
                _font_rep = _QFont("Consolas", max(10, self._font_size - 1))
                self.txt_reporte.document().setDefaultFont(_font_rep)
                self.txt_reporte.setFont(_font_rep)
                self.txt_reporte.setPlainText(texto_rep)
                self.btn_reporte.setEnabled(True)
                self.btn_guardar_rep.setEnabled(True)

            self.tabs_resultado.setCurrentIndex(2)
        else:
            self.tabs_resultado.setCurrentIndex(1)

    def _generar_reporte(self):
        """Ir a la pestaña de reporte."""
        self.tabs_resultado.setCurrentIndex(3)

    def _guardar_reporte(self):
        texto = self.txt_reporte.toPlainText()
        if not texto.strip():
            return
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar Reporte", "reporte_clinico.txt",
            "Archivo de texto (*.txt);;Todos los archivos (*)"
        )
        if ruta:
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(texto)
            self.status.showMessage(f"Reporte guardado en {ruta}", 4000)

    def _limpiar(self):
        self.editor.clear()
        self.tabla_tokens.setRowCount(0)
        self.tabla_errores.setRowCount(0)
        self.txt_arbol.clear()
        self.tabla_errores_sint.setRowCount(0)
        self.tabla_simbolos.setRowCount(0)
        self.tabla_errores_sem.setRowCount(0)
        self.txt_reporte.clear()
        self.btn_reporte.setEnabled(False)
        self.btn_guardar_rep.setEnabled(False)
        self._ultimo_arbol = None
        self._ultima_tabla = None
        self.lbl_estado_sint.setText("Sin analizar")
        self.lbl_estado_sint.setStyleSheet("font-size:12px; font-weight:700; color:#845162; padding:2px 0px;")
        self.lbl_estado_sem.setText("Sin analizar")
        self.lbl_estado_sem.setStyleSheet("font-size:12px; font-weight:700; color:#845162; padding:2px 0px;")
