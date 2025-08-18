# ui/ui_panel_derecho.py (VERSIÓN FINAL, COMPLETA Y CORREGIDA)

from PyQt6.QtWidgets import (
    QTabWidget, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QCompleter, QFrame, QMessageBox,
    QDialog, QSpinBox, QHBoxLayout, QComboBox, QRadioButton, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt
from sqlalchemy import text # Importante para ejecutar consultas con SQLAlchemy
from datetime import datetime

# --- CLASE PARA LA VENTANA EMERGENTE DE ACTUALIZACIÓN MÚLTIPLE ---
class VentanaActualizacionMultiple(QDialog):
    def __init__(self, parent=None, productos=None, table_type="productos", engine=None):
        super().__init__(parent)
        self.setWindowTitle(f"Actualizar Múltiple")
        self.setMinimumWidth(400)
        self.productos = productos or []
        self.current_table_type = table_type
        self.engine = engine
        self.config_labels = {
            "productos": "producto", "materiasprimas": "materia prima", "productosreventa": "producto de reventa",
        }
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(QLabel(f"¿Cuántos {self.config_labels.get(self.current_table_type, 'items')}s actualizarás?"))
        self.spin_cantidad = QSpinBox()
        self.spin_cantidad.setRange(1, 50)
        self.layout.addWidget(self.spin_cantidad)
        btn_generar = QPushButton("Generar Campos")
        btn_generar.clicked.connect(self.generar_campos)
        self.layout.addWidget(btn_generar)
        self.campos_layout = QVBoxLayout()
        self.layout.addLayout(self.campos_layout)
        self.btn_guardar = QPushButton("Guardar Cambios")
        self.btn_guardar.clicked.connect(self.guardar_cambios)
        self.btn_guardar.setEnabled(False)
        self.layout.addWidget(self.btn_guardar)
        self.campos = []

    def generar_campos(self):
        while self.campos_layout.count():
            item = self.campos_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    sub_item = item.layout().takeAt(0)
                    if sub_item.widget(): sub_item.widget().deleteLater()
        self.campos.clear()
        cantidad = self.spin_cantidad.value()
        nombre_campo = f"Nombre del {self.config_labels.get(self.current_table_type, 'item')}"
        for i in range(cantidad):
            h_layout = QHBoxLayout()
            le_nombre = QLineEdit(placeholderText=f"{nombre_campo} #{i+1}")
            completer = QCompleter(self.productos)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            le_nombre.setCompleter(completer)
            le_cantidad = QLineEdit(placeholderText=f"Nueva Cantidad #{i+1}")
            h_layout.addWidget(le_nombre)
            h_layout.addWidget(le_cantidad)
            self.campos_layout.addLayout(h_layout)
            self.campos.append((le_nombre, le_cantidad))
        self.btn_guardar.setEnabled(True)

    def guardar_cambios(self):
        if not self.engine:
            QMessageBox.critical(self, "Error", "No hay conexión a la base de datos.")
            return
        try:
            with self.engine.connect() as conn:
                with conn.begin() as trans:
                    table_configs = {
                        "productos": ("productos", "cantidad_producto", "nombre_producto"),
                        "materiasprimas": ("materiasprimas", "cantidad_comprada_mp", "nombre_mp"),
                        "productosreventa": ("productosreventa", "cantidad_prev", "nombre_prev")
                    }
                    if self.current_table_type not in table_configs: return
                    tabla, col_cantidad, col_nombre = table_configs[self.current_table_type]
                    errores = []
                    for idx, (le_nombre, le_cantidad) in enumerate(self.campos):
                        nombre, cantidad_str = le_nombre.text().strip(), le_cantidad.text().strip()
                        if not nombre or not cantidad_str:
                            errores.append(f"Fila {idx+1}: Campos vacíos.")
                            continue
                        try:
                            cantidad = float(cantidad_str)
                        except ValueError:
                            errores.append(f"Fila {idx+1}: La cantidad debe ser un número.")
                            continue
                        query = text(f"UPDATE {tabla} SET {col_cantidad} = :cantidad WHERE {col_nombre} = :nombre")
                        result = conn.execute(query, {"cantidad": cantidad, "nombre": nombre})
                        if result.rowcount == 0:
                            errores.append(f"Fila {idx+1}: '{nombre}' no encontrado.")
                    if errores:
                        QMessageBox.warning(self, "Advertencia", "No se guardaron los cambios:\n" + "\n".join(errores))
                        trans.rollback()
                    else:
                        QMessageBox.information(self, "Éxito", "Cambios guardados correctamente.")
                        self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error de base de datos: {e}")

# --- PANEL DERECHO PRINCIPAL ---
class PanelDerecho(QTabWidget):
    def __init__(self, tabla_referencia, actualizar_tabla_callback, obtener_tipo_tabla, engine):
        super().__init__()
        self.tabla_referencia = tabla_referencia
        self.actualizar_tabla_callback = actualizar_tabla_callback
        self.obtener_tipo_tabla = obtener_tipo_tabla
        self.engine = engine
        self.setFixedWidth(400)
        self.materias_primas = []
        self.proveedores = []
        self.proveedor_id_map = {}
        
        self.tab_entrada = self.crear_tab_entrada()
        self.tab_salida = self.crear_tab_salida()
        self.tab_gestion = self.crear_tab_gestion()
        self.addTab(self.tab_entrada, "Entrada")
        self.addTab(self.tab_salida, "Salida")
        self.addTab(self.tab_gestion, "Gestión")
        self.configuracion_ui = {
            "productos": {
                "nombre_label": "Producto:", "nombre_placeholder": "Nombre del producto",
                "area_label": "Área:", "area_placeholder": "Área (QUIMO/QUIMO CLEAN)",
                "unidad_placeholder_gestion": "Unidad (KG, L, PZA...)"},
            "materiasprimas": {
                "nombre_label": "Materia Prima:", "nombre_placeholder": "Nombre de la materia prima",
                "proveedor_label": "Proveedor:", "proveedor_placeholder": "Nombre del proveedor",
                "unidad_placeholder_gestion": "Unidad (KG, L, PZA...)"},
            "productosreventa": {
                "nombre_label": "Producto Reventa:", "nombre_placeholder": "Nombre del producto de reventa",
                "proveedor_label": "Proveedor:", "proveedor_placeholder": "Nombre del proveedor",
                "area_label": "Área:", "area_placeholder": "Área (QUIMO/QUIMO CLEAN)",
                "unidad_placeholder_gestion": "Unidad (KG, L, PZA...)"}
        }
        
        self.cargar_materias_primas()
        self.cargar_proveedores()
        self.actualizar_labels_con_tipo(self.obtener_tipo_tabla())
        self.configurar_autocompletado()
    
    def crear_tab_entrada(self):
        layout = QVBoxLayout()
        self.nombre_entrada = QLineEdit()
        self.nombre_entrada.editingFinished.connect(lambda: self.autocompletar('entrada'))
        self.cantidad_entrada = QLineEdit(placeholderText="Cantidad")
        self.label_info_entrada = QLabel("...")
        self.btn_guardar_entrada = QPushButton("Registrar Entrada")
        self.btn_guardar_entrada.clicked.connect(self.registrar_entrada)
        btn_cancelar = QPushButton("Limpiar")
        btn_cancelar.clicked.connect(lambda: self.limpiar_formulario("entrada"))
        layout.addWidget(QLabel("Registrar Entrada"))
        layout.addWidget(self.nombre_entrada)
        layout.addWidget(self.cantidad_entrada)
        layout.addWidget(self.label_info_entrada)
        layout.addWidget(self.btn_guardar_entrada)
        layout.addWidget(btn_cancelar)
        tab = QWidget()
        tab.setLayout(layout)
        return tab

    def crear_tab_salida(self):
        layout = QVBoxLayout()
        self.nombre_salida = QLineEdit()
        self.nombre_salida.editingFinished.connect(lambda: self.autocompletar('salida'))
        self.cantidad_salida = QLineEdit(placeholderText="Cantidad")
        self.label_info_salida = QLabel("...")
        self.btn_guardar_salida = QPushButton("Registrar Salida")
        self.btn_guardar_salida.clicked.connect(self.registrar_salida)
        btn_cancelar = QPushButton("Limpiar")
        btn_cancelar.clicked.connect(lambda: self.limpiar_formulario("salida"))
        layout.addWidget(QLabel("Registrar Salida"))
        layout.addWidget(self.nombre_salida)
        layout.addWidget(self.cantidad_salida)
        layout.addWidget(self.label_info_salida)
        layout.addWidget(self.btn_guardar_salida)
        layout.addWidget(btn_cancelar)
        tab = QWidget()
        tab.setLayout(layout)
        return tab

    def crear_tab_gestion(self):
        layout = QVBoxLayout()
        self.nuevo_nombre = QLineEdit()
        self.nuevo_nombre.editingFinished.connect(lambda: self.autocompletar("gestion"))
        self.label_gestion_unidad = QLabel("Unidad de Medida:")
        self.nueva_unidad_combobox = QComboBox()
        self.nueva_unidad_combobox.addItems(["KG", "L", "PZA", "GAL"])
        
        self.label_gestion_proveedor = QLabel()
        self.nuevo_proveedor_combobox = QComboBox()
        
        self.label_gestion_area = QLabel()
        self.nuevo_area_combobox = QComboBox()
        
        estatus_frame = QFrame()
        estatus_layout = QHBoxLayout(estatus_frame)
        estatus_layout.setContentsMargins(0,0,0,0)
        self.label_gestion_estatus = QLabel("Estatus:")
        self.radio_estatus_activo = QRadioButton("Activo")
        self.radio_estatus_inactivo = QRadioButton("Inactivo")
        self.radio_estatus_activo.setChecked(True)
        estatus_layout.addWidget(self.radio_estatus_activo)
        estatus_layout.addWidget(self.radio_estatus_inactivo)
        self.label_info_gestion = QLabel("...")
        self.label_info_gestion.setWordWrap(True)
        
        self.formula_group_box = QFrame()
        self.formula_group_box.setFrameShape(QFrame.Shape.StyledPanel)
        formula_layout = QVBoxLayout(self.formula_group_box)
        formula_layout.addWidget(QLabel("Fórmula del Producto"))
        formula_input_layout = QHBoxLayout()
        self.formula_mp_combo = QComboBox()
        self.formula_porcentaje_input = QLineEdit(placeholderText="Porcentaje (%)")
        self.formula_porcentaje_input.setFixedWidth(100)
        self.formula_add_btn = QPushButton("Añadir")
        self.formula_add_btn.clicked.connect(self.anadir_materia_a_formula)
        formula_input_layout.addWidget(self.formula_mp_combo)
        formula_input_layout.addWidget(self.formula_porcentaje_input)
        formula_input_layout.addWidget(self.formula_add_btn)
        formula_layout.addLayout(formula_input_layout)
        self.formula_table = QTableWidget()
        self.formula_table.setColumnCount(2)
        self.formula_table.setHorizontalHeaderLabels(["Materia Prima", "Porcentaje"])
        self.formula_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.formula_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        formula_layout.addWidget(self.formula_table)
        self.formula_remove_btn = QPushButton("Quitar Materia Prima Seleccionada")
        self.formula_remove_btn.clicked.connect(self.quitar_materia_de_formula)
        formula_layout.addWidget(self.formula_remove_btn)
        
        btn_agregar = QPushButton("Agregar / Actualizar")
        btn_agregar.clicked.connect(self.guardar_producto)
        btn_baja = QPushButton("Dar de Baja")
        btn_baja.clicked.connect(self.dar_de_baja_producto)
        btn_multi = QPushButton("Actualizar Varios")
        btn_multi.clicked.connect(self.abrir_ventana_multiple)
        self.label_gestion_nombre = QLabel()
        
        layout.addWidget(QLabel("Gestión de Inventario"))
        layout.addWidget(self.label_gestion_nombre)
        layout.addWidget(self.nuevo_nombre)
        layout.addWidget(self.label_gestion_unidad)
        layout.addWidget(self.nueva_unidad_combobox)
        layout.addWidget(self.label_gestion_proveedor)
        layout.addWidget(self.nuevo_proveedor_combobox)
        layout.addWidget(self.label_gestion_area)
        layout.addWidget(self.nuevo_area_combobox)
        layout.addWidget(self.label_gestion_estatus)
        layout.addWidget(estatus_frame)
        layout.addWidget(self.formula_group_box)
        layout.addWidget(btn_agregar)
        layout.addWidget(btn_baja)
        layout.addWidget(btn_multi)
        layout.addWidget(self.label_info_gestion)
        tab = QWidget()
        tab.setLayout(layout)
        return tab
        
    def configurar_autocompletado(self, tipo_tabla=None):
        if not self.engine: return
        try:
            with self.engine.connect() as conn:
                tipo_tabla = tipo_tabla or self.obtener_tipo_tabla()
                queries = {
                    "productos": text("SELECT nombre_producto FROM productos ORDER BY nombre_producto"),
                    "materiasprimas": text("SELECT nombre_mp FROM materiasprimas ORDER BY nombre_mp"),
                    "productosreventa": text("SELECT nombre_prev FROM productosreventa ORDER BY nombre_prev")
                }
                query = queries.get(tipo_tabla)
                if query is None: self.productos = []; return
                
                result = conn.execute(query)
                self.productos = [row[0] for row in result.fetchall()]
                completer = QCompleter(self.productos)
                completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
                self.nombre_entrada.setCompleter(completer)
                self.nombre_salida.setCompleter(completer)
                self.nuevo_nombre.setCompleter(completer)
        except Exception as e:
            print(f"Error al configurar autocompletado: {e}")
            self.productos = []

    def cargar_materias_primas(self):
        if not self.engine: return
        try:
            with self.engine.connect() as conn:
                query = text("SELECT nombre_mp FROM materiasprimas ORDER BY nombre_mp")
                result = conn.execute(query)
                self.materias_primas = [row[0] for row in result.fetchall()]
                self.formula_mp_combo.clear()
                self.formula_mp_combo.addItems(self.materias_primas)
        except Exception as e:
            print(f"Error al cargar materias primas: {e}")

    def cargar_proveedores(self):
        if not self.engine: return
        try:
            with self.engine.connect() as conn:
                query = text("SELECT id_proveedor, nombre_proveedor FROM proveedor ORDER BY nombre_proveedor")
                result = conn.execute(query)
                self.proveedor_id_map.clear()
                self.proveedores.clear()
                for id_prov, nombre_prov in result.fetchall():
                    self.proveedores.append(nombre_prov)
                    self.proveedor_id_map[nombre_prov] = id_prov
        except Exception as e:
            print(f"Error al cargar proveedores: {e}")


    def anadir_materia_a_formula(self):
        materia_prima = self.formula_mp_combo.currentText()
        porcentaje_str = self.formula_porcentaje_input.text().strip()

        if not materia_prima or not porcentaje_str:
            QMessageBox.warning(self, "Campos incompletos", "Debe seleccionar una materia prima y especificar un porcentaje.")
            return

        try:
            porcentaje = float(porcentaje_str)
            if porcentaje <= 0:
                QMessageBox.warning(self, "Porcentaje inválido", "El porcentaje debe ser un número positivo.")
                return
        except ValueError:
            QMessageBox.warning(self, "Porcentaje inválido", "El porcentaje debe ser un número.")
            return

        for row in range(self.formula_table.rowCount()):
            if self.formula_table.item(row, 0).text() == materia_prima:
                QMessageBox.warning(self, "Materia prima duplicada", f"'{materia_prima}' ya está en la fórmula.")
                return

        row_position = self.formula_table.rowCount()
        self.formula_table.insertRow(row_position)
        self.formula_table.setItem(row_position, 0, QTableWidgetItem(materia_prima))
        self.formula_table.setItem(row_position, 1, QTableWidgetItem(str(porcentaje)))
        
        self.formula_porcentaje_input.clear()


    def quitar_materia_de_formula(self):
        selected_rows = self.formula_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Sin selección", "Debe seleccionar una materia prima de la tabla para quitarla.")
            return
        
        for row in sorted([r.row() for r in selected_rows], reverse=True):
            self.formula_table.removeRow(row)


    def abrir_ventana_multiple(self):
        dlg = VentanaActualizacionMultiple(self, productos=self.productos, table_type=self.obtener_tipo_tabla(), engine=self.engine)
        if dlg.exec():
            self.actualizar_tabla_callback()
            self.configurar_autocompletado()

    def autocompletar(self, destino):
        campos = {"entrada": self.nombre_entrada, "salida": self.nombre_salida, "gestion": self.nuevo_nombre}
        labels = {"entrada": self.label_info_entrada, "salida": self.label_info_salida, "gestion": self.label_info_gestion}
        campo, label, texto = campos[destino], labels[destino], campos[destino].text().strip()
        
        if not texto:
            label.setText("...")
            self.formula_table.setRowCount(0)
            return
            
        if not self.engine: return
        try:
            with self.engine.connect() as conn:
                tipo_tabla = self.obtener_tipo_tabla()
                
                resultado = None
                if tipo_tabla == "productos":
                    query = text("SELECT nombre_producto, unidad_medida_producto, area_producto, cantidad_producto, estatus_producto, id_producto FROM productos WHERE nombre_producto = :nombre")
                    resultado = conn.execute(query, {"nombre": texto}).fetchone()
                elif tipo_tabla == "materiasprimas":
                    query = text("SELECT m.nombre_mp, m.unidad_medida_mp, p.nombre_proveedor, m.cantidad_comprada_mp, m.estatus_mp, m.id_mp FROM materiasprimas m JOIN proveedor p ON m.proveedor = p.id_proveedor WHERE m.nombre_mp = :nombre")
                    resultado = conn.execute(query, {"nombre": texto}).fetchone()
                elif tipo_tabla == "productosreventa":
                    query = text("SELECT pr.nombre_prev, pr.unidad_medida_prev, p.nombre_proveedor, pr.cantidad_prev, pr.estatus_prev, pr.id_prev, pr.area_prev FROM productosreventa pr JOIN proveedor p ON pr.proveedor = p.id_proveedor WHERE pr.nombre_prev = :nombre")
                    resultado = conn.execute(query, {"nombre": texto}).fetchone()
                
                self.formula_table.setRowCount(0)

                if resultado:
                    nombre = resultado[0]
                    unidad = resultado[1]
                    extra_val = resultado[2] # Area para productos, Proveedor para los otros
                    cantidad = resultado[3]
                    estatus = resultado[4]
                    item_id = resultado[5]

                    label.setText(f"{nombre} | Stock: {cantidad or 0:.2f} {unidad}")
                    if destino == "gestion":
                        self.nuevo_nombre.setText(str(nombre))
                        self.nueva_unidad_combobox.setCurrentText(str(unidad))
                        self.radio_estatus_activo.setChecked(bool(estatus))
                        self.radio_estatus_inactivo.setChecked(not bool(estatus))

                        if tipo_tabla == "productos":
                            self.nuevo_area_combobox.setCurrentText(str(extra_val))
                            formula_query = text("SELECT m.nombre_mp, f.porcentaje FROM formulas f JOIN materiasprimas m ON f.id_mp = m.id_mp WHERE f.id_producto = :producto_id")
                            formula_resultado = conn.execute(formula_query, {"producto_id": item_id}).fetchall()
                            for row_num, row_data in enumerate(formula_resultado):
                                self.formula_table.insertRow(row_num)
                                self.formula_table.setItem(row_num, 0, QTableWidgetItem(row_data[0]))
                                self.formula_table.setItem(row_num, 1, QTableWidgetItem(str(row_data[1])))
                        elif tipo_tabla == "materiasprimas":
                             self.nuevo_proveedor_combobox.setCurrentText(str(extra_val))
                        elif tipo_tabla == "productosreventa":
                            self.nuevo_proveedor_combobox.setCurrentText(str(extra_val))
                            self.nuevo_area_combobox.setCurrentText(str(resultado[6])) # Area para reventa
                else:
                    label.setText(f"'{texto}' no encontrado.")
        except Exception as e:
            print(f"Error en autocompletar: {e}")
            label.setText("Error al buscar.")

    def registrar_entrada(self):
        self.registrar_movimiento(self.nombre_entrada.text(), self.cantidad_entrada.text(), "entrada")
    
    def registrar_salida(self):
        self.registrar_movimiento(self.nombre_salida.text(), self.cantidad_salida.text(), "salida")

    def registrar_movimiento(self, nombre, cantidad_str, tipo):
        if not nombre or not cantidad_str:
            QMessageBox.warning(self, "Campos Incompletos", "Complete todos los campos.")
            return
        try:
            cantidad = float(cantidad_str)
            if cantidad <= 0: raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Cantidad Inválida", "La cantidad debe ser un número positivo.")
            return
        if not self.engine: return
        
        try:
            with self.engine.connect() as conn:
                with conn.begin() as trans:
                    tipo_tabla = self.obtener_tipo_tabla()
                    configs = {
                        "productos": ("productos", "nombre_producto", "cantidad_producto", "estatus_producto"),
                        "materiasprimas": ("materiasprimas", "nombre_mp", "cantidad_comprada_mp", "estatus_mp"),
                        "productosreventa": ("productosreventa", "nombre_prev", "cantidad_prev", "estatus_prev")
                    }
                    if tipo_tabla not in configs: return
                    tabla, col_nombre, col_cantidad, col_estatus = configs[tipo_tabla]
                    
                    query_select = text(f"SELECT {col_cantidad}, {col_estatus} FROM {tabla} WHERE {col_nombre} = :nombre")
                    resultado = conn.execute(query_select, {"nombre": nombre}).fetchone()
                    if not resultado:
                        QMessageBox.critical(self, "Error", "Registro no encontrado.")
                        return

                    stock_actual, estatus_activo = resultado
                    if not estatus_activo:
                        QMessageBox.warning(self, "Advertencia", "No se puede registrar movimiento para un producto inactivo.")
                        return

                    nuevo_stock = (float(stock_actual) or 0) + cantidad if tipo == "entrada" else (float(stock_actual) or 0) - cantidad
                    if nuevo_stock < 0:
                        QMessageBox.critical(self, "Error", "No hay suficiente stock para la salida.")
                        return
                    
                    query_update = text(f"UPDATE {tabla} SET {col_cantidad} = :stock WHERE {col_nombre} = :nombre")
                    conn.execute(query_update, {"stock": nuevo_stock, "nombre": nombre})
                    
                    if tipo_tabla == "productos" and tipo == "entrada":
                        #self.descontar_materia_prima(conn, nombre, cantidad)
                        # Calcular costo de producción
                        costo_total = self.calcular_costo_produccion(conn, nombre, cantidad)
                        
                        # Obtener área del producto
                        query_area = text("SELECT area_producto FROM productos WHERE nombre_producto = :nombre")
                        result_area = conn.execute(query_area, {"nombre": nombre}).fetchone()
                        area = result_area[0] if result_area else "QUIMO"
                        
                        # Emitir señal de producción registrada
                        self.produccion_registrada.emit(nombre, cantidad, area, costo_total)
            
            self.actualizar_tabla_callback()
            self.configurar_autocompletado()
            QMessageBox.information(self, "Éxito", f"{tipo.title()} registrada.")
            self.limpiar_formulario(tipo)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error en la base de datos: {e}")

    def descontar_materia_prima(self, conn, nombre_producto, cantidad_producida):
        try:
            query_id = text("SELECT id_producto FROM productos WHERE nombre_producto = :nombre")
            producto_id_result = conn.execute(query_id, {"nombre": nombre_producto}).fetchone()
            if not producto_id_result: return

            producto_id = producto_id_result[0]
            
            query_formulas = text("SELECT id_mp, porcentaje FROM formulas WHERE id_producto = :id")
            ingredientes = conn.execute(query_formulas, {"id": producto_id}).fetchall()
            if not ingredientes: return

            for materia_prima_id, porcentaje in ingredientes:
                cantidad_a_descontar = (float(porcentaje) * cantidad_producida) / 100
                query_update_mp = text("UPDATE materiasprimas SET cantidad_comprada_mp = cantidad_comprada_mp - :cantidad WHERE id_mp = :id")
                conn.execute(query_update_mp, {"cantidad": cantidad_a_descontar, "id": materia_prima_id})

        except Exception as e:
            raise Exception(f"Error al deducir materias primas: {e}")

    def guardar_producto(self):
        datos = {
            "nombre": self.nuevo_nombre.text().strip(),
            "unidad": self.nueva_unidad_combobox.currentText().strip(), 
            "proveedor": self.nuevo_proveedor_combobox.currentText().strip(),
            "area": self.nuevo_area_combobox.currentText().strip(),
            "estatus": 1 if self.radio_estatus_activo.isChecked() else 0
        }
        if not datos["nombre"]:
            QMessageBox.warning(self, "Nombre vacío", "El nombre es obligatorio.")
            return

        tipo_tabla = self.obtener_tipo_tabla()
        if tipo_tabla in ["materiasprimas", "productosreventa"] and not datos["proveedor"]:
            QMessageBox.warning(self, "Proveedor Requerido", "Debe seleccionar un proveedor.")
            return
        if tipo_tabla in ["productos", "productosreventa"] and not datos["area"]:
             QMessageBox.warning(self, "Área Requerida", "Debe seleccionar un área.")
             return


        if not self.engine: return
        try:
            with self.engine.connect() as conn:
                with conn.begin() as trans:
                    if tipo_tabla == "productos":
                        self.guardar_item_generico(conn, "productos", "nombre_producto", "id_producto", datos, {
                            "unidad_medida_producto": datos["unidad"],
                            "area_producto": datos["area"],
                            "estatus_producto": datos["estatus"]
                        })
                    elif tipo_tabla == "materiasprimas":
                        id_proveedor = self.proveedor_id_map.get(datos["proveedor"])
                        self.guardar_item_generico(conn, "materiasprimas", "nombre_mp", "id_mp", datos, {
                            "unidad_medida_mp": datos["unidad"],
                            "proveedor": id_proveedor,
                            "estatus_mp": datos["estatus"]
                        })
                    elif tipo_tabla == "productosreventa":
                        id_proveedor = self.proveedor_id_map.get(datos["proveedor"])
                        self.guardar_item_generico(conn, "productosreventa", "nombre_prev", "id_prev", datos, {
                            "unidad_medida_prev": datos["unidad"],
                            "proveedor": id_proveedor,
                            "area_prev": datos["area"],
                            "estatus_prev": datos["estatus"]
                        })

            self.actualizar_tabla_callback()
            self.configurar_autocompletado()
            self.limpiar_formulario("gestion")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar:\n{e}")

    def guardar_item_generico(self, conn, tabla, col_nombre, col_id, datos, columnas_valores):
        query_existe = text(f"SELECT {col_id} FROM {tabla} WHERE {col_nombre} = :nombre")
        result_existe = conn.execute(query_existe, {"nombre": datos["nombre"]}).fetchone()
        
        mensaje = ""
        item_id = None

        if result_existe:
            item_id = result_existe[0]
            update_set = ", ".join([f"{k} = :{k}" for k in columnas_valores.keys()])
            query_update = text(f"UPDATE {tabla} SET {update_set} WHERE {col_nombre} = :nombre_original")
            
            params = columnas_valores.copy()
            params["nombre_original"] = datos["nombre"]
            conn.execute(query_update, params)
            mensaje = "Registro actualizado."
        else:
            columnas_valores[col_nombre] = datos["nombre"]
            
            # --- INICIO DE LA CORRECCIÓN ---
            # Añadir valores por defecto para los campos NOT NULL de materiasprimas
            if tabla == "materiasprimas":
                columnas_valores["cantidad_comprada_mp"] = 0.0
                columnas_valores["costo_unitario_mp"] = 0.0
                columnas_valores["tipo_moneda"] = "MXN"
                columnas_valores["total_mp"] = 0.0
            # --- FIN DE LA CORRECCIÓN ---
            elif tabla == "productos":
                 columnas_valores["cantidad_producto"] = 0.0
            elif tabla == "productosreventa":
                columnas_valores["cantidad_prev"] = 0.0

            column_names = ", ".join(columnas_valores.keys())
            placeholders = ", ".join([f":{k}" for k in columnas_valores.keys()])
            query_insert = text(f"INSERT INTO {tabla} ({column_names}) VALUES ({placeholders})")
            result = conn.execute(query_insert, columnas_valores)
            item_id = result.lastrowid
            mensaje = "Registro agregado."

        if self.obtener_tipo_tabla() == "productos" and item_id is not None:
            query_delete_formula = text("DELETE FROM formulas WHERE id_producto = :id_producto")
            conn.execute(query_delete_formula, {"id_producto": item_id})
            for row in range(self.formula_table.rowCount()):
                nombre_mp = self.formula_table.item(row, 0).text()
                porcentaje = float(self.formula_table.item(row, 1).text())
                query_id_mp = text("SELECT id_mp FROM materiasprimas WHERE nombre_mp = :nombre_mp")
                id_mp_result = conn.execute(query_id_mp, {"nombre_mp": nombre_mp}).fetchone()
                if id_mp_result:
                    id_mp = id_mp_result[0]
                    query_insert_formula = text("INSERT INTO formulas (id_producto, id_mp, porcentaje) VALUES (:id_producto, :id_mp, :porcentaje)")
                    conn.execute(query_insert_formula, {"id_producto": item_id, "id_mp": id_mp, "porcentaje": porcentaje})
        
        QMessageBox.information(self, "Éxito", mensaje)


    def dar_de_baja_producto(self):
        nombre = self.nuevo_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Nombre vacío", "Escribe el nombre del producto.")
            return

        confirm = QMessageBox.question(self, "Confirmar Baja", f"¿Estás seguro de dar de baja '{nombre}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            if not self.engine: return
            try:
                with self.engine.connect() as conn:
                    with conn.begin() as trans:
                        tipo_tabla = self.obtener_tipo_tabla()
                        configs = {
                            "productos": ("productos", "nombre_producto", "estatus_producto"),
                            "materiasprimas": ("materiasprimas", "nombre_mp", "estatus_mp"),
                            "productosreventa": ("productosreventa", "nombre_prev", "estatus_prev")
                        }
                        if tipo_tabla not in configs: return
                        tabla, col_nombre, col_estatus = configs[tipo_tabla]

                        query = text(f"UPDATE {tabla} SET {col_estatus} = 0 WHERE {col_nombre} = :nombre")
                        result = conn.execute(query, {"nombre": nombre})
                        
                        if result.rowcount > 0:
                            QMessageBox.information(self, "Éxito", f"'{nombre}' ha sido dado de baja.")
                        else:
                            QMessageBox.warning(self, "No Encontrado", f"No se encontró el producto '{nombre}'.")
                
                self.actualizar_tabla_callback()
                self.configurar_autocompletado()
                self.limpiar_formulario("gestion")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo dar de baja:\n{e}")

    def limpiar_formulario(self, tipo):
        if tipo == "entrada": self.nombre_entrada.clear(); self.cantidad_entrada.clear(); self.label_info_entrada.setText("...")
        elif tipo == "salida": self.nombre_salida.clear(); self.cantidad_salida.clear(); self.label_info_salida.setText("...")
        elif tipo == "gestion":
            self.nuevo_nombre.clear()
            self.nueva_unidad_combobox.setCurrentIndex(0)
            self.nuevo_proveedor_combobox.setCurrentIndex(0)
            self.nuevo_area_combobox.setCurrentIndex(0)
            self.radio_estatus_activo.setChecked(True)
            self.label_info_gestion.setText("...")
            self.formula_table.setRowCount(0)

    def actualizar_labels_con_tipo(self, tipo_de_tabla):
        config = self.configuracion_ui.get(tipo_de_tabla, {})
        
        self.nombre_entrada.setPlaceholderText(config.get("nombre_placeholder", "Nombre"))
        self.nombre_salida.setPlaceholderText(config.get("nombre_placeholder", "Nombre"))
        self.label_gestion_nombre.setText(config.get("nombre_label", "Nombre:"))
        self.nuevo_nombre.setPlaceholderText(config.get("nombre_placeholder", "Nombre"))
        self.nueva_unidad_combobox.setToolTip(config.get("unidad_placeholder_gestion", "Unidad..."))
        
        proveedor_label = config.get("proveedor_label")
        self.label_gestion_proveedor.setText(proveedor_label)
        self.nuevo_proveedor_combobox.clear()
        if proveedor_label:
            self.nuevo_proveedor_combobox.addItems([""] + self.proveedores)
            self.nuevo_proveedor_combobox.setToolTip(config.get("proveedor_placeholder", "Proveedor..."))
            self.label_gestion_proveedor.show()
            self.nuevo_proveedor_combobox.show()
        else:
            self.label_gestion_proveedor.hide()
            self.nuevo_proveedor_combobox.hide()

        area_label = config.get("area_label")
        self.label_gestion_area.setText(area_label)
        self.nuevo_area_combobox.clear()
        if area_label:
            self.nuevo_area_combobox.addItems(["", "QUIMO", "QUIMO CLEAN"])
            self.nuevo_area_combobox.setToolTip(config.get("area_placeholder", "Área..."))
            self.label_gestion_area.show()
            self.nuevo_area_combobox.show()
        else:
            self.label_gestion_area.hide()
            self.nuevo_area_combobox.hide()
        
        self.formula_group_box.setVisible(tipo_de_tabla == "productos")
    
    def calcular_costo_produccion(self, conn, nombre_producto, cantidad):
        """Calcula el costo de producción basado en las materias primas"""
        try:
            # Obtener ID del producto
            query_id = text("SELECT id_producto FROM productos WHERE nombre_producto = :nombre")
            producto_id_result = conn.execute(query_id, {"nombre": nombre_producto}).fetchone()
            if not producto_id_result:
                return 0.0
                
            producto_id = producto_id_result[0]
            
            # Obtener receta del producto
            query_formula = text("""
                SELECT m.id_mp, m.costo_unitario_mp, f.porcentaje 
                FROM formulas f
                JOIN materiasprimas m ON f.id_mp = m.id_mp
                WHERE f.id_producto = :producto_id
            """)
            ingredientes = conn.execute(query_formula, {"id": producto_id}).fetchall()
            
            costo_total = 0.0
            for id_mp, costo_unitario, porcentaje in ingredientes:
                cantidad_mp = (porcentaje * cantidad) / 100
                costo_total += cantidad_mp * costo_unitario
                
            return costo_total
            
        except Exception as e:
            print(f"Error calculando costo de producción: {e}")
            return 0.0