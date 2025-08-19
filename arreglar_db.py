import sqlite3
import os

DB_FILENAME = 'quimo.db'

def fix_database():
    """
    Abre la base de datos y añade las columnas 'costo' y 'area'
    a la tabla 'produccion' si no existen.
    """
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), DB_FILENAME)
    
    if not os.path.exists(db_path):
        print(f"Error: No se encontró el archivo '{DB_FILENAME}' en esta carpeta.")
        return

    print(f"Abriendo la base de datos: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Intentando añadir la columna 'costo' a la tabla 'produccion'...")
        try:
            cursor.execute("ALTER TABLE produccion ADD COLUMN costo REAL DEFAULT 0.0;")
            print(" -> Columna 'costo' añadida con éxito.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(" -> La columna 'costo' ya existía. No se hizo nada.")
            else:
                raise e

        print("Intentando añadir la columna 'area' a la tabla 'produccion'...")
        try:
            cursor.execute("ALTER TABLE produccion ADD COLUMN area TEXT;")
            print(" -> Columna 'area' añadida con éxito.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(" -> La columna 'area' ya existía. No se hizo nada.")
            else:
                raise e
                
        conn.commit()
        conn.close()
        
        print("\n¡Listo! La base de datos ha sido actualizada correctamente.")
        
    except Exception as e:
        print(f"\nOcurrió un error inesperado: {e}")

if __name__ == "__main__":
    fix_database()