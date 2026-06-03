# MySQL-MCP-Guard (Tutor Edition)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Protocol](https://img.shields.io/badge/Protocol-MCP-orange.svg)](https://modelcontextprotocol.io)

> **MySQL-MCP-Guard** no es solo un conector de base de datos; es el tutor que desearías haber tenido en primer año de facultad. Transforma tu IA en un experto en SQL que te guía, te protege y te enseña.

---

## ¿Qué hace a UniMySQL único?

A diferencia de otros servidores MCP que son "cajas negras" o riesgos de seguridad, UniMySQL está construido bajo la filosofía de **Aprendizaje Supervisado**:

### 1. Capa de Supervisión Interactiva
Si intentas realizar un `DELETE` o `UPDATE`, el servidor intercepta la petición. El Tutor explica las consecuencias y solo ejecuta el comando si confirmas explícitamente. ¡Adiós a los errores catastróficos!

### 2. Planificador Educativo (Explain-First)
Incorporamos herramientas de auditoría que analizan cómo MySQL ejecuta tus consultas. La IA puede detectar si te falta un índice o si tu consulta es ineficiente antes de que se convierta en un problema.

### 3. Mapeo de Relaciones (Oracle Style)
Detectamos automáticamente las Claves Foráneas (FK) y las presentamos de forma clara para que el LLM entienda tu esquema sin alucinaciones.

### 4. Exportación Masiva (CSV/JSON)
¿Necesitas sacar miles de filas? Nuestra herramienta de exportación guarda los datos directamente en una carpeta local (`exports/`), evitando saturar el chat y ahorrando tokens.

### 5. Recursos de Esquema Nativos
Exponemos el esquema completo de tu base de datos como un Recurso MCP (`mysql://localhost/schema`), permitiendo que la IA entienda tus tablas al instante sin ejecutar herramientas.

### 6. Prompts Interactivos
Usa plantillas de enseñanza integradas como `leccion-sql` y `auditoria-esquema` para guiar tu aprendizaje.

---

## Cómo funciona (Arquitectura)

```mermaid
graph TD
  User((Estudiante)) -->|Pregunta Natural| LLM["Model Context Protocol Client"]
  LLM -->|JSON-RPC| MCP["MySQL-MCP-Guard Server"]
  
  subgraph "Seguridad & Tutoría"
    MCP --> Guard{¿Es Destructivo?}
    Guard -->|Sí| Warn["Pedir Confirmación"]
    Guard -->|No| Safe["Ejecutar SQL"]
  end
  
  Safe --> MySQL[("MySQL Localhost")]
  MySQL --> Results["Resultados Paginados"]
  Results -->|Feedback Educativo| LLM
```

---

## 🚀 Instalación Rápida

### Opción A: Uso Instantáneo (Recomendado)
No necesitas clonar nada. Si tienes Node.js instalado, puedes usar la versión global directamente:

```json
"unimysql": {
  "command": "npx",
  "args": ["-y", "mysql-mcp-guard"],
  "env": {
    "MYSQL_HOST": "localhost",
    "MYSQL_USER": "tu_usuario",
    "MYSQL_PASSWORD": "tu_password",
    "MYSQL_DATABASE": "tu_base_de_datos"
  }
}
```

### Opción B: Versión Python (Local)
1. **Clona el repo:** `git clone https://github.com/adiego-101/unimysql-mcp.git`
2. **Instala dependencias:** `pip install mcp mysql-connector-python python-dotenv`
3. **Configura tu `.env`:** Copia `.env.example` a `.env` y ajusta tus credenciales.

---

## 📊 Especificaciones Técnicas

### Variables de Entorno
| Variable | Descripción | Default |
| :--- | :--- | :--- |
| `MYSQL_HOST` | Host de la base de datos (Usa `host.docker.internal` si MySQL corre en Docker) | `localhost` |
| `MYSQL_USER` | Usuario | `root` |
| `MYSQL_PASSWORD`| Contraseña | (vacío) |
| `MYSQL_DATABASE`| Nombre de la BD | `test` |

### Herramientas Disponibles
- `list_tables`: Lista todas las tablas.
- `describe_table`: Estructura detallada y relaciones.
- `execute_query`: Ejecución SQL con confirmación de seguridad para borrados/actualizaciones.
- `explain_query`: Análisis de rendimiento y consejos de indexación.
- `export_data`: Exportación masiva a archivos CSV/JSON.

### Recursos y Prompts MCP
- **Recurso:** `mysql://localhost/schema` - Acceso instantáneo al esquema para la IA.
- **Prompt:** `leccion-sql` - Tutoriales personalizados usando tus datos reales.
- **Prompt:** `auditoria-esquema` - Análisis experto del diseño de tu base de datos.


---

## Configuración en Agentes

### Claude Desktop
Añade esto a tu `claude_desktop_config.json`:
```json
"unimysql": {
 "command": "python",
 "args": ["/ruta/absoluta/a/unimysql_mcp/server.py"]
}
```

### Cursor / Gemini CLI
Solo apunta el servidor MCP a la ruta del archivo `server.py`.

---

## El "Usuario Tutor" (Buenas Prácticas)
No uses `root`. Sigue nuestra guía para crear un usuario con los permisos exactos:

```sql
CREATE USER 'mcp_tutor'@'localhost' IDENTIFIED BY 'tu_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON universidad.* TO 'mcp_tutor'@'localhost';
FLUSH PRIVILEGES;
```

---

## Contribuir
Este es un proyecto **Open Source** para estudiantes. Si tienes una idea para una nueva herramienta educativa, ¡abre un PR! 

*Hecho con  para la comunidad de OpenAI y estudiantes de todo el mundo.* 
nidad de OpenAI y estudiantes de todo el mundo.* 
