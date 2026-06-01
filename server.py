import os
import re
import sys
from typing import Optional
import mysql.connector
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Cargamos las variables de entorno para no dejar nada hardcodeado (¡Seguridad ante todo!)
load_dotenv()

# Inicializamos el servidor FastMCP con un nombre amigable
mcp = FastMCP("UniMySQL-Tutor")

def get_db_connection():
    """Establece la conexión con la base de datos local."""
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "test")
    )

def is_destructive_query(sql: str) -> bool:
    """Detecta si la consulta es un UPDATE o DELETE para activar la supervisión."""
    sql_upper = sql.upper().strip()
    return sql_upper.startswith("UPDATE") or sql_upper.startswith("DELETE")

@mcp.tool()
def list_tables():
    """Lista todas las tablas de la base de datos actual para que el LLM sepa qué hay disponible."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        return {"tables": tables}
    except Exception as e:
        return {"isError": True, "message": f"Vaya, no pude listar las tablas: {str(e)}"}
    finally:
        conn.close()

def is_safe_name(name: str) -> bool:
    """Valida que los nombres de tablas o columnas solo contengan caracteres alfanuméricos y guiones bajos."""
    return re.match(r'^[a-zA-Z0-9_]+$', name) is not None

@mcp.tool()
def describe_table(table_name: str):
    """Obtiene la estructura de una tabla y sus relaciones. Úsala para entender el esquema antes de consultar."""
    if not is_safe_name(table_name):
        return {"isError": True, "message": "Nombre de tabla inválido o sospechoso."}
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Estructura de columnas (Usamos parámetros para seguridad)
        cursor.execute(f"DESCRIBE `{table_name}`")
        columns = cursor.fetchall()
        
        # Relaciones de Claves Foráneas
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
        return {"isError": True, "message": f"Error al describir tabla: {str(e)}"}
    finally:
        conn.close()

@mcp.tool()
def explain_query(sql: str):
    """
    Analiza el plan de ejecución de una consulta (EXPLAIN). 
    Úsala para diagnosticar por qué una consulta es lenta o qué índices está usando MySQL.
    """
    if not sql.upper().strip().startswith("SELECT"):
        return {"isError": True, "message": "Solo se pueden analizar planes de ejecución para consultas SELECT."}

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(f"EXPLAIN {sql}")
        plan = cursor.fetchall()
        return {
            "explanation": plan,
            "advice": "Mira la columna 'type': 'ALL' significa que estás escaneando toda la tabla (lento). Busca 'index' o 'ref'."
        }
    except Exception as e:
        return {"isError": True, "message": f"No se pudo analizar el plan: {str(e)}"}
    finally:
        conn.close()

@mcp.tool()
def execute_query(sql: str, confirm: bool = False):
    # ... (Mantenemos la lógica de confirmación anterior)
    """
    Ejecuta una consulta SQL. 
    IMPORTANTE: Si la consulta es UPDATE o DELETE, esta herramienta fallará a menos que confirm=True.
    Esto es para que la IA primero explique el cambio al usuario y obtenga su permiso.
    """
    if is_destructive_query(sql) and not confirm:
        return {
            "isError": True, 
            "requires_confirmation": True,
            "message": (
                "🚨 DETENIDO: Has intentado una operación de escritura (UPDATE/DELETE). "
                "Como tutor, DEBES explicarle al usuario qué filas se verán afectadas y por qué. "
                "Solo después de que el usuario diga 'sí', vuelve a llamar a esta función pasando confirm=True."
            )
        }

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Añadimos un LIMIT 50 automático a los SELECT si el usuario no puso uno
        if sql.upper().strip().startswith("SELECT") and "LIMIT" not in sql.upper():
            sql = sql.rstrip(";") + " LIMIT 50"
            sys.stderr.write("INFO: Aplicando LIMIT 50 preventivo.\n")

        cursor.execute(sql)
        
        if sql.upper().strip().startswith("SELECT"):
            results = cursor.fetchall()
            return {"results": results, "count": len(results)}
        else:
            conn.commit()
            return {"status": "success", "affected_rows": cursor.rowcount, "message": "¡Cambio aplicado con éxito!"}
            
    except Exception as e:
        return {"isError": True, "message": f"La base de datos se quejó: {str(e)}"}
    finally:
        conn.close()

if __name__ == "__main__":
    # Arrancamos el servidor en modo STDIO
    mcp.run()
