import re
import os

def convert_postgres_to_sqlite(input_file_path, output_file_path):
    """
    Convierte un archivo DDL de PostgreSQL a un formato compatible con SQLite,
    manejando correctamente las claves primarias y otras restricciones.
    """
    try:
        with open(input_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo '{input_file_path}'. Asegúrate de que exista.")
        return

    # --- Pre-procesamiento: Extraer restricciones definidas con ALTER TABLE ---

    # 1. Encontrar todas las claves primarias y guardarlas
    pk_map = {}
    pk_pattern = re.compile(r"ALTER TABLE ONLY public\.(\w+)\s+ADD CONSTRAINT \w+ PRIMARY KEY \((\w+)\);", re.IGNORECASE)
    for match in pk_pattern.finditer(sql_content):
        table_name, pk_column = match.groups()
        pk_map[table_name] = pk_column
    # Eliminar estas declaraciones para que no se procesen después
    sql_content = pk_pattern.sub("", sql_content)

    # 2. Encontrar todas las claves foráneas y guardarlas
    fk_map = {}
    fk_pattern = re.compile(r"ALTER TABLE ONLY public\.(\w+)\s+ADD CONSTRAINT \w+ FOREIGN KEY \((.*?)\) REFERENCES public\.(.*?)\((.*?)\);", re.IGNORECASE)
    for match in fk_pattern.finditer(sql_content):
        table_name, column, ref_table, ref_column = match.groups()
        if table_name not in fk_map:
            fk_map[table_name] = []
        fk_map[table_name].append(f"FOREIGN KEY({column}) REFERENCES {ref_table}({ref_column})")
    sql_content = fk_pattern.sub("", sql_content)

    # --- Procesamiento principal: Convertir cada tabla ---
    
    final_statements = []
    table_pattern = re.compile(r"CREATE TABLE public\.(\w+) \((.*?)\);", re.DOTALL | re.IGNORECASE)
    
    for table_match in table_pattern.finditer(sql_content):
        table_name, table_body = table_match.groups()
        
        lines = table_body.strip().split(',\n')
        new_definitions = []

        # Procesar cada línea de la definición de la tabla
        for line in lines:
            line = line.strip()
            if not line: continue

            # Es una definición de constraint CHECK en línea
            if line.upper().startswith("CONSTRAINT"):
                check_match = re.search(r"CHECK \(\(\((.*?)\)\)\)", line)
                if check_match:
                    check_body = check_match.group(1)
                    # Convertir `col::text = ANY (ARRAY[...])` a `col IN (...)`
                    in_match = re.search(r"\((\w+)\)::text = ANY \(ARRAY\[(.*?)\]\)", check_body)
                    if in_match:
                        col, values_str = in_match.groups()
                        values = [f"'{v}'" for v in re.findall(r"\'(.*?)\'", values_str)]
                        new_definitions.append(f"CHECK({col} IN ({', '.join(values)}))")
                continue

            # Es una definición de columna
            parts = line.split()
            col_name = parts[0]

            # Reemplazar tipos de datos
            line = re.sub(r"character varying\(\d+\)|bpchar|\btext\b", "TEXT", line, flags=re.IGNORECASE)
            line = re.sub(r"numeric\(\d+,\s*\d+\)", "REAL", line, flags=re.IGNORECASE)
            line = re.sub(r"\bboolean\b", "INTEGER", line, flags=re.IGNORECASE)
            line = re.sub(r"\bdate\b", "TEXT", line, flags=re.IGNORECASE)
            
            # Manejar claves primarias de forma inteligente
            if table_name in pk_map and col_name == pk_map[table_name]:
                # Esta es la columna de clave primaria, la definimos aquí
                line = f"{col_name} INTEGER PRIMARY KEY AUTOINCREMENT"
            else:
                # No es PK, solo convertir el tipo si es integer
                line = re.sub(r"\binteger\b", "INTEGER", line, flags=re.IGNORECASE)

            # Limpiar el resto
            line = re.sub(r"GENERATED ALWAYS AS \(.*?\) STORED", "", line)
            line = re.sub(r"DEFAULT true", "DEFAULT 1", line, flags=re.IGNORECASE)
            line = re.sub(r"DEFAULT CURRENT_DATE", "DEFAULT (strftime('%Y-%m-%d', 'now'))", line, flags=re.IGNORECASE)
            line = re.sub(r"::text|::character varying", "", line) # Limpiar casting de postgres
            
            new_definitions.append(line.strip())

        # Añadir las claves foráneas que guardamos al principio
        if table_name in fk_map:
            new_definitions.extend(fk_map[table_name])

        # Construir la declaración final de la tabla
        final_table_def = ",\n    ".join(filter(None, new_definitions))
        final_statements.append(f"CREATE TABLE {table_name} (\n    {final_table_def}\n);")
        
    # Guardar el resultado
    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write("-- Script de base de datos convertido para SQLite (versión corregida)\n\n")
            f.write("\n\n".join(final_statements))
        print(f"✅ ¡Éxito! El archivo '{output_file_path}' ha sido creado/actualizado correctamente.")
    except Exception as e:
        print(f"❌ Error al escribir en el archivo de salida: {e}")

# --- Ejecución ---
if __name__ == "__main__":
    input_file = 'quimoBDSQL_texto.sql'
    output_file = 'quimo_sqlite.sql'
    convert_postgres_to_sqlite(input_file, output_file)