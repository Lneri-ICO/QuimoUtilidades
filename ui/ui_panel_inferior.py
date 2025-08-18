from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QMessageBox, QHBoxLayout, QTabWidget,
    QComboBox, QGroupBox, QGridLayout
)
from PyQt6.QtCore import Qt
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class PanelInferior(QWidget):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.setLayout(QVBoxLayout())
        
        # Crear pestañas para organizar mejor la información
        self.tabs = QTabWidget()
        self.layout().addWidget(self.tabs)
        
        # Pestaña de Producción
        self.tab_produccion = QWidget()
        self.tabs.addTab(self.tab_produccion, "Producción")
        self.tab_produccion.setLayout(QVBoxLayout())
        
        # Sección de producción
        layout_produccion = QHBoxLayout()
        layout_produccion.addWidget(QLabel("<b>Producción Semanal</b>"))
        self.btn_exportar = QPushButton("Exportar a Excel")
        layout_produccion.addWidget(self.btn_exportar)
        layout_produccion.addStretch()
        self.tab_produccion.layout().addLayout(layout_produccion)

        # Tabla de producción
        self.tabla_produccion = QTableWidget()
        self.tab_produccion.layout().addWidget(self.tabla_produccion)

        self.tabla_produccion.setColumnCount(12)  # Agregar columnas para costos y ganancias
        self.tabla_produccion.setHorizontalHeaderLabels(
            ["Producto (unidad)", "L", "M", "M", "J", "V", "S", "D", "Total", "Costo Total", "Precio Venta", "Ganancia"]
        )
        self.tabla_produccion.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Botones
        btn_layout = QHBoxLayout()
        btn_cargar = QPushButton("Cargar Producción")
        btn_cargar.clicked.connect(self.cargar_datos_desde_db)
        btn_layout.addWidget(btn_cargar)
        
        self.btn_calcular_costos = QPushButton("Calcular Costos y Ganancias")
        self.btn_calcular_costos.clicked.connect(self.calcular_costos)
        btn_layout.addWidget(self.btn_calcular_costos)
        self.tab_produccion.layout().addLayout(btn_layout)

        self.label_total_produccion = QLabel("")
        self.tab_produccion.layout().addWidget(self.label_total_produccion)

        # Pestaña de Costos
        self.tab_costos = QWidget()
        self.tabs.addTab(self.tab_costos, "Costos")
        self.tab_costos.setLayout(QVBoxLayout())
        
        # Sección de costos
        self.tab_costos.layout().addWidget(QLabel("<b>Costos de Producción</b>"))
        
        # Tabla de costos detallada
        self.tabla_costos = QTableWidget()
        self.tab_costos.layout().addWidget(self.tabla_costos)
        self.tabla_costos.setColumnCount(9)
        self.tabla_costos.setHorizontalHeaderLabels(
            ["Materia Prima", "Costo Unitario", "L", "M", "M", "J", "V", "S", "D"]
        )
        self.tabla_costos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Totales de costos
        self.layout_totales_costos = QHBoxLayout()
        self.label_total_costos = QLabel("")
        self.label_total_ganancias = QLabel("")
        self.label_margen_ganancia = QLabel("")
        
        self.layout_totales_costos.addWidget(self.label_total_costos)
        self.layout_totales_costos.addWidget(self.label_total_ganancias)
        self.layout_totales_costos.addWidget(self.label_margen_ganancia)
        
        self.tab_costos.layout().addLayout(self.layout_totales_costos)

        # Variables para almacenar datos
        self.df_produccion = None
        self.df_costos = None
        self.recetas_df = None
        self.materias_primas = None
        
        # Pestaña de Análisis Mensual
        self.tab_mensual = QWidget()
        self.tabs.addTab(self.tab_mensual, "Análisis Mensual")
        self.tab_mensual.setLayout(QVBoxLayout())
        
        # Selector de período
        periodo_layout = QHBoxLayout()
        periodo_layout.addWidget(QLabel("Período:"))
        self.combo_periodo = QComboBox()
        self.combo_periodo.addItems(["Última semana", "Últimos 15 días", "Último mes", "Últimos 3 meses"])
        self.combo_periodo.currentIndexChanged.connect(self.actualizar_analisis_mensual)
        periodo_layout.addWidget(self.combo_periodo)
        periodo_layout.addStretch(1)
        self.tab_mensual.layout().addLayout(periodo_layout)
        
        # Contenedor para gráficos y tabla
        self.contenedor_principal = QHBoxLayout()
        self.tab_mensual.layout().addLayout(self.contenedor_principal)
        
        # Tabla de resumen mensual
        self.tabla_mensual = QTableWidget()
        self.tabla_mensual.setColumnCount(5)
        self.tabla_mensual.setHorizontalHeaderLabels(["Producto", "Costo Total", "Precio Venta", "Ganancia", "Margen (%)"])
        self.tabla_mensual.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.contenedor_principal.addWidget(self.tabla_mensual)
        
        # Contenedor para gráficos
        self.contenedor_graficos = QVBoxLayout()
        self.contenedor_principal.addLayout(self.contenedor_graficos)
        
        # Gráfico de torta para costos
        self.grafico_costos = FigureCanvasQTAgg(Figure(figsize=(5, 4)))
        self.ax_costos = self.grafico_costos.figure.subplots()
        self.contenedor_graficos.addWidget(self.grafico_costos)
        
        # Gráfico de barras para ganancias
        self.grafico_ganancias = FigureCanvasQTAgg(Figure(figsize=(5, 4)))
        self.ax_ganancias = self.grafico_ganancias.figure.subplots()
        self.contenedor_graficos.addWidget(self.grafico_ganancias)
        
        # Cargar datos iniciales para análisis mensual
        self.actualizar_analisis_mensual()

    def conectar_panel_derecho(self, panel_derecho):
        """Conectar las señales del panel derecho"""
        panel_derecho.produccion_registrada.connect(self.registrar_produccion)

    def registrar_produccion(self, producto, cantidad, area):
        """Registrar producción en la semana actual"""
        fecha_actual = datetime.now().date()
        
        # Obtener día de la semana (0=lunes, 6=domingo)
        dia_semana = fecha_actual.weekday()
        dias = ["L", "M", "M", "J", "V", "S", "D"]
        dia = dias[dia_semana]
        
        # Registrar en la base de datos
        try:
            with self.engine.connect() as conn:
                # Insertar o actualizar registro
                query = text("""
                    INSERT INTO produccion (producto, cantidad, fecha, dia, area)
                    VALUES (:producto, :cantidad, :fecha, :dia, :area)
                    ON CONFLICT(fecha, producto) DO UPDATE SET
                    cantidad = produccion.cantidad + :cantidad
                """)
                conn.execute(query, {
                    "producto": producto,
                    "cantidad": cantidad,
                    "fecha": fecha_actual,
                    "dia": dia,
                    "area": area
                })
            
            # Actualizar la tabla visual
            self.cargar_datos_desde_db()
            
        except Exception as e:
            print(f"Error al registrar producción: {e}")

    def cargar_datos_desde_db(self):
        try:
            query = """
            SELECT 
                p.id_producto,
                p.nombre_producto AS producto,
                p.unidad_medida_producto AS unidad,
                pr.dia,
                pr.fecha,
                pr.cantidad
            FROM produccion pr
            JOIN productos p ON pr.producto_id = p.id_producto
            WHERE pr.fecha >= DATE('now', '-7 days')  -- Últimos 7 días
            """
            
            df = pd.read_sql_query(query, self.engine)
            
            # Convertir fecha a tipo datetime
            if 'fecha' in df.columns:
                df['fecha'] = pd.to_datetime(df['fecha'])
            
            # Cargar recetas
            recetas_query = """
            SELECT 
                r.producto_id,
                r.materia_prima_id,
                mp.nombre_mp AS materia_prima,
                r.cantidad_mp_por_unidad AS cantidad,
                COALESCE(mp.costo_unitario_mp, 0) AS precio
            FROM formulas r
            JOIN materiasprimas mp ON r.id_mp = mp.id_mp
            """
            self.recetas_df = pd.read_sql_query(recetas_query, self.engine)
            
            # Cargar materias primas
            mp_query = "SELECT id_mp, nombre_mp, costo_unitario_mp FROM materiasprimas"
            self.materias_primas = pd.read_sql_query(mp_query, self.engine)

            if df.empty:
                QMessageBox.information(self, "Sin datos", "No hay datos de producción registrados")
                return

            # Guardar el DataFrame para usar en el cálculo de costos
            self.df_produccion = df.copy()

            # Procesar datos para mostrar
            df["producto_unidad"] = df["producto"] + " (" + df["unidad"] + ")"
            tabla = df.pivot_table(index=["id_producto", "producto_unidad"], 
                                  columns="dia", 
                                  values="cantidad", 
                                  aggfunc='sum').fillna(0)

            # Asegurar columnas en orden de semana
            dias_orden = ["L", "M", "M", "J", "V", "S", "D"]
            for d in dias_orden:
                if d not in tabla.columns:
                    tabla[d] = 0

            tabla = tabla[dias_orden]
            tabla["Total"] = tabla.sum(axis=1)

            # Inicializar columnas de costos y ganancias
            tabla["Costo Total"] = 0.0
            tabla["Precio Venta"] = 0.0
            tabla["Ganancia"] = 0.0

            self.mostrar_tabla_produccion(tabla)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo leer la base de datos:\n{e}")

    def mostrar_tabla_produccion(self, df):
        if df is None or df.empty:
            self.tabla_produccion.setRowCount(0)
            self.tabla_produccion.setColumnCount(0)
            self.label_total_produccion.setText("Sin datos")
            return

        self.tabla_produccion.setRowCount(df.shape[0])
        self.tabla_produccion.setColumnCount(12)
        self.tabla_produccion.setHorizontalHeaderLabels(
            ["Producto (unidad)", "L", "M", "M", "J", "V", "S", "D", "Total", "Costo Total", "Precio Venta", "Ganancia"]
        )

        total_produccion = 0
        total_costo = 0
        total_venta = 0
        total_ganancia = 0

        for i, (index, row) in enumerate(df.iterrows()):
            id_producto, producto_unidad = index
            
            # Columna 0: Producto
            self.tabla_produccion.setItem(i, 0, QTableWidgetItem(producto_unidad))
            
            # Columnas 1-8: Días y Total
            dias_ordenados = ["L", "M", "M", "J", "V", "S", "D", "Total"]
            for j, dia in enumerate(dias_ordenados, start=1):
                val = row[dia] if dia in row else 0
                item = QTableWidgetItem(str(round(val, 2)))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabla_produccion.setItem(i, j, item)
                
                if dia == "Total":
                    total_produccion += val
            
            # Columnas 9-11: Costo, Precio Venta, Ganancia
            for j, col in enumerate(["Costo Total", "Precio Venta", "Ganancia"], start=9):
                val = row[col] if col in row else 0
                item = QTableWidgetItem(f"${val:,.2f}")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabla_produccion.setItem(i, j, item)
                
                if col == "Costo Total":
                    total_costo += val
                elif col == "Precio Venta":
                    total_venta += val
                elif col == "Ganancia":
                    total_ganancia += val

        self.label_total_produccion.setText(
            f"<b>Total producción: {total_produccion} unidades | "
            f"Costo total: ${total_costo:,.2f} | "
            f"Venta total: ${total_venta:,.2f} | "
            f"Ganancia: ${total_ganancia:,.2f}</b>"
        )

    def calcular_costos(self):
        if self.df_produccion is None or self.df_produccion.empty:
            QMessageBox.warning(self, "Sin datos", "Primero cargue los datos de producción")
            return
            
        try:
            # Crear DataFrame para costos detallados
            dias = ["L", "M", "M", "J", "V", "S", "D"]
            costos_detallados = pd.DataFrame(0, index=self.materias_primas["id_mp"], columns=dias)
            costos_detallados["Materia Prima"] = self.materias_primas.set_index("id_mp")["nombre_mp"]
            costos_detallados["Costo Unitario"] = self.materias_primas.set_index("id_mp")["costo_unitario_mp"]
            
            # Calcular costos para cada producto
            for _, prod_row in self.df_produccion.iterrows():
                id_producto = prod_row["id_producto"]
                
                # Filtrar recetas para este producto
                recetas_producto = self.recetas_df[self.recetas_df["producto_id"] == id_producto]
                
                for _, receta in recetas_producto.iterrows():
                    id_mp = receta["materia_prima_id"]
                    cantidad_mp = receta["cantidad"]
                    precio_mp = receta["precio"]
                    
                    # Distribuir el costo por día
                    for dia in dias:
                        if dia in prod_row and not pd.isna(prod_row[dia]):
                            cantidad_dia = prod_row[dia]
                            costo_dia = cantidad_dia * cantidad_mp * precio_mp
                            if id_mp in costos_detallados.index:
                                costos_detallados.loc[id_mp, dia] += costo_dia
            
            # Calcular totales para la tabla de costos
            costos_detallados["Total"] = costos_detallados[dias].sum(axis=1)
            
            # Guardar para mostrar
            self.df_costos = costos_detallados
            self.mostrar_tabla_costos()
            
            # Calcular ganancias para la tabla de producción
            self.calcular_ganancias()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron calcular los costos:\n{e}")

    def calcular_ganancias(self):
        """Calcula ganancias del 30% para productos vendidos"""
        if self.df_produccion is None:
            return
            
        # Crear una copia para modificar
        df = self.df_produccion.copy()
        
        for i, (index, row) in enumerate(df.iterrows()):
            id_producto, _ = index
            
            # Obtener receta para este producto
            recetas_producto = self.recetas_df[self.recetas_df["producto_id"] == id_producto]
            costo_total = 0
            
            # Calcular costo total del producto
            for _, receta in recetas_producto.iterrows():
                cantidad_mp = receta["cantidad"]
                precio_mp = receta["precio"]
                # Usamos la producción total del producto
                costo_total += row["Total"] * cantidad_mp * precio_mp
            
            # Aplicar 30% de ganancia
            precio_venta = costo_total * 1.30
            ganancia = precio_venta - costo_total
            
            # Actualizar valores en el DataFrame
            df.loc[index, "Costo Total"] = costo_total
            df.loc[index, "Precio Venta"] = precio_venta
            df.loc[index, "Ganancia"] = ganancia
        
        # Actualizar y mostrar
        self.df_produccion = df
        self.mostrar_tabla_produccion(df)

    def mostrar_tabla_costos(self):
        if self.df_costos is None or self.df_costos.empty:
            self.tabla_costos.setRowCount(0)
            self.tabla_costos.setColumnCount(0)
            return

        # Configurar tabla
        dias = ["L", "M", "M", "J", "V", "S", "D"]
        self.tabla_costos.setRowCount(len(self.df_costos))
        self.tabla_costos.setColumnCount(len(dias) + 2)  # +2 para Materia Prima y Costo Unitario
        self.tabla_costos.setHorizontalHeaderLabels(
            ["Materia Prima", "Costo Unitario"] + dias
        )
        
        total_costos = 0
        
        for i, (_, row) in enumerate(self.df_costos.iterrows()):
            # Materia Prima
            item_mp = QTableWidgetItem(row["Materia Prima"])
            self.tabla_costos.setItem(i, 0, item_mp)
            
            # Costo Unitario
            item_cu = QTableWidgetItem(f"${row['Costo Unitario']:,.2f}")
            item_cu.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla_costos.setItem(i, 1, item_cu)
            
            # Costos por día
            for j, dia in enumerate(dias, start=2):
                costo = row[dia]
                item = QTableWidgetItem(f"${costo:,.2f}")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabla_costos.setItem(i, j, item)
                
                total_costos += costo
        
        # Calcular ganancias
        total_ventas = total_costos * 1.30
        total_ganancias = total_ventas - total_costos
        margen_ganancia = (total_ganancias / total_ventas * 100) if total_ventas > 0 else 0
        
        # Actualizar labels
        self.label_total_costos.setText(f"<b>Costo total: ${total_costos:,.2f}</b>")
        self.label_total_ganancias.setText(f"<b>Ganancia total: ${total_ganancias:,.2f}</b>")
        self.label_margen_ganancia.setText(f"<b>Margen de ganancia: {margen_ganancia:.2f}%</b>")
    
    def actualizar_analisis_mensual(self):
        """Actualiza el análisis mensual basado en el período seleccionado"""
        if self.df_produccion is None or self.recetas_df is None:
            return
            
        # Determinar el rango de fechas
        periodo = self.combo_periodo.currentText()
        fecha_fin = datetime.now()
        
        if periodo == "Última semana":
            fecha_inicio = fecha_fin - timedelta(days=7)
        elif periodo == "Últimos 15 días":
            fecha_inicio = fecha_fin - timedelta(days=15)
        elif periodo == "Último mes":
            fecha_inicio = fecha_fin - relativedelta(months=1)
        else:  # Últimos 3 meses
            fecha_inicio = fecha_fin - relativedelta(months=3)
        
        # Filtrar datos por período
        df_filtrado = self.df_produccion[
            (self.df_produccion['fecha'] >= fecha_inicio) & 
            (self.df_produccion['fecha'] <= fecha_fin)
        ]
        
        if df_filtrado.empty:
            self.tabla_mensual.setRowCount(0)
            return
            
        # Agrupar por producto
        df_agrupado = df_filtrado.groupby(['id_producto', 'producto']).agg({
            'cantidad': 'sum'
        }).reset_index()
        
        # Calcular costos y ganancias
        resumen = []
        for _, row in df_agrupado.iterrows():
            id_producto = row['id_producto']
            cantidad_total = row['cantidad']
            
            # Filtrar recetas para este producto
            recetas_producto = self.recetas_df[self.recetas_df["producto_id"] == id_producto]
            costo_total = 0
            
            # Calcular costo total del producto
            for _, receta in recetas_producto.iterrows():
                cantidad_mp = receta["cantidad"]
                precio_mp = receta["precio"]
                costo_total += cantidad_total * cantidad_mp * precio_mp
            
            # Aplicar 30% de ganancia
            precio_venta = costo_total * 1.30
            ganancia = precio_venta - costo_total
            margen = (ganancia / precio_venta * 100) if precio_venta > 0 else 0
            
            resumen.append({
                'Producto': row['producto'],
                'Costo Total': costo_total,
                'Precio Venta': precio_venta,
                'Ganancia': ganancia,
                'Margen (%)': margen
            })
        
        # Crear DataFrame de resumen
        df_resumen = pd.DataFrame(resumen)
        
        # Mostrar en tabla
        self.tabla_mensual.setRowCount(len(df_resumen))
        for i, (_, row) in enumerate(df_resumen.iterrows()):
            self.tabla_mensual.setItem(i, 0, QTableWidgetItem(row['Producto']))
            self.tabla_mensual.setItem(i, 1, QTableWidgetItem(f"${row['Costo Total']:,.2f}"))
            self.tabla_mensual.setItem(i, 2, QTableWidgetItem(f"${row['Precio Venta']:,.2f}"))
            self.tabla_mensual.setItem(i, 3, QTableWidgetItem(f"${row['Ganancia']:,.2f}"))
            self.tabla_mensual.setItem(i, 4, QTableWidgetItem(f"{row['Margen (%)']:.2f}%"))
        
        # Actualizar gráficos
        self.actualizar_graficos(df_resumen)
    
    def actualizar_graficos(self, df):
        """Actualiza los gráficos con los datos del resumen"""
        # Gráfico de torta: Distribución de costos
        self.ax_costos.clear()
        if not df.empty:
            costos = df.groupby('Producto')['Costo Total'].sum()
            self.ax_costos.pie(costos, labels=costos.index, autopct='%1.1f%%', startangle=90)
            self.ax_costos.set_title('Distribución de Costos')
        self.grafico_costos.draw()
        
        # Gráfico de barras: Comparación de ganancias
        self.ax_ganancias.clear()
        if not df.empty:
            productos = df['Producto']
            ganancias = df['Ganancia']
            self.ax_ganancias.bar(productos, ganancias, color='green')
            self.ax_ganancias.set_title('Ganancias por Producto')
            self.ax_ganancias.set_ylabel('Ganancia ($)')
            self.ax_ganancias.tick_params(axis='x', rotation=45)
        self.grafico_ganancias.draw()