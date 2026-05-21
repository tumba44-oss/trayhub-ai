#!/bin/bash
# Script de deploy no Render.com
# Execute este script no terminal do Render

echo "🚀 Deploy TrayHub AI no Render"
echo ""
echo "1. Acesse: https://dashboard.render.com"
echo "2. Clique em 'New +' -> 'Web Service'"
echo "3. Conecte sua conta GitHub"
echo "4. Selecione o repositório: tumba44-oss/trayhub-ai"
echo "5. Configure:"
echo "   - Name: trayhub-ai"
echo "   - Runtime: Python 3"
echo "   - Build Command: pip install -r requirements.txt"
echo "   - Start Command: python3 server.py"
echo "6. Clique em 'Create Web Service'"
echo ""
echo "Ou use a CLI do Render:"
echo "   render deploy --repo tumba44-oss/trayhub-ai"
