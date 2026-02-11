#!/bin/bash
#
# 🚀 Script de Monitoreo y Deploy - ClientFlow Pro
# 
# Uso: ./scripts/deploy-monitor.sh [opciones]
# 
# Opciones:
#   --skip-push       No hacer push a GitHub
#   --skip-backend    No deployar backend a Railway
#   --skip-frontend   No deployar frontend a Vercel
#   --monitor-only    Solo monitorear estado sin deployar
#

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
PROJECT_DIR="/home/lobster/.openclaw/workspace/clientflow-pro"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
LOG_FILE="/tmp/clientflow-deploy-$(date +%Y%m%d-%H%M%S).log"

# Flags
SKIP_PUSH=false
SKIP_BACKEND=false
SKIP_FRONTEND=false
MONITOR_ONLY=false

# Parsear argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-push) SKIP_PUSH=true ;;
        --skip-backend) SKIP_BACKEND=true ;;
        --skip-frontend) SKIP_FRONTEND=true ;;
        --monitor-only) MONITOR_ONLY=true ;;
        *) echo "Opción desconocida: $1"; exit 1 ;;
    esac
    shift
done

# Funciones
log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✓${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}✗${NC} $1" | tee -a "$LOG_FILE"
}

section() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo ""
}

# Verificar dependencias
check_deps() {
    log "Verificando dependencias..."
    
    # Git
    if ! command -v git &> /dev/null; then
        error "Git no está instalado"
        exit 1
    fi
    success "Git disponible"
    
    # Railway CLI
    if [ "$SKIP_BACKEND" = false ] && [ "$MONITOR_ONLY" = false ]; then
        if ! command -v railway &> /dev/null; then
            error "Railway CLI no está instalado. Ejecuta: npm install -g @railway/cli"
            exit 1
        fi
        success "Railway CLI disponible"
    fi
    
    # Vercel CLI
    if [ "$SKIP_FRONTEND" = false ] && [ "$MONITOR_ONLY" = false ]; then
        if ! command -v vercel &> /dev/null; then
            warning "Vercel CLI no está instalado. Intentando con npx..."
            VERCEL_CMD="npx vercel"
        else
            VERCEL_CMD="vercel"
            success "Vercel CLI disponible"
        fi
    fi
}

# Verificar estado de Git
check_git() {
    section "📊 ESTADO DE GIT"
    
    cd "$PROJECT_DIR"
    
    # Verificar si hay cambios sin commit
    if [ -n "$(git status --porcelain)" ]; then
        warning "Hay cambios sin commit:"
        git status --short
        
        if [ "$MONITOR_ONLY" = false ] && [ "$SKIP_PUSH" = false ]; then
            error "Haz commit de los cambios antes de deployar"
            exit 1
        fi
    else
        success "Working tree limpio - no hay cambios pendientes"
    fi
    
    # Mostrar último commit
    log "Último commit:"
    git log -1 --oneline --decorate
    
    # Verificar si hay commits sin push
    LOCAL=$(git rev-parse @)
    REMOTE=$(git rev-parse @{u} 2>/dev/null || echo "")
    
    if [ -n "$REMOTE" ]; then
        if [ "$LOCAL" != "$REMOTE" ]; then
            warning "Hay commits locales sin push"
            git log --oneline "$REMOTE..$LOCAL"
        else
            success "Repositorio sincronizado con origin/main"
        fi
    fi
}

# Push a GitHub
git_push() {
    if [ "$SKIP_PUSH" = true ] || [ "$MONITOR_ONLY" = true ]; then
        return
    fi
    
    section "📤 PUSH A GITHUB"
    
    cd "$PROJECT_DIR"
    
    log "Haciendo push a origin/main..."
    if git push origin main; then
        success "Push completado exitosamente"
    else
        error "El push falló"
        exit 1
    fi
}

# Deploy backend a Railway
deploy_backend() {
    if [ "$SKIP_BACKEND" = true ] || [ "$MONITOR_ONLY" = true ]; then
        return
    fi
    
    section "🚂 DEPLOY BACKEND A RAILWAY"
    
    cd "$BACKEND_DIR"
    
    # Verificar si está logueado
    if ! railway whoami &> /dev/null; then
        error "No estás autenticado en Railway"
        log "Ejecuta: railway login"
        exit 1
    fi
    
    log "Iniciando deploy en Railway..."
    if railway up --yes --message "Deploy: $(git log -1 --pretty=%B)"; then
        success "Backend deployado exitosamente"
    else
        error "El deploy del backend falló"
        return 1
    fi
}

