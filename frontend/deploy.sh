#!/bin/bash

# Script de despliegue para ClientFlow Pro Frontend
# Uso: ./deploy-frontend.sh

echo "🚀 ClientFlow Pro - Frontend Deployment Script"
echo "================================================"
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar que estamos en el directorio correcto
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ Error: No se encontró package.json${NC}"
    echo "Ejecuta este script desde el directorio frontend/"
    exit 1
fi

echo -e "${GREEN}✓${NC} Directorio frontend verificado"

# Verificar vercel.json
if [ ! -f "vercel.json" ]; then
    echo -e "${RED}❌ Error: No se encontró vercel.json${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} vercel.json encontrado"

# Verificar Vercel CLI
echo ""
echo "🔍 Verificando Vercel CLI..."
if ! command -v vercel &> /dev/null; then
    if ! command -v npx &> /dev/null; then
        echo -e "${RED}❌ Error: npx no está instalado${NC}"
        exit 1
    fi
    VERCEL_CMD="npx vercel"
else
    VERCEL_CMD="vercel"
fi

echo -e "${GREEN}✓${NC} Vercel CLI disponible: $VERCEL_CMD"

# Verificar login
echo ""
echo "🔍 Verificando autenticación..."
if ! $VERCEL_CMD whoami &> /dev/null; then
    echo -e "${YELLOW}⚠️  No estás autenticado en Vercel${NC}"
    echo ""
    echo "Por favor, ejecuta primero:"
    echo -e "${YELLOW}  $VERCEL_CMD login${NC}"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓${NC} Autenticación verificada"

# Preguntar por las variables de entorno
echo ""
echo "📋 Configuración de Variables de Entorno"
echo "-----------------------------------------"
echo "Estas variables deben configurarse en el dashboard de Vercel"
echo "después del primer despliegue."
echo ""

read -p "¿Has configurado ya el backend? (s/n): " backend_ready

if [ "$backend_ready" = "s" ] || [ "$backend_ready" = "S" ]; then
    read -p "URL del backend API (ej: https://api.tudominio.com): " api_url
    read -p "URL del WebSocket (ej: wss://api.tudominio.com): " ws_url
    
    echo ""
    echo "📝 Para configurar las variables, ejecuta:"
    echo -e "${YELLOW}  $VERCEL_CMD env add REACT_APP_API_URL${NC}"
    echo -e "  Valor: ${GREEN}$api_url${NC}"
    echo ""
    echo -e "${YELLOW}  $VERCEL_CMD env add REACT_APP_WS_URL${NC}"
    echo -e "  Valor: ${GREEN}$ws_url${NC}"
    echo ""
fi

# Preguntar tipo de despliegue
echo ""
echo "🚀 Opciones de Despliegue"
echo "-------------------------"
echo "1) Preview (despliegue de prueba)"
echo "2) Production (despliegue a producción)"
echo ""
read -p "Selecciona una opción (1/2): " deploy_option

# Ejecutar despliegue
echo ""
echo "🚀 Iniciando despliegue..."
echo ""

case $deploy_option in
    1)
        $VERCEL_CMD
        ;;
    2)
        $VERCEL_CMD --prod
        ;;
    *)
        echo -e "${YELLOW}⚠️  Opción no válida. Desplegando a preview...${NC}"
        $VERCEL_CMD
        ;;
esac

# Resultado
echo ""
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Despliegue completado${NC}"
    echo ""
    echo "📋 Siguientes pasos:"
    echo "   1. Ve a https://vercel.com/dashboard"
    echo "   2. Selecciona tu proyecto"
    echo "   3. Ve a Settings → Environment Variables"
    echo "   4. Configura REACT_APP_API_URL y REACT_APP_WS_URL"
    echo "   5. Re-deploy si es necesario"
else
    echo -e "${RED}❌ El despliegue falló${NC}"
    echo "Revisa los errores arriba y vuelve a intentarlo."
fi
