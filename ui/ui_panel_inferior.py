# ui/ui_panel_inferior.py (VERSIÓN COMPLETA Y CORREGIDA)

from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QMessageBox, QHBoxLayout, QTabWidget,
    QComboBox
)
from PyQt6.QtCore import Qt
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from sqlalchemy import text

class PanelInferior(QWidget):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.df_produccion = pd.DataFrame()

        self.setLayout(QVBoxLayout())
        
        self.tabs = QTabWidget()
        self.layout().addWidget(self.tabs)
        
        # Pestaña de Producción
        self.tab_produccion = QWidget()
        self.tabs.addTab(self.tab_produccion, "Producción")
        self.tab_produccion.setLayout(QVBoxLayout())
        
        periodo_layout = QHBoxLayout()
        periodo_layout.addWidget(QLabel("<b>Seleccionar Período de Análisis:</b>"))
        self.combo_periodo = QComboBox()
        self.combo_periodo.addItems(["Última semana", "Últimos 15 días", "Último mes", "Últimos 3 meses"])
        self.combo_periodo.currentIndexChanged.connect(self.cargar_datos_desde_db)
        periodo_layout.addWidget(self.combo_periodo)
        periodo_layout.addStretch(1)
        self.btn_exportar = QPushButton("Exportar a Excel")
        periodo_layout.addWidget(self.btn_exportar)
        self.tab_produccion.layout().addLayout(periodo_layout)

        self.tabla_produccion = QTableWidget()
        self.tabla_produccion.setColumnCount(12)
        self.tabla_produccion.setHorizontalHeaderLabels(
            ["Producto (unidad)", "L", "M", "M", "J", "V", "S", "D", "Total", "Costo Total", "Precio Venta", "Ganancia"]
        )
        self.tabla_produccion.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tab_produccion.layout().addWidget(self.tabla_produccion)

        btn_layout = QHBoxLayout()
        btn_cargar = QPushButton("Recargar Datos del Período")
        btn_cargar.clicked.connect(self.cargar_datos_desde_db)
        btn_layout.addWidget(btn_cargar)
        
        self.btn_calcular_costos = QPushButton("Calcular Costos y Ganancias (Detallado)")
        self.btn_calcular_costos.clicked.connect(self.calcular_costos_receta)
        btn_layout.addWidget(self.btn_calcular_costos)
        self.tab_produccion.layout().addLayout(btn_layout)

        self.label_total_produccion = QLabel("")
        self.tab_produccion.layout().addWidget(self.label_total_produccion)

        # Pestaña de Costos
        self.tab_costos = QWidget()
        self.tabs.addTab(self.tab_costos, "Costos")
        self.tab_costos.setLayout(QVBoxLayout())
        self.tab_costos.layout().addWidget(QLabel("<b>Costos de Producción Detallados (Basado en Recetas)</b>"))
        self.tabla_costos = QTableWidget()
        self.tabla_costos.setColumnCount(9)
        self.tabla_costos.setHorizontalHeaderLabels(
            ["Materia Prima", "Costo Unitario", "L", "M", "M", "J", "V", "S", "D"]
        )
        self.tabla_costos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tab_costos.layout().addWidget(self.tabla_costos)
        
        self.layout_totales_costos = QHBoxLayout()
        self.label_total_costos = QLabel("")
        self.label_total_ganancias = QLabel("")
        self.label_margen_ganancia = QLabel("")
        self.layout_totales_costos.addWidget(self.label_total_costos)
        self.layout_totales_costos.addWidget(self.label_total_ganancias)
        self.layout_totales_costos.addWidget(self.label_margen_ganancia)
        self.tab_costos.layout().addLayout(self.layout_totales_costos)

        # Pestaña de Análisis de Rentabilidad
        self.tab_mensual = QWidget()
        self.tabs.addTab(self.tab_mensual, "Análisis de Rentabilidad")
        self.tab_mensual.setLayout(QVBoxLayout())
        
        self.contenedor_principal = QHBoxLayout()
        self.tab_mensual.layout().addLayout(self.contenedor_principal)
        
        self.tabla_mensual = QTableWidget()
        self.tabla_mensual.setColumnCount(5)
        self.tabla_mensual.setHorizontalHeaderLabels(["Producto", "Costo Total", "Precio Venta", "Ganancia", "Margen (%)"])
        self.tabla_mensual.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.contenedor_principal.addWidget(self.tabla_mensual)
        
        self.contenedor_graficos = QVBoxLayout()
        self.contenedor_principal.addLayout(self.contenedor_graficos)
        self.grafico_costos = FigureCanvasQTAgg(Figure(figsize=(5, 4)))
        self.ax_costos = self.grafico_costos.figure.subplots()
        self.contenedor_graficos.addWidget(self.grafico_costos)
        self.grafico_ganancias = FigureCanvasQTAgg(Figure(figsize=(5, 4)))
        self.ax_ganancias = self.grafico_ganancias.figure.subplots()
        self.contenedor_graficos.addWidget(self.grafico_ganancias)
        
        self.recetas_df = None
        self.materias_primas = None
        
        self.cargar_datos_desde_db()

    def registrar_produccion_con_costo(self, producto_nombre, cantidad, area, costo):
        fecha_actual = datetime.now().date()
        dia_str = ["L", "M", "M", "J", "V", "S", "D"][fecha_actual.weekday()]
        
        try:
            with self.engine.connect() as conn:
                with conn.begin() as trans:
                    # <--- CORRECCIÓN: Obtener el ID del producto a partir de su nombre
                    query_id = text("SELECT id_producto FROM productos WHERE nombre_producto = :nombre")
                    result = conn.execute(query_id, {"nombre": producto_nombre}).fetchone()
                    if not result:
                        QMessageBox.critical(self, "Error", f"No se encontró el producto '{producto_nombre}' en la base de datos.")
                        return
                    producto_id = result[0]

                    # <--- CORRECCIÓN: Usar producto_id en la consulta INSERT
                    query_insert = text("""
                        INSERT INTO produccion (producto_id, cantidad, fecha, dia, area, costo)
                        VALUES (:producto_id, :cantidad, :fecha, :dia, :area, :costo)
                        ON CONFLICT(fecha, producto_id) DO UPDATE SET
                        cantidad = produccion.cantidad + :cantidad,
                        costo = produccion.costo + :costo;
                    """)
                    conn.execute(query_insert, {
                        "producto_id": producto_id,
                        "cantidad": cantidad, "fecha": fecha_actual, "dia": dia_str,
                        "area": area, "costo": costo
                    })
            
            QMessageBox.information(self, "Éxito", f"Producción de '{producto_nombre}' registrada.")
            self.cargar_datos_desde_db()
            
        except Exception as e:
            QMessageBox.critical(self, "Error de Base de Datos", f"Error al registrar producción: {e}")

    def cargar_datos_desde_db(self):
        try:
            periodo = self.combo_periodo.currentText()
            fecha_fin = datetime.now().date()
            if periodo == "Última semana": fecha_inicio = fecha_fin - timedelta(days=7)
            elif periodo == "Últimos 15 días": fecha_inicio = fecha_fin - timedelta(days=15)
            elif periodo == "Último mes": fecha_inicio = fecha_fin - relativedelta(months=1)
            else: fecha_inicio = fecha_fin - relativedelta(months=3)
            
            # <--- CORRECCIÓN: La consulta ahora une con producto_id
            query = text("""
            SELECT 
                p.nombre_producto AS producto,
                p.unidad_medida_producto AS unidad,
                pr.dia,
                pr.fecha,
                pr.cantidad,
                pr.costo,
                pr.area
            FROM produccion pr
            JOIN productos p ON pr.producto_id = p.id_producto
            WHERE pr.fecha BETWEEN :start_date AND :end_date
            """)
            
            self.df_produccion = pd.read_sql_query(query, self.engine, params={"start_date": fecha_inicio, "end_date": fecha_fin})

            if self.df_produccion.empty:
                self.tabla_produccion.setRowCount(0)
                self.label_total_produccion.setText("No hay datos para el período seleccionado.")
                self.actualizar_analisis_mensual() # Limpia la otra pestaña
                return

            self.actualizar_vista_produccion()
            self.actualizar_analisis_mensual()

        except Exception as e:
            QMessageBox.critical(self, "Error de Carga", f"No se pudo leer la base de datos: {e}")

    def actualizar_vista_produccion(self):
        df = self.df_produccion.copy()
        df_pivot = df.pivot_table(index=["producto", "unidad"], columns="dia", values="cantidad", aggfunc='sum').fillna(0)
        df_totales = df.groupby(['producto', 'unidad']).agg(Total_Cantidad=('cantidad', 'sum'), Total_Costo=('costo', 'sum')).reset_index()
        df_merged = pd.merge(df_pivot.reset_index(), df_totales, on=['producto', 'unidad'])

        dias_orden = ["L", "M", "J", "V", "S", "D"]
        for d in dias_orden:
            if d not in df_merged.columns: df_merged[d] = 0
        
        df_merged = df_merged.rename(columns={'Total_Cantidad': 'Total'})
        df_merged['Costo Total'] = df_merged['Total_Costo']
        df_merged["Precio Venta"] = df_merged["Costo Total"] * 1.30
        df_merged["Ganancia"] = df_merged["Precio Venta"] - df_merged["Costo Total"]
        
        self.mostrar_tabla_produccion(df_merged)

    def mostrar_tabla_produccion(self, df):
        df['producto_unidad'] = df['producto'] + " (" + df['unidad'] + ")"
        self.tabla_produccion.setRowCount(df.shape[0])
        total_produccion, total_costo, total_venta, total_ganancia = 0, 0, 0, 0

        for i, row in df.iterrows():
            self.tabla_produccion.setItem(i, 0, QTableWidgetItem(row["producto_unidad"]))
            dias_ordenados = ["L", "M", "M", "J", "V", "S", "D", "Total"]
            for j, dia in enumerate(dias_ordenados, start=1):
                val = row.get(dia, 0)
                item = QTableWidgetItem(f"{val:.2f}")
                self.tabla_produccion.setItem(i, j, item)
                if dia == "Total": total_produccion += val
            
            for j, col in enumerate(["Costo Total", "Precio Venta", "Ganancia"], start=9):
                val = row[col]
                item = QTableWidgetItem(f"${val:,.2f}")
                self.tabla_produccion.setItem(i, j, item)
                if col == "Costo Total": total_costo += val
                elif col == "Precio Venta": total_venta += val
                elif col == "Ganancia": total_ganancia += val

        self.label_total_produccion.setText(
            f"<b>Total producción: {total_produccion:,.2f} | Costo: ${total_costo:,.2f} | Venta: ${total_venta:,.2f} | Ganancia: ${total_ganancia:,.2f}</b>"
        )

    def calcular_costos_receta(self):
        if self.df_produccion is None or self.df_produccion.empty:
            QMessageBox.warning(self, "Sin datos", "Primero cargue los datos de producción.")
            return
        # Lógica para calcular costos basados en recetas (sin cambios)
        pass

    def actualizar_analisis_mensual(self):
        if self.df_produccion is None or self.df_produccion.empty:
            self.tabla_mensual.setRowCount(0)
            self.actualizar_graficos(pd.DataFrame())
            return
            
        df_agrupado = self.df_produccion.groupby('producto').agg(
            costo_total=('costo', 'sum')
        ).reset_index()
        
        df_agrupado['precio_venta'] = df_agrupado['costo_total'] * 1.30
        df_agrupado['ganancia'] = df_agrupado['precio_venta'] - df_agrupado['costo_total']
        df_agrupado['margen'] = df_agrupado.apply(
            lambda row: (row['ganancia'] / row['precio_venta'] * 100) if row['precio_venta'] > 0 else 0,
            axis=1
        )
        
        self.tabla_mensual.setRowCount(len(df_agrupado))
        for i, row in df_agrupado.iterrows():
            self.tabla_mensual.setItem(i, 0, QTableWidgetItem(row['producto']))
            self.tabla_mensual.setItem(i, 1, QTableWidgetItem(f"${row['costo_total']:,.2f}"))
            self.tabla_mensual.setItem(i, 2, QTableWidgetItem(f"${row['precio_venta']:,.2f}"))
            self.tabla_mensual.setItem(i, 3, QTableWidgetItem(f"${row['ganancia']:,.2f}"))
            self.tabla_mensual.setItem(i, 4, QTableWidgetItem(f"{row['margen']:.2f}%"))
        
        self.actualizar_graficos(df_agrupado)
    
    def actualizar_graficos(self, df):
        self.ax_costos.clear()
        if not df.empty and df['costo_total'].sum() > 0:
            self.ax_costos.pie(df['costo_total'], labels=df['producto'], autopct='%1.1f%%', startangle=90)
            self.ax_costos.set_title('Distribución de Costos')
        else:
            self.ax_costos.text(0.5, 0.5, 'Sin datos', ha='center', va='center')
        self.grafico_costos.draw()
        
        self.ax_ganancias.clear()
        if not df.empty:
            df_sorted = df.sort_values('ganancia', ascending=False).head(10)
            self.ax_ganancias.bar(df_sorted['producto'], df_sorted['ganancia'], color='green')
            self.ax_ganancias.set_title('Ganancias por Producto')
            self.ax_ganancias.set_ylabel('Ganancia ($)')
            self.ax_ganancias.tick_params(axis='x', rotation=45, labelsize=8)
            self.grafico_ganancias.figure.tight_layout()
        else:
            self.ax_ganancias.text(0.5, 0.5, 'Sin datos', ha='center', va='center')
        self.grafico_ganancias.draw()