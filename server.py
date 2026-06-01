import os
import re
import sys
import csv
import json
from typing import Optional
import mysql.connector
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Cargamos las variables de entorno
load_dotenv()

# Inicializamos el servidor FastMCP
mcp = FastMCP("UniMySQL-Tutor")

# Directorio de exportaciones
EXPORTS_DIR = os.path.join(os.getcwd(), "exports")
if not os.path.exists(EXPORTS_DIR):
    os.makedirs(EXPORTS_DIR)

def get_db_connection():
    """Establece la conexión con la base de datos local."""
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "test")
    )

def is_safe_name(name: str) -> bool:
    """Valida que los nombres solo contengan caracteres alfanuméricos y guiones bajos."""
    return re.match(r'^[a-zA-Z0-9_]+$', name) is not None

def is_destructive_query(sql: str) -> bool:
    """Detecta si la consulta es un UPDATE o DELETE."""
    sql_upper = sql.upper().strip()
    return sql_upper.startswith("UPDATE") or sql_upper.startswith("DELETE")

@mcp.tool()
def list_tables():
    """Lista todas las tablas de la base de datos."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        return {"tables": tables}
    except Exception as e:
        return {"isError": True, "message": f"Error: {str(e)}"}
    finally:
        conn.close()

@mcp.tool()
def describe_table(table_name: str):
    """Obtiene la estructura y relaciones de una tabla."""
    if not is_safe_name(table_name):
        return {"isError": True, "message": "Nombre de tabla inválido."}
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(f"DESCRIBE `{table_name}`")
        columns = cursor.fetchall()
        
        cursor.execute("""
            SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_NAME = %s AND TABLE_SCHEMA = DATABASE() AND REFERENCED_TABLE_NAME IS NOT NULL
        """, (table_name,))
        relations = cursor.fetchall()
        
        return {
            "table": table_name,
            "columns": columns,
            "relations": relations if relations else "Sin relaciones detectadas."
        }
    except Exception as e:
        return {"isError": True, "message": f"Error: {str(e)}"}
    finally:
        conn.close()

@mcp.tool()
def explain_query(sql: str):
    """Analiza el plan de ejecución de una consulta SELECT."""
    if not sql.upper().strip().startswith("SELECT"):
        return {"isError": True, "message": "Solo SELECT puede ser analizado con EXPLAIN."}

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(f"EXPLAIN {sql}")
        plan = cursor.fetchall()
        return {
            "explanation": plan,
            "advice": "Busca 'ALL' en la columna 'type'; indica que falta un índice."
        }
    except Exception as e:
        return {"isError": True, "message": f"Error: {str(e)}"}
    finally:
        conn.close()

@mcp.tool()
def export_data(sql: str, filename: str, format: str = "csv"):
    """
    Exporta resultados masivos a un archivo local (CSV o JSON).
    Evita saturar el chat con miles de filas.
    """
    if not sql.upper().strip().startswith("SELECT"):
        return {"isError": True, "message": "Solo se pueden exportar consultas SELECT."}

    # Sanitizar nombre de archivo
    safe_filename = re.sub(r'[^a-zA-Z0-9_-]', '_', filename) + f".{format}"
    target_path = os.path.join(EXPORTS_DIR, safe_filename)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()

        if format == "csv":
            if rows:
                with open(target_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                    writer.writeheader()
                    writer.writerows(rows)
        else:
            with open(target_path, 'w', encoding='utf-8') as f:
                json.dump(rows, f, indent=2, default=str)

        return {
            "status": "success",
            "message": f"✅ Exportación exitosa",
            "file": safe_filename,
            "path": target_path,
            "rows_count": len(rows),
            "format": format.upper()
        }
    except Exception as e:
        return {"isError": True, "message": f"Error en exportación: {str(e)}"}
    finally:
        conn.close()

@mcp.tool()
def execute_query(sql: str, confirm: bool = False):
    """Ejecuta SQL con supervisión interactiva para UPDATE/DELETE."""
    if is_destructive_query(sql) and not confirm:
        return {
            "isError": True, 
            "requires_confirmation": True,
            "message": "🚨 DETENIDO: Operación destructiva. Explica el riesgo al usuario y pide confirmación (confirm=True)."
        }

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if sql.upper().strip().startswith("SELECT") and "LIMIT" not in sql.upper():
            sql = sql.rstrip(";") + " LIMIT 50"
            sys.stderr.write("INFO: Aplicando LIMIT 50 preventivo.\n")

        cursor.execute(sql)
        
        if sql.upper().strip().startswith("SELECT"):
            results = cursor.fetchall()
            return {"results": results, "count": len(results)}
        else:
            conn.commit()
            return {"status": "success", "affected_rows": cursor.rowcount, "message": "Cambio aplicado."}
            
    except Exception as e:
        return {"isError": True, "message": f"Error: {str(e)}"}
    finally:
        conn.close()

if __name__ == "__main__":
    mcp.run()
