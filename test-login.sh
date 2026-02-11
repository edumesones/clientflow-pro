#!/bin/bash
# Diagnóstico final del login

echo "=== DIAGNÓSTICO LOGIN ==="
echo ""

echo "1. Test /init:"
curl -s https://clientflow-pro-production.up.railway.app/init
echo ""
echo ""

echo "2. Test login:"
curl -s -X POST https://clientflow-pro-production.up.railway.app/api/auth/login-json \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@clientflow.pro","password":"demo123"}'
echo ""
echo ""

echo "3. Test health:"
curl -s https://clientflow-pro-production.up.railway.app/health
echo ""
