import sys
from PyQt6.QtWidgets import QApplication
from gui_main import VentanaPrincipal


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()