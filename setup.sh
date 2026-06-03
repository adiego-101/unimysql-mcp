#!/bin/bash

# --- Colores para un toque humano ---
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE} Bienvenido al instalador de UniMySQL-MCP${NC}"
echo -e "Preparando tu tutor personal de bases de datos...\n"

# 1. Verificar Python
if ! command -v python3 &> /dev/null
then
  echo -e "${YELLOW} No encontré python3. Por favor instálalo para continuar.${NC}"
  exit 1
fi

# 2. Instalar dependencias
echo -e " Instalando dependencias necesarias..."
pip install mcp mysql-connector-python python-dotenv --quiet
echo -e "${GREEN} Dependencias listas.${NC}"

# 3. Configurar .env si no existe
if [ ! -f .env ]; then
  echo -e "\n Vamos a configurar tu conexión local rápidamente."
  read -p "MySQL Host (default: localhost): " db_host
  db_host=${db_host:-localhost}
  read -p "MySQL User (default: root): " db_user
  db_user=${db_user:-root}
  read -sp "MySQL Password: " db_pass
  echo ""
  read -p "MySQL Database (default: universidad): " db_name
  db_name=${db_name:-universidad}

  echo "MYSQL_HOST=$db_host" > .env
  echo "MYSQL_USER=$db_user" >> .env
  echo "MYSQL_PASSWORD=$db_pass" >> .env
  echo "MYSQL_DATABASE=$db_name" >> .env
  echo -e "${GREEN} Archivo .env creado.${NC}"
fi

# 4. Mostrar configuración para agentes
echo -e "\n${BLUE} ¡Todo listo! Ahora configura tu agente favorito:${NC}"
echo -e "\n${YELLOW}Para Claude Desktop (claude_desktop_config.json):${NC}"
echo -e "{"
echo -e " \"mcpServers\": {"
echo -e "  \"unimysql\": {"
echo -e "   \"command\": \"python3\","
echo -e "   \"args\": [\"$(pwd)/server.py\"]"
echo -e "  }"
echo -e " }"
echo -e "}"

echo -e "\n${YELLOW}Para Cursor:${NC}"
echo -e "Añade un nuevo servidor MCP con la ruta: $(pwd)/server.py"

echo -e "\n${GREEN}¡Disfruta aprendiendo SQL con tu nuevo tutor! ${NC}"
