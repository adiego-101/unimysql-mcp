# 🎓 UniMySQL-MCP (Tutor Edition)

¡Bienvenido al servidor MCP diseñado para democratizar el aprendizaje de bases de datos! 🚀

Este no es el típico conector de bases de datos. **UniMySQL-MCP** es un tutor interactivo que vive en tu chat y te ayuda a dominar MySQL sin romper nada en el intento.

## ✨ Características que nos hacen diferentes
- **Capa de Supervisión Interactiva:** Si intentas borrar o actualizar datos, el tutor te detendrá, te explicará las consecuencias y te pedirá permiso. ¡Se acabaron los `DELETE` accidentales sin `WHERE`!
- **Mapeo Inteligente de Relaciones:** Al estilo de Oracle, detectamos automáticamente cómo se conectan tus tablas para que tus `JOIN` tengan sentido desde el primer momento.
- **Paginación Preventiva:** Protegemos tu chat limitando automáticamente los resultados de grandes consultas.
- **Tono Humano:** Commits reales, comentarios honestos y una IA que te trata como a un colega estudiante.

## 🛠️ Instalación Rápida (Para universitarios con prisa)

1. **Instala las dependencias:**
   Necesitas Python 3.10+ y, opcionalmente, `uv` para una velocidad de vértigo.
   ```bash
   pip install mcp mysql-connector-python python-dotenv
   ```

2. **Configura tu acceso:**
   Copia el archivo `.env.example` a `.env` y pon tus credenciales de localhost.

3. **Conéctalo a tu cliente (Cursor, Claude Desktop, Gemini CLI):**
   Añade esto a tu configuración de MCP:
   ```json
   "unimysql": {
     "command": "python",
     "args": ["/tu/ruta/al/unimysql-mcp/server.py"]
   }
   ```

## 🔐 Guía de Seguridad: El Usuario Tutor
No uses `root`. Sé un buen ingeniero y crea un usuario con los permisos justos. Ejecuta esto en tu MySQL:

```sql
-- Creamos al tutor
CREATE USER 'mcp_tutor'@'localhost' IDENTIFIED BY 'tu_password_seguro';

-- Le damos permiso para lo necesario en tu base de datos
GRANT SELECT, INSERT, UPDATE, DELETE ON universidad.* TO 'mcp_tutor'@'localhost';

FLUSH PRIVILEGES;
```

---
*Hecho con ❤️ para la comunidad abierta de OpenAI. Si este proyecto te sirve para aprobar bases de datos, ¡mándame una estrella en GitHub!* ⭐
