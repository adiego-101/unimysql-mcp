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

@mcp.tool()
def describe_table(table_name: str):
    """Obtiene la estructura de una tabla y sus relaciones. Úsala para entender el esquema antes de consultar."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Estructura de columnas
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        
        # Intentamos buscar claves foráneas para entender las relaciones (estilo Oracle)
        cursor.execute(f"""
            SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_NAME = '{table_name}' AND TABLE_SCHEMA = DATABASE() AND REFERENCED_TABLE_NAME IS NOT NULL
        """)
        relations = cursor.fetchall()
        
        return {
            "table": table_name,
            "columns": columns,
            "relations_detected": relations if relations else "No se detectaron FKs directas."
        }
    except Exception as e:
        return {"isError": True, "message": f"Hubo un problema al describir '{table_name}': {str(e)}"}
    finally:
        conn.close()

@mcp.tool()
def execute_query(sql: str, confirm: bool = False):
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
