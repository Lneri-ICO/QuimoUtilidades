from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox,
    QHeaderView, QComboBox
)
from PyQt6.QtCore import Qt
import pandas as pd
from PyQt6.QtCore import QTimer
import traceback

from ui.ui_panel_derecho import PanelDerecho
from ui.ui_panel_inferior import PanelInferior
# No necesitas 'import sqlite3' aquí si ya usas SQLAlchemy
# import sqlite3

import sys
import os

def get_project_root():
    """
    Obtiene la ruta raíz del proyecto de forma fiable, tanto en
    desarrollo como en la aplicación empaquetada (.exe).
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    

class InventarioApp(QMainWindow):
    def __init__(self):
        from sqlalchemy import create_engine
        
        super().__init__()
        self.setWindowTitle("Sistema de Inventario - QUIMO")
        self.setMinimumSize(1200, 800)
        
        # Variables de estado
        self.df_original = None
        self.current_product_id = None
        self.current_table_type = "productos"  # Tipo de tabla actual
        
        # Conexión a la base de datos
        db_path = os.path.join(get_project_root(), 'quimo.db')
        print(f"DEBUG: Conectando a la base de datos en: {db_path}")
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        
        # Inicializar UI
        self.init_ui()
        
        # Cargar datos iniciales
        self.cargar_datos_desde_db()

        # Crear panel derecho
        self.panel_derecho = PanelDerecho(
            self.tabla_productos, 
            self.cargar_datos_desde_db,
            lambda: self.current_table_type,
            self.engine
        )
        self.main_layout.addWidget(self.panel_derecho)
        
        # Configurar autocompletado
        self.panel_derecho.configurar_autocompletado(self.selector_tabla.currentText())
        
        # Crear panel inferior
        self.panel_inferior = PanelInferior(self.engine)
        self.left_layout.addWidget(self.panel_inferior)
        
        # Conectar los paneles
        # Esta conexión asume que 'PanelDerecho' tiene una señal llamada 'produccion_registrada'
        # y que 'PanelInferior' tiene un método (slot) llamado 'registrar_produccion_con_costo'
        self.panel_derecho.produccion_registrada.connect(
            self.panel_inferior.registrar_produccion_con_costo
        )
        
        # Depuración
        # QTimer.singleShot(1000, self.mostrar_info_depuracion)

    def init_ui(self):
        """Inicializa todos los componentes de la interfaz"""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout principal (horizontal)
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(15)
        self.central_widget.setLayout(self.main_layout)
        
        # Layout izquierdo (vertical)
        self.left_layout = QVBoxLayout()
        self.left_layout.setSpacing(10)
        self.main_layout.addLayout(self.left_layout, stretch=3)  # 3/4 del espacio
        
        # Selector de tipo de tabla
        self.selector_tabla = QComboBox()
        self.selector_tabla.addItems(["Productos", "Materias Primas", "Productos Reventa"])
        self.selector_tabla.currentIndexChanged.connect(self.cambiar_tipo_tabla)
        self.left_layout.addWidget(self.selector_tabla)
        
        # Barra de búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre...")
        self.search_input.textChanged.connect(self.filtrar_tabla)
        self.left_layout.addWidget(self.search_input)
        
        # Tabla de productos
        self.tabla_productos = QTableWidget()
        self.tabla_productos.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_productos.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tabla_productos.itemSelectionChanged.connect(self.actualizar_paneles_seleccion)
        
        # Configurar encabezados de tabla
        self.actualizar_encabezados()
        
        self.left_layout.addWidget(self.tabla_productos)
        
        # Configurar tabla
        self.tabla_productos.setStyleSheet("""
            QTableWidget {
                gridline-color: #c0c0c0;
                font-size: 12px;
                background-color: white;
                color: black;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)
        self.tabla_productos.setAlternatingRowColors(True)
        self.tabla_productos.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Ajustar stretch factors para los elementos en left_layout
        self.left_layout.setStretch(0, 0)  # ComboBox selector
        self.left_layout.setStretch(1, 0)  # Barra de búsqueda
        self.left_layout.setStretch(2, 3)  # Tabla principal (mayor prioridad)
        self.left_layout.setStretch(3, 1)  # Panel inferior

    def actualizar_encabezados(self):
        """Actualiza los encabezados según el tipo de tabla seleccionado"""
        if self.current_table_type == "productos":
            self.tabla_productos.setColumnCount(6)
            headers = ["ID", "Producto", "Unidad", "Área", "Cantidad", "Estatus"]
        elif self.current_table_type == "materiasprimas":
            self.tabla_productos.setColumnCount(6)
            headers = ["ID", "Materia Prima", "Unidad", "Proveedor", "Cantidad", "Estatus"]
        else:  # productosreventa
            self.tabla_productos.setColumnCount(6)
            headers = ["ID", "Producto", "Unidad", "Proveedor", "Cantidad", "Estatus"]
        
        self.tabla_productos.setHorizontalHeaderLabels(headers)
        
        # Ajustar tamaño de columnas
        header = self.tabla_productos.horizontalHeader()
        for i in range(len(headers)):
            if i == 1:  # Columna de nombre (más ancha)
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
            else:
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)

    def cambiar_tipo_tabla(self, index):
        """Cambia el tipo de tabla a mostrar"""
        print(f"Cambiando tipo de tabla a índice {index}")
        tipos = ["productos", "materiasprimas", "productosreventa"]
        self.current_table_type = tipos[index]
        print(f"Tipo de tabla actual: {self.current_table_type}")
        self.actualizar_encabezados()
        self.cargar_datos_desde_db()
        self.panel_derecho.actualizar_labels_con_tipo(self.current_table_type)
        self.panel_derecho.configurar_autocompletado(self.current_table_type)
        print("cambiar_tipo_tabla ejecutado exitosamente.")

    def cargar_datos_desde_db(self):
        """Carga datos sin warnings usando SQLAlchemy con manejo mejorado"""
        try:
            from sqlalchemy.exc import SQLAlchemyError
            
            # Consultas específicas por tipo de tabla
            queries = {
                "productos": """
                    SELECT id_producto, nombre_producto, unidad_medida_producto,
                        area_producto, cantidad_producto, estatus_producto
                    FROM productos ORDER BY nombre_producto
                """,
                "materiasprimas": """
                    SELECT m.id_mp, m.nombre_mp, m.unidad_medida_mp,
                        p.nombre_proveedor, m.cantidad_comprada_mp, m.estatus_mp
                    FROM materiasprimas m
                    LEFT JOIN proveedor p ON m.proveedor = p.id_proveedor
                    ORDER BY m.nombre_mp
                """,
                "productosreventa": """
                    SELECT p.id_prev, p.nombre_prev, p.unidad_medida_prev,
                        pr.nombre_proveedor, p.cantidad_prev, p.estatus_prev
                    FROM productosreventa p
                    LEFT JOIN proveedor pr ON p.proveedor = pr.id_proveedor
                    ORDER BY p.nombre_prev
                """
            }
            
            with self.engine.connect() as connection:
                self.df_original = pd.read_sql_query(
                    queries[self.current_table_type],
                    connection
                )
                
            print(f"Datos cargados correctamente. Filas: {len(self.df_original)}")
            self.mostrar_tabla_productos(self.df_original)
            
        except KeyError:
            error_msg = f"Tipo de tabla no válido: {self.current_table_type}"
            QMessageBox.critical(self, "Error", error_msg)
        except SQLAlchemyError as e:
            error_msg = f"Error de base de datos: {str(e)}"
            QMessageBox.critical(self, "Error", error_msg)
        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            QMessageBox.critical(self, "Error", error_msg)

    def mostrar_tabla_productos(self, df):
        """Muestra los datos del DataFrame en la tabla de manera confiable"""
        try:
            self.tabla_productos.setRowCount(0)
            
            if df is None or df.empty:
                return
            
            self.tabla_productos.setRowCount(len(df))
            
            required_columns = {
                "productos": ["id_producto", "nombre_producto", "unidad_medida_producto", "area_producto", "cantidad_producto", "estatus_producto"],
                "materiasprimas": ["id_mp", "nombre_mp", "unidad_medida_mp", "nombre_proveedor", "cantidad_comprada_mp", "estatus_mp"],
                "productosreventa": ["id_prev", "nombre_prev", "unidad_medida_prev", "nombre_proveedor", "cantidad_prev", "estatus_prev"]
            }
            
            expected_columns = required_columns.get(self.current_table_type, [])
            if not all(col in df.columns for col in expected_columns):
                missing = [col for col in expected_columns if col not in df.columns]
                QMessageBox.critical(self, "Error de Datos", f"Faltan columnas en los datos recibidos: {', '.join(missing)}")
                return
            
            for i, row in df.iterrows():
                try:
                    if self.current_table_type == "productos":
                        data_map = ("id_producto", "nombre_producto", "unidad_medida_producto", "area_producto", "cantidad_producto", "estatus_producto")
                    elif self.current_table_type == "materiasprimas":
                        data_map = ("id_mp", "nombre_mp", "unidad_medida_mp", "nombre_proveedor", "cantidad_comprada_mp", "estatus_mp")
                    else:  # productosreventa
                        data_map = ("id_prev", "nombre_prev", "unidad_medida_prev", "nombre_proveedor", "cantidad_prev", "estatus_prev")

                    # Llenar la tabla
                    id_val = str(row[data_map[0]])
                    nombre_val = str(row[data_map[1]])
                    unidad_val = str(row[data_map[2]])
                    extra_val = str(row[data_map[3]]) if pd.notna(row[data_map[3]]) else "N/A"
                    try:
                        # Intenta convertir el valor a un número flotante
                        cantidad_float = float(row[data_map[4]])
                        cantidad_val = f"{cantidad_float:.2f}"
                    except (ValueError, TypeError):
                        # Si falla (ej. es texto vacío o None), usa un valor por defecto
                        cantidad_val = "0.00"
                    estatus_val = "Activo" if row[data_map[5]] in [1, True, '1', 't', 'true', 'activo'] else "Inactivo"

                    # Columna 0: ID
                    item_id = QTableWidgetItem(id_val)
                    item_id.setFlags(item_id.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.tabla_productos.setItem(i, 4, QTableWidgetItem(cantidad_val))
                    
                    # Columna 1: Nombre
                    self.tabla_productos.setItem(i, 1, QTableWidgetItem(nombre_val))

                    # Columna 2: Unidad
                    self.tabla_productos.setItem(i, 2, QTableWidgetItem(unidad_val))

                    # Columna 3: Área / Proveedor
                    self.tabla_productos.setItem(i, 3, QTableWidgetItem(extra_val))

                    # Columna 4: Cantidad
                    self.tabla_productos.setItem(i, 4, QTableWidgetItem(cantidad_val))
                    
                    # Columna 5: Estatus
                    item_estatus = QTableWidgetItem(estatus_val)
                    item_estatus.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item_estatus.setBackground(Qt.GlobalColor.green if estatus_val == "Activo" else Qt.GlobalColor.red)
                    self.tabla_productos.setItem(i, 5, item_estatus)
                    
                except Exception as row_error:
                    print(f"Error procesando fila {i}: {row_error}")
                    traceback.print_exc()
            
            self.tabla_productos.resizeColumnsToContents()
            self.tabla_productos.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron mostrar los datos: {e}")

    def filtrar_tabla(self, texto):
        """Filtra la tabla según el texto de búsqueda de manera efectiva"""
        try:
            if not hasattr(self, "df_original") or self.df_original.empty:
                return

            texto = str(texto).strip().lower()
            
            if not texto:
                self.mostrar_tabla_productos(self.df_original)
                return

            nombre_col = {
                "productos": "nombre_producto",
                "materiasprimas": "nombre_mp",
                "productosreventa": "nombre_prev"
            }.get(self.current_table_type)
            
            if nombre_col not in self.df_original.columns:
                return
            
            mask = self.df_original[nombre_col].str.lower().str.contains(texto, na=False)
            df_filtrado = self.df_original[mask]

            self.mostrar_tabla_productos(df_filtrado)

        except Exception as e:
            QMessageBox.warning(self, "Error de Filtrado", f"Ocurrió un error al filtrar: {e}")

    def actualizar_paneles_seleccion(self):
        """Actualiza el panel derecho según la selección en la tabla"""
        selected_rows = self.tabla_productos.selectionModel().selectedRows()
        if not selected_rows:
            self.current_product_id = None
            return
            
        row = selected_rows[0].row()
        
        # Para obtener el ID del producto del DataFrame original filtrado/sin filtrar
        # es más seguro obtener el texto de la celda.
        try:
            product_id = int(self.tabla_productos.item(row, 0).text())
            cantidad_str = self.tabla_productos.item(row, 4).text()
            estatus_str = self.tabla_productos.item(row, 5).text()
            
            self.current_product_id = product_id
            
            self.panel_derecho.actualizar_datos_producto({
                'id': product_id,
                'cantidad': float(cantidad_str),
                'estatus': estatus_str == "Activo",
                'tipo': self.current_table_type
            })
        except (ValueError, AttributeError) as e:
            print(f"Error al actualizar paneles: No se pudo leer la fila. {e}")
        except Exception as e:
            print(f"Error inesperado al actualizar paneles: {e}")

    def closeEvent(self, event):
        """Maneja el cierre de la aplicación"""
        reply = QMessageBox.question(
            self, 
            'Salir', 
            '¿Está seguro que desea salir de la aplicación?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

# -------------------------------------------------------------------
# LA CLASE DUPLICADA DE PanelInferior FUE ELIMINADA DE AQUÍ
# -------------------------------------------------------------------