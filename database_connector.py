import psycopg2
import configparser
from PyQt6.QtWidgets import QMessageBox

def get_db_connection():
    
    """
    Esto establece y tambien devuelve una conexión a la base de datos PostgreSQL,
    Lee la configuración desde config.ini,
    Muestra un error si la conexión falla.
    """
    config = configparser.ConfigParser()
    try:
        config.read('config.ini')
        db_config = config['database']
        
        conn = psycopg2.connect(
            dbname=db_config['dbname'],
            user=db_config['user'],
            password=db_config['password'],
            host=db_config['host'],
            port=db_config['port'],
            connect_timeout=5
        )
        return conn
    except FileNotFoundError:
        error_msg = "Error: No se encontró el archivo 'config.ini'."
        print(error_msg)
        QMessageBox.critical(None, "Error de Configuración", error_msg)
        return None
    except KeyError:
        error_msg = "Error: El archivo 'config.ini' no tiene la sección [database] o le faltan claves."
        print(error_msg)
        QMessageBox.critical(None, "Error de Configuración", error_msg)
        return None
    except Exception as e:
        error_msg = f"No se pudo conectar a la base de datos:\n{e}"
        print(error_msg)
        QMessageBox.critical(None, "Error de Conexión", error_msg)
        return None
