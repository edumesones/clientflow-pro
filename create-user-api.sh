#!/bin/bash
# Crear usuario demo directamente

RAILWAY_TOKEN="476ef6c9-fad8-44ae-b256-5f2c400ea909"

echo "Creando usuario demo..."

# Usar Railway API para ejecutar comando
curl -s -X POST "https://backboard.railway.app/graphql" \
  -H "Authorization: Bearer $RAILWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { executeSql(projectId: \"\" sql: \"INSERT INTO users (email, hashed_password, full_name, role, is_active) VALUES ('\"'"'"'demo@clientflow.pro'"'"'"', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAYMyzJ/I1K', 'Dr. Ana Garcia', 'professional', true) ON CONFLICT (email) DO NOTHING;\") { result } }"
  }'

echo ""
echo "Verificando..."
curl -s -X POST https://clientflow-pro-production.up.railway.app/api/auth/login-json \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@clientflow.pro","password":"demo123"}'
