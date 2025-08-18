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
import sqlite3

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
        self.panel_derecho.configurar_autocompletado(self.current_table_type)
        print("cambiar_tipo_tabla ejecutado exitosamente.")

    def cargar_datos_desde_db(self):
        """Carga datos sin warnings usando SQLAlchemy con manejo mejorado"""
        try:
            from sqlalchemy import create_engine
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
                    JOIN proveedor p ON m.proveedor = p.id_proveedor
                    ORDER BY m.nombre_mp
                """,
                "productosreventa": """
                    SELECT p.id_prev, p.nombre_prev, p.unidad_medida_prev,
                        pr.nombre_proveedor, p.cantidad_prev, p.estatus_prev
                    FROM productosreventa p
                    JOIN proveedor pr ON p.proveedor = pr.id_proveedor
                    ORDER BY p.nombre_prev
                """
            }
            
            with self.engine.connect() as connection:  # Usar self.engine
                self.df_original = pd.read_sql_query(
                    queries[self.current_table_type],
                    connection
                )
                
            # Depuración opcional
            print(f"Datos cargados correctamente. Filas: {len(self.df_original)}")
            self.mostrar_tabla_productos(self.df_original)
            
        except KeyError:
            error_msg = f"Tipo de tabla no válido: {self.current_table_type}"
            print(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
        except SQLAlchemyError as e:
            error_msg = f"Error de base de datos: {str(e)}"
            print(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            print(error_msg)
            QMessageBox.critical(self, "Error", error_msg)

    def mostrar_tabla_productos(self, df):
        """Muestra los datos del DataFrame en la tabla de manera confiable"""
        try:
            # Limpiar tabla completamente
            self.tabla_productos.clearContents()
            self.tabla_productos.setRowCount(0)
            
            if df is None or df.empty:
                print("MostrarTabla: DataFrame vacío o None")
                return
            
            print("\nCONTENIDO COMPLETO DEL DATAFRAME FILTRADO:")
            print(df)
            
            print(f"\n=== INFORMACIÓN DETALLADA DEL DATAFRAME ===")
            print(f"Total registros: {len(df)}")
            print("\nEstructura del DataFrame:")
            print(df.columns.tolist())
            print("\nPrimer registro completo:")
            print(df.iloc[0].to_dict())
            
            # Configurar número de filas
            self.tabla_productos.setRowCount(len(df))
            
            # Verificar estructura del DataFrame
            required_columns = {
                "productos": ["id_producto", "nombre_producto", "unidad_medida_producto", 
                            "area_producto", "cantidad_producto", "estatus_producto"],
                "materiasprimas": ["id_mp", "nombre_mp", "unidad_medida_mp",
                                "nombre_proveedor", "cantidad_comprada_mp", "estatus_mp"],
                "productosreventa": ["id_prev", "nombre_prev", "unidad_medida_prev",
                                    "nombre_proveedor", "cantidad_prev", "estatus_prev"]
            }
            
            # Verificar que las columnas del DF coinciden con lo esperado
            expected_columns = required_columns.get(self.current_table_type, [])
            if not all(col in df.columns for col in expected_columns):
                missing = [col for col in expected_columns if col not in df.columns]
                print(f"Error: Faltan columnas en el DataFrame: {missing}")
                QMessageBox.critical(self, "Error", f"El formato de los datos no coincide.\nFaltan columnas: {', '.join(missing)}")
                return
            
            for i, row in df.iterrows():
                try:
                    # Mapear columnas del DataFrame a posiciones en la tabla
                    if self.current_table_type == "productos":
                        data = {
                            "id": row["id_producto"],
                            "nombre": row["nombre_producto"],
                            "unidad": row["unidad_medida_producto"],
                            "extra": row["area_producto"],
                            "cantidad": row["cantidad_producto"],
                            "estatus": row["estatus_producto"]
                        }
                    elif self.current_table_type == "materiasprimas":
                        data = {
                            "id": row["id_mp"],
                            "nombre": row["nombre_mp"],
                            "unidad": row["unidad_medida_mp"],
                            "extra": row["nombre_proveedor"],
                            "cantidad": row["cantidad_comprada_mp"],
                            "estatus": row["estatus_mp"]
                        }
                    else:  # productosreventa
                        data = {
                            "id": row["id_prev"],
                            "nombre": row["nombre_prev"],
                            "unidad": row["unidad_medida_prev"],
                            "extra": row["nombre_proveedor"],
                            "cantidad": row["cantidad_prev"],
                            "estatus": row["estatus_prev"]
                        }
                    
                    # ID
                    id_val = str(data["id"]) if pd.notna(data["id"]) else ""
                    item_id = QTableWidgetItem(id_val)
                    item_id.setFlags(item_id.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.tabla_productos.setItem(i, 0, item_id)
                    
                    # Nombre
                    nombre = str(data["nombre"]) if pd.notna(data["nombre"]) else "N/A"
                    item_nombre = QTableWidgetItem(nombre)
                    item_nombre.setFlags(item_nombre.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.tabla_productos.setItem(i, 1, item_nombre)
                    
                    # Unidad
                    unidad_val = str(data["unidad"]) if pd.notna(data["unidad"]) else ""
                    item_unidad = QTableWidgetItem(unidad_val)
                    item_unidad.setFlags(item_unidad.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    item_unidad.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tabla_productos.setItem(i, 2, item_unidad)
                    
                    # Área/Proveedor
                    extra_val = str(data["extra"]) if pd.notna(data["extra"]) else ""
                    item_extra = QTableWidgetItem(extra_val)
                    item_extra.setFlags(item_extra.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    item_extra.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tabla_productos.setItem(i, 3, item_extra)
                    
                    # Cantidad
                    cantidad_val = str(data["cantidad"]) if pd.notna(data["cantidad"]) else ""
                    item_cantidad = QTableWidgetItem(cantidad_val)
                    item_cantidad.setFlags(item_cantidad.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    item_cantidad.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    self.tabla_productos.setItem(i, 4, item_cantidad)
                    
                    # Estatus
                    estatus_val = str(data["estatus"]) if pd.notna(data["estatus"]) else ""
                    estatus_text = "Activo" if estatus_val.lower() in ('true', 'activo', '1', 't') else "Inactivo"
                    item_estatus = QTableWidgetItem(estatus_text)
                    item_estatus.setFlags(item_estatus.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    item_estatus.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item_estatus.setBackground(Qt.GlobalColor.green if estatus_text == "Activo" else Qt.GlobalColor.red)
                    self.tabla_productos.setItem(i, 5, item_estatus)
                    
                except Exception as row_error:
                    print(f"\n--- ERROR CRÍTICO AL PROCESAR LA FILA {i} ---")
                    print(f"Contenido de la fila: {row.to_dict()}")
                    traceback.print_exc()
                    
            print("Tabla actualizada correctamente")
            
            # Redimensionar y ajustar
            self.tabla_productos.resizeColumnsToContents()
            self.tabla_productos.resizeRowsToContents()
            self.tabla_productos.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            self.tabla_productos.viewport().update()
            print("Tabla actualizada y redimensionada correctamente")
            
        except Exception as e:
            print(f"Error crítico en mostrar_tabla_productos: {str(e)}")
            self.tabla_productos.setRowCount(0)
            QMessageBox.critical(self, "Error", f"No se pudieron mostrar los datos:\n{str(e)}")

    def filtrar_tabla(self, texto):
        """Filtra la tabla según el texto de búsqueda de manera efectiva"""
        try:
            # Verificación básica de datos
            if not hasattr(self, "df_original") or self.df_original.empty:
                print("Advertencia: No hay datos para filtrar")
                self.tabla_productos.setRowCount(0)
                return

            texto = str(texto).strip().lower()
            
            # Mostrar todos los registros si no hay texto de búsqueda
            if not texto:
                self.mostrar_tabla_productos(self.df_original)
                return

            # Verificar que existe la columna de nombres
            nombre_col = {
                "productos": "nombre_producto",
                "materiasprimas": "nombre_mp",
                "productosreventa": "nombre_prev"
            }.get(self.current_table_type)
            
            if nombre_col not in self.df_original.columns:
                print(f"Error: No existe la columna {nombre_col} para búsqueda")
                return
            
            # Convertir la columna de nombres a string y limpiarla
            nombres = self.df_original[nombre_col].astype(str).str.lower().str.strip()
            
            # Filtrado
            mask = nombres.str.contains(texto, regex=False)
            df_filtrado = self.df_original[mask].reset_index(drop=True)  # Resetear índices

            # Mostrar resultados
            self.mostrar_tabla_productos(df_filtrado)

        except Exception as e:
            print(f"Error durante el filtrado: {str(e)}")
            self.tabla_productos.setRowCount(0)
            QMessageBox.warning(self, "Error", f"Ocurrió un error al filtrar: {str(e)}")
            

    def actualizar_paneles_seleccion(self):
        """Actualiza los paneles derecho e inferior según la selección"""
        selected_items = self.tabla_productos.selectedItems()
        
        if not selected_items:
            self.current_product_id = None
            return
            
        row = selected_items[0].row()
        product_id = int(self.tabla_productos.item(row, 0).text())
        self.current_product_id = product_id
        
        # Obtener datos completos del producto seleccionado
        try:
            cantidad = float(self.tabla_productos.item(row, 4).text())
            estatus = self.tabla_productos.item(row, 5).text() == "Activo"
            
            # Actualizar panel derecho
            self.panel_derecho.actualizar_datos_producto({
                'id': product_id,
                'cantidad': cantidad,
                'estatus': estatus,
                'tipo': self.current_table_type
            })
                
        except Exception as e:
            print(f"Error al actualizar paneles: {e}")

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
            
    def mostrar_info_depuracion(self):
        """Muestra información crítica para depuración"""
        if not hasattr(self, "df_original") or self.df_original.empty:
            print("No hay datos cargados en df_original")
            return
        
        print("\n=== INFORMACIÓN PARA DEPURACIÓN ===")
        print(f"Tipo de tabla actual: {self.current_table_type}")
        print(f"Total registros: {len(self.df_original)}")
        print("\nTipos de datos:")
        print(self.df_original.dtypes)
        
        print("\nPrimeras 5 filas:")
        print(self.df_original.head().to_dict())
        
        print("\nValores nulos por columna:")
        print(self.df_original.isnull().sum())
        
class PanelInferior(QWidget):
    def __init__(self, engine):
        # ... código existente ...
        
        # Modificar la señal para incluir costo
        self.produccion_registrada.connect(self.registrar_produccion_con_costo)

    # Renombrar y modificar el método de registro
    def registrar_produccion_con_costo(self, producto, cantidad, area, costo):
        """Registrar producción con costo en la semana actual"""
        fecha_actual = datetime.now().date()
        dia_semana = fecha_actual.weekday()
        dias = ["L", "M", "M", "J", "V", "S", "D"]
        dia = dias[dia_semana]
        
        try:
            with self.engine.connect() as conn:
                # Insertar o actualizar registro
                query = text("""
                    INSERT INTO produccion (producto, cantidad, fecha, dia, area, costo)
                    VALUES (:producto, :cantidad, :fecha, :dia, :area, :costo)
                    ON CONFLICT(fecha, producto) DO UPDATE SET
                    cantidad = produccion.cantidad + :cantidad,
                    costo = produccion.costo + :costo
                """)
                conn.execute(query, {
                    "producto": producto,
                    "cantidad": cantidad,
                    "fecha": fecha_actual,
                    "dia": dia,
                    "area": area,
                    "costo": costo
                })
            
            # Actualizar la tabla visual
            self.cargar_datos_desde_db()
            
        except Exception as e:
            print(f"Error al registrar producción: {e}")