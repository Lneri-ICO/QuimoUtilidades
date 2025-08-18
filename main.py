from PyQt6.QtWidgets import QApplication
import sys
from ui.ui_inventario import InventarioApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = InventarioApp()
    ventana.show()
    sys.exit(app.exec())

# Función: Este es el punto de entrada de la aplicación.
# Crea una instancia de QApplication (necesaria para cualquier aplicación PyQt),
# instancia la ventana principal (InventarioApp) y ejecuta el bucle principal de eventos.