# Deploy frontend a Vercel
deploy_frontend() {
    if [ "$SKIP_FRONTEND" = true ] || [ "$MONITOR_ONLY" = true ]; then
        return
    fi
    
    section "▲ DEPLOY FRONTEND A VERCEL"
    
    cd "$FRONTEND_DIR"
    
    # Verificar si está logueado
    if ! $VERCEL_CMD whoami &> /dev/null; then
        error "No estás autenticado en Vercel"
        log "Ejecuta: $VERCEL_CMD login"
        exit 1
    fi
    
    log "Iniciando deploy en Vercel..."
    if $VERCEL_CMD --prod --yes; then
        success "Frontend deployado exitosamente"
    else
        error "El deploy del frontend falló"
        return 1
    fi
}

# Monitorear logs de Railway
monitor_railway_logs() {
    section "📜 LOGS DE RAILWAY"
    
    cd "$BACKEND_DIR"
    
    if ! railway whoami &> /dev/null; then
        warning "No estás autenticado en Railway - no se pueden obtener logs"
        return
    fi
    
    log "Obteniendo últimos logs del backend..."
    
    # Obtener logs (timeout después de 30 segundos si es interactivo)
    timeout 30 railway logs --lines 50 || true
}

# Verificar estado de salud
check_health() {
    section "🏥 VERIFICACIÓN DE SALUD"
    
    # Intentar obtener la URL del backend de Railway
    cd "$BACKEND_DIR"
    
    if railway whoami &> /dev/null; then
        log "Obteniendo información del proyecto..."
        railway status
        
        # Intentar hacer health check si tenemos la URL
        BACKEND_URL=$(railway variables get RAILWAY_PUBLIC_DOMAIN 2>/dev/null || echo "")
        
        if [ -n "$BACKEND_URL" ]; then
            log "Haciendo health check a https://$BACKEND_URL/health"
            if curl -s "https://$BACKEND_URL/health" | grep -q "healthy"; then
                success "Backend está saludable"
            else
                warning "El health check falló o no responde"
            fi
        fi
    else
        warning "No se puede verificar estado - no autenticado en Railway"
    fi
}

# Verificar variables de entorno
check_env_vars() {
    section "🔐 VARIABLES DE ENTORNO"
    
    cd "$BACKEND_DIR"
    
    if railway whoami &> /dev/null; then
        log "Variables configuradas en Railway:"
        railway variables | grep -E "^(CORS_ORIGINS|DATABASE_URL|SECRET_KEY|ENVIRONMENT)" || true
        
        # Verificar específicamente CORS_ORIGINS
        CORS=$(railway variables get CORS_ORIGINS 2>/dev/null || echo "NO_CONFIGURADO")
        if [ "$CORS" = "NO_CONFIGURADO" ]; then
            warning "CORS_ORIGINS no está configurado"
            log "Para configurar ejecuta:"
            log "  railway variables set CORS_ORIGINS=\"https://tu-frontend.vercel.app\""
        else
            success "CORS_ORIGINS configurado: $CORS"
        fi
    else
        log "Variables esperadas en Railway:"
        log "  - CORS_ORIGINS (crítico para que el frontend funcione)"
        log "  - DATABASE_URL"
        log "  - SECRET_KEY"
        log "  - ENVIRONMENT=production"
    fi
}

# Resumen final
show_summary() {
    section "📋 RESUMEN DEL DEPLOY"
    
    echo "Fecha: $(date)"
    echo "Log guardado en: $LOG_FILE"
    echo ""
    
    if [ "$MONITOR_ONLY" = true ]; then
        echo "Modo: Solo monitoreo"
    else
        [ "$SKIP_PUSH" = false ] && success "Git push: Completado" || warning "Git push: Saltado"
        [ "$SKIP_BACKEND" = false ] && success "Backend deploy: Completado" || warning "Backend deploy: Saltado"
        [ "$SKIP_FRONTEND" = false ] && success "Frontend deploy: Completado" || warning "Frontend deploy: Saltado"
    fi
    
    echo ""
    echo "Próximos pasos:"
    echo "  1. Verificar que el backend responde: curl https://<tu-backend>/health"
    echo "  2. Verificar que el frontend carga correctamente"
    echo "  3. Probar login en la aplicación"
    echo "  4. Revisar logs si hay errores: railway logs --follow"
    echo ""
    echo -e "${GREEN}✅ Proceso completado${NC}"
}

# Main
main() {
    section "🚀 CLIENTFLOW PRO - DEPLOY & MONITOR"
    
    log "Iniciando script de deploy..."
    log "Modo: $([ "$MONITOR_ONLY" = true ] && echo "Monitoreo" || echo "Deploy")"
    
    check_deps
    check_git
    
    if [ "$MONITOR_ONLY" = false ]; then
        git_push
        deploy_backend
        deploy_frontend
        
        # Esperar un poco para que el deploy se estabilice
        if [ "$SKIP_BACKEND" = false ]; then
            log "Esperando 30 segundos para que el deploy se estabilice..."
            sleep 30
        fi
    fi
    
    monitor_railway_logs
    check_health
    check_env_vars
    show_summary
}

# Ejecutar
main "$@"
