import sqlite3
import os

DB_FILENAME = 'quimo.db'

def rebuild_production_table():
    """
    Recrea la tabla 'produccion' con una restricción UNIQUE en (fecha, producto_id)
    para permitir el uso de ON CONFLICT.
    """
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), DB_FILENAME)
    
    if not os.path.exists(db_path):
        print(f"Error: No se encontró el archivo '{DB_FILENAME}'.")
        return

    print(f"Conectando a la base de datos: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("Iniciando la reconstrucción de la tabla 'produccion'...")
        
        # Iniciar una transacción
        cursor.execute("BEGIN TRANSACTION;")

        # 1. Crear una nueva tabla con la estructura correcta
        print(" -> Paso 1: Creando tabla temporal con la estructura correcta...")
        cursor.execute("""
        CREATE TABLE produccion_nueva (
            id_produccion INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            producto_id INTEGER NOT NULL,
            dia TEXT NOT NULL,
            cantidad REAL NOT NULL,
            costo REAL DEFAULT 0.0,
            area TEXT,
            FOREIGN KEY (producto_id) REFERENCES productos (id_producto),
            UNIQUE (fecha, producto_id)
        );
        """)

        # 2. Copiar los datos de la tabla vieja a la nueva
        print(" -> Paso 2: Copiando datos existentes a la nueva tabla...")
        cursor.execute("""
        INSERT INTO produccion_nueva (id_produccion, fecha, producto_id, dia, cantidad, costo, area)
        SELECT id_produccion, fecha, producto_id, dia, cantidad, costo, area
        FROM produccion;
        """)

        # 3. Eliminar la tabla original
        print(" -> Paso 3: Eliminando la tabla antigua...")
        cursor.execute("DROP TABLE produccion;")

        # 4. Renombrar la nueva tabla a la original
        print(" -> Paso 4: Renombrando la tabla nueva...")
        cursor.execute("ALTER TABLE produccion_nueva RENAME TO produccion;")

        # Confirmar la transacción
        conn.commit()
        print("\n¡Éxito! La tabla 'produccion' ha sido reconstruida y ahora es compatible con ON CONFLICT.")

    except Exception as e:
        # Si algo sale mal, revertir todo
        conn.rollback()
        print(f"\n¡Error! No se pudo completar la operación. Se revirtieron todos los cambios. Error: {e}")
    finally:
        conn.close()
        print("Conexión a la base de datos cerrada.")


if __name__ == "__main__":
    rebuild_production_table()