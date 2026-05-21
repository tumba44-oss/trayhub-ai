#!/usr/bin/env python3
"""
TrayHub AI - Servidor Backend
Dashboard com Agente IA Autônomo para E-commerce Tray
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import urllib.parse
import urllib.request
import time
from datetime import datetime, timedelta

# Configurações
PORT = int(os.environ.get('PORT', 3002))
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Arquivos de dados
LOJAS_FILE = os.path.join(DATA_DIR, 'lojas.json')
PEDIDOS_FILE = os.path.join(DATA_DIR, 'pedidos.json')
PRODUTOS_FILE = os.path.join(DATA_DIR, 'produtos.json')
CLIENTES_FILE = os.path.join(DATA_DIR, 'clientes.json')
CONFIG_FILE = os.path.join(DATA_DIR, 'config.json')
ATIVIDADES_FILE = os.path.join(DATA_DIR, 'atividades.json')
CHAT_FILE = os.path.join(DATA_DIR, 'chat.json')

# Dados demo para simulação (quando não há conexão Tray)
DEMO_LOJA = {
    "id": "demo",
    "nome": "Loja Demo",
    "subdominio": "demo",
    "status": "connected",
    "conectado_em": datetime.now().isoformat(),
    "consumer_key": "demo_key",
    "consumer_secret": "demo_secret",
    "access_token": "demo_token",
    "demo_mode": True
}

DEMO_PEDIDOS = [
    {
        "id": "1001",
        "status": "approved",
        "total": 299.90,
        "subtotal": 279.90,
        "shipping": 20.00,
        "discount": 0,
        "created_at": (datetime.now() - timedelta(hours=2)).isoformat(),
        "customer": {"id": "1", "name": "João Silva", "email": "joao@email.com", "phone": "(11) 98765-4321"},
        "items": [{"product_id": "1", "name": "Tênis Nike Air Max", "quantity": 1, "price": 279.90}],
        "shipping_address": {"street": "Rua das Flores", "number": "123", "city": "São Paulo", "state": "SP"},
        "payment": {"method": "credit_card", "installments": 3}
    },
    {
        "id": "1002",
        "status": "pending",
        "total": 159.90,
        "subtotal": 149.90,
        "shipping": 10.00,
        "discount": 0,
        "created_at": (datetime.now() - timedelta(hours=5)).isoformat(),
        "customer": {"id": "2", "name": "Maria Santos", "email": "maria@email.com", "phone": "(11) 91234-5678"},
        "items": [{"product_id": "2", "name": "Mochila Adidas", "quantity": 1, "price": 149.90}],
        "shipping_address": {"street": "Av. Paulista", "number": "1000", "city": "São Paulo", "state": "SP"},
        "payment": {"method": "boleto", "installments": 1}
    },
    {
        "id": "1003",
        "status": "shipped",
        "total": 499.90,
        "subtotal": 459.90,
        "shipping": 40.00,
        "discount": 0,
        "created_at": (datetime.now() - timedelta(days=1)).isoformat(),
        "customer": {"id": "3", "name": "Pedro Costa", "email": "pedro@email.com", "phone": "(11) 95555-9999"},
        "items": [{"product_id": "3", "name": "Fone Bluetooth JBL", "quantity": 1, "price": 459.90}],
        "shipping_address": {"street": "Rua Augusta", "number": "500", "city": "São Paulo", "state": "SP"},
        "payment": {"method": "credit_card", "installments": 6}
    },
    {
        "id": "1004",
        "status": "delivered",
        "total": 89.90,
        "subtotal": 79.90,
        "shipping": 10.00,
        "discount": 0,
        "created_at": (datetime.now() - timedelta(days=2)).isoformat(),
        "customer": {"id": "4", "name": "Ana Oliveira", "email": "ana@email.com", "phone": "(11) 98888-7777"},
        "items": [{"product_id": "4", "name": "Camiseta Nike", "quantity": 2, "price": 39.95}],
        "shipping_address": {"street": "Rua Oscar Freire", "number": "200", "city": "São Paulo", "state": "SP"},
        "payment": {"method": "pix", "installments": 1}
    },
    {
        "id": "1005",
        "status": "canceled",
        "total": 1299.90,
        "subtotal": 1259.90,
        "shipping": 40.00,
        "discount": 0,
        "created_at": (datetime.now() - timedelta(days=3)).isoformat(),
        "customer": {"id": "5", "name": "Carlos Lima", "email": "carlos@email.com", "phone": "(11) 92222-3333"},
        "items": [{"product_id": "5", "name": "Smartwatch Samsung", "quantity": 1, "price": 1259.90}],
        "shipping_address": {"street": "Av. Brigadeiro", "number": "300", "city": "São Paulo", "state": "SP"},
        "payment": {"method": "credit_card", "installments": 12}
    }
]

DEMO_PRODUTOS = [
    {"id": "1", "name": "Tênis Nike Air Max", "price": 299.90, "promotional_price": 279.90, "stock": 15, "category": "Calçados", "sales": 45, "image": "👟"},
    {"id": "2", "name": "Mochila Adidas", "price": 189.90, "promotional_price": 149.90, "stock": 8, "category": "Acessórios", "sales": 32, "image": "🎒"},
    {"id": "3", "name": "Fone Bluetooth JBL", "price": 499.90, "promotional_price": 459.90, "stock": 3, "category": "Eletrônicos", "sales": 28, "image": "🎧"},
    {"id": "4", "name": "Camiseta Nike", "price": 99.90, "promotional_price": 79.90, "stock": 50, "category": "Roupas", "sales": 120, "image": "👕"},
    {"id": "5", "name": "Smartwatch Samsung", "price": 1499.90, "promotional_price": 1259.90, "stock": 5, "category": "Eletrônicos", "sales": 15, "image": "⌚"},
    {"id": "6", "name": "Calça Jeans Levi's", "price": 249.90, "promotional_price": 199.90, "stock": 12, "category": "Roupas", "sales": 38, "image": "👖"},
    {"id": "7", "name": "Tênis Adidas Ultraboost", "price": 599.90, "promotional_price": 499.90, "stock": 7, "category": "Calçados", "sales": 22, "image": "👟"},
    {"id": "8", "name": "Relógio Casio", "price": 349.90, "promotional_price": 299.90, "stock": 20, "category": "Acessórios", "sales": 18, "image": "⌚"}
]

DEMO_CLIENTES = [
    {"id": "1", "name": "João Silva", "email": "joao@email.com", "phone": "(11) 98765-4321", "orders": 5, "total_spent": 1549.50, "last_order": (datetime.now() - timedelta(hours=2)).isoformat()},
    {"id": "2", "name": "Maria Santos", "email": "maria@email.com", "phone": "(11) 91234-5678", "orders": 3, "total_spent": 489.70, "last_order": (datetime.now() - timedelta(hours=5)).isoformat()},
    {"id": "3", "name": "Pedro Costa", "email": "pedro@email.com", "phone": "(11) 95555-9999", "orders": 8, "total_spent": 3240.80, "last_order": (datetime.now() - timedelta(days=1)).isoformat()},
    {"id": "4", "name": "Ana Oliveira", "email": "ana@email.com", "phone": "(11) 98888-7777", "orders": 2, "total_spent": 179.80, "last_order": (datetime.now() - timedelta(days=2)).isoformat()},
    {"id": "5", "name": "Carlos Lima", "email": "carlos@email.com", "phone": "(11) 92222-3333", "orders": 1, "total_spent": 0, "last_order": (datetime.now() - timedelta(days=3)).isoformat()}
]

DEMO_ATIVIDADES = [
    {"id": "1", "type": "order", "message": "Novo pedido #1001 - R$ 299,90", "time": (datetime.now() - timedelta(hours=2)).isoformat(), "read": False},
    {"id": "2", "type": "alert", "message": "Estoque baixo: Fone Bluetooth JBL (3 unidades)", "time": (datetime.now() - timedelta(hours=3)).isoformat(), "read": False},
    {"id": "3", "type": "order", "message": "Pedido #1002 aguardando pagamento", "time": (datetime.now() - timedelta(hours=5)).isoformat(), "read": True},
    {"id": "4", "type": "success", "message": "Pedido #1003 enviado para entrega", "time": (datetime.now() - timedelta(days=1)).isoformat(), "read": True},
    {"id": "5", "type": "alert", "message": "Produto 'Smartwatch Samsung' sem estoque", "time": (datetime.now() - timedelta(days=2)).isoformat(), "read": True}
]

DEMO_CHAT = [
    {"role": "bot", "message": "Olá! Sou o **TrayBot**, seu assistente de e-commerce. Posso ajudar você a gerenciar pedidos, monitorar estoque, analisar vendas e muito mais!", "time": datetime.now().isoformat()}
]


def load_json(filepath, default=None):
    """Carrega dados JSON do arquivo"""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return default if default is not None else []


def save_json(filepath, data):
    """Salva dados JSON no arquivo"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# Inicializar dados demo (para demonstração sem API Tray)
def init_demo_data():
    config = load_json(CONFIG_FILE, {})
    
    if config.get('demo_mode', True):
        # Modo demo: preencher com dados de exemplo
        if not os.path.exists(LOJAS_FILE) or load_json(LOJAS_FILE) == []:
            save_json(LOJAS_FILE, [DEMO_LOJA])
        if not os.path.exists(PEDIDOS_FILE) or load_json(PEDIDOS_FILE) == []:
            save_json(PEDIDOS_FILE, DEMO_PEDIDOS)
        if not os.path.exists(PRODUTOS_FILE) or load_json(PRODUTOS_FILE) == []:
            save_json(PRODUTOS_FILE, DEMO_PRODUTOS)
        if not os.path.exists(CLIENTES_FILE) or load_json(CLIENTES_FILE) == []:
            save_json(CLIENTES_FILE, DEMO_CLIENTES)
        if not os.path.exists(ATIVIDADES_FILE) or load_json(ATIVIDADES_FILE) == []:
            save_json(ATIVIDADES_FILE, DEMO_ATIVIDADES)
        if not os.path.exists(CHAT_FILE) or load_json(CHAT_FILE) == []:
            save_json(CHAT_FILE, DEMO_CHAT)
    else:
        # Modo real: dados vazios
        if not os.path.exists(LOJAS_FILE):
            save_json(LOJAS_FILE, [])
        if not os.path.exists(PEDIDOS_FILE):
            save_json(PEDIDOS_FILE, [])
        if not os.path.exists(PRODUTOS_FILE):
            save_json(PRODUTOS_FILE, [])
        if not os.path.exists(CLIENTES_FILE):
            save_json(CLIENTES_FILE, [])
        if not os.path.exists(ATIVIDADES_FILE):
            save_json(ATIVIDADES_FILE, [])
        if not os.path.exists(CHAT_FILE):
            save_json(CHAT_FILE, [])
    
    if not os.path.exists(CONFIG_FILE):
        save_json(CONFIG_FILE, {"demo_mode": True, "created_at": datetime.now().isoformat()})


init_demo_data()


class TrayHubHandler(BaseHTTPRequestHandler):
    """Handler para requisições HTTP"""

    def log_message(self, format, *args):
        pass  # Silenciar logs

    def _set_headers(self, status=200, content_type='application/json'):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def _json_response(self, data, status=200):
        self._set_headers(status)
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def _serve_file(self, filepath, content_type):
        """Serve arquivo estático"""
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self._json_response({'error': 'Arquivo não encontrado'}, 404)

    def do_OPTIONS(self):
        self._set_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # Arquivos estáticos
        PUBLIC_DIR = os.path.join(os.path.dirname(__file__), 'public')
        
        if path == '/' or path == '/index.html':
            self._serve_file(os.path.join(PUBLIC_DIR, 'index.html'), 'text/html')
            return
        elif path == '/conectar':
            self._serve_file(os.path.join(PUBLIC_DIR, 'conectar.html'), 'text/html')
            return
        elif path == '/pedidos':
            self._serve_file(os.path.join(PUBLIC_DIR, 'pedidos.html'), 'text/html')
            return
        elif path == '/produtos':
            self._serve_file(os.path.join(PUBLIC_DIR, 'produtos.html'), 'text/html')
            return
        elif path == '/clientes':
            self._serve_file(os.path.join(PUBLIC_DIR, 'clientes.html'), 'text/html')
            return
        elif path == '/relatorios':
            self._serve_file(os.path.join(PUBLIC_DIR, 'relatorios.html'), 'text/html')
            return
        elif path.startswith('/css/'):
            filepath = os.path.join(PUBLIC_DIR, path.lstrip('/'))
            self._serve_file(filepath, 'text/css')
            return
        elif path.startswith('/js/'):
            filepath = os.path.join(PUBLIC_DIR, path.lstrip('/'))
            self._serve_file(filepath, 'application/javascript')
            return

        # API Endpoints
        elif path == '/api/status':
            lojas = load_json(LOJAS_FILE, [])
            config = load_json(CONFIG_FILE, {})
            connected = any(l.get('status') == 'connected' for l in lojas)
            demo_mode = config.get('demo_mode', True)
            self._json_response({
                'connected': connected,
                'demo_mode': demo_mode,
                'loja': lojas[0] if lojas else None
            })
            return

        elif path == '/api/dashboard':
            pedidos = load_json(PEDIDOS_FILE, [])
            produtos = load_json(PRODUTOS_FILE, [])
            clientes = load_json(CLIENTES_FILE, [])
            atividades = load_json(ATIVIDADES_FILE, [])

            # Calcular métricas
            total_vendas = sum(p['total'] for p in pedidos if p['status'] in ['approved', 'shipped', 'delivered'])
            total_pedidos = len(pedidos)
            pedidos_hoje = len([p for p in pedidos if p['created_at'].startswith(datetime.now().strftime('%Y-%m-%d'))])
            produtos_baixo_estoque = len([p for p in produtos if p['stock'] <= 5])
            total_clientes = len(clientes)

            # Pedidos por status
            status_count = {}
            for p in pedidos:
                status = p['status']
                status_count[status] = status_count.get(status, 0) + 1

            # Vendas por dia (últimos 7 dias)
            vendas_por_dia = []
            for i in range(6, -1, -1):
                dia = datetime.now() - timedelta(days=i)
                dia_str = dia.strftime('%Y-%m-%d')
                valor = sum(p['total'] for p in pedidos if p['created_at'].startswith(dia_str) and p['status'] in ['approved', 'shipped', 'delivered'])
                vendas_por_dia.append({
                    'dia': dia.strftime('%d/%m'),
                    'valor': valor
                })

            self._json_response({
                'metrics': {
                    'total_vendas': total_vendas,
                    'total_pedidos': total_pedidos,
                    'pedidos_hoje': pedidos_hoje,
                    'produtos_baixo_estoque': produtos_baixo_estoque,
                    'total_clientes': total_clientes,
                    'ticket_medio': total_vendas / total_pedidos if total_pedidos > 0 else 0
                },
                'status_count': status_count,
                'vendas_por_dia': vendas_por_dia,
                'atividades': atividades[:10],
                'pedidos_recentes': pedidos[:5]
            })
            return

        elif path == '/api/pedidos':
            pedidos = load_json(PEDIDOS_FILE, [])
            status_filter = query.get('status', [None])[0]
            if status_filter:
                pedidos = [p for p in pedidos if p['status'] == status_filter]
            self._json_response({'pedidos': pedidos})
            return

        elif path.startswith('/api/pedidos/'):
            pedido_id = path.split('/')[-1]
            pedidos = load_json(PEDIDOS_FILE, [])
            pedido = next((p for p in pedidos if p['id'] == pedido_id), None)
            if pedido:
                self._json_response(pedido)
            else:
                self._json_response({'error': 'Pedido não encontrado'}, 404)
            return

        elif path == '/api/produtos':
            produtos = load_json(PRODUTOS_FILE, [])
            alerta = query.get('alerta', [None])[0]
            if alerta:
                produtos = [p for p in produtos if p['stock'] <= 5]
            self._json_response({'produtos': produtos})
            return

        elif path == '/api/clientes':
            clientes = load_json(CLIENTES_FILE, [])
            self._json_response({'clientes': clientes})
            return

        elif path == '/api/atividades':
            atividades = load_json(ATIVIDADES_FILE, [])
            self._json_response({'atividades': atividades})
            return

        elif path == '/api/chat':
            chat = load_json(CHAT_FILE, [])
            self._json_response({'messages': chat})
            return

        elif path == '/api/relatorios':
            pedidos = load_json(PEDIDOS_FILE, [])
            produtos = load_json(PRODUTOS_FILE, [])
            clientes = load_json(CLIENTES_FILE, [])

            # Relatório de vendas por categoria
            vendas_categoria = {}
            for p in pedidos:
                if p['status'] in ['approved', 'shipped', 'delivered']:
                    for item in p.get('items', []):
                        prod = next((pr for pr in produtos if pr['id'] == item['product_id']), None)
                        if prod:
                            cat = prod['category']
                            vendas_categoria[cat] = vendas_categoria.get(cat, 0) + item['price'] * item['quantity']

            # Top produtos
            top_produtos = sorted(produtos, key=lambda x: x['sales'], reverse=True)[:5]

            # Clientes mais valiosos
            top_clientes = sorted(clientes, key=lambda x: x['total_spent'], reverse=True)[:5]

            self._json_response({
                'vendas_categoria': vendas_categoria,
                'top_produtos': top_produtos,
                'top_clientes': top_clientes,
                'total_vendas': sum(p['total'] for p in pedidos if p['status'] in ['approved', 'shipped', 'delivered']),
                'total_pedidos': len(pedidos),
                'taxa_conversao': 65.5  # Simulado
            })
            return

        else:
            self._json_response({'error': 'Endpoint não encontrado'}, 404)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')

        try:
            data = json.loads(body) if body else {}
        except:
            data = {}

        if path == '/api/chat':
            # Processar mensagem do chat com IA
            message = data.get('message', '').lower()
            chat = load_json(CHAT_FILE, [])

            # Adicionar mensagem do usuário
            chat.append({
                'role': 'user',
                'message': data.get('message', ''),
                'time': datetime.now().isoformat()
            })

            # Resposta inteligente do bot
            resposta = self._processar_mensagem_ia(message, data.get('message', ''))

            chat.append({
                'role': 'bot',
                'message': resposta,
                'time': datetime.now().isoformat()
            })

            save_json(CHAT_FILE, chat)
            self._json_response({'message': resposta})
            return

        elif path == '/api/pedidos/status':
            # Atualizar status do pedido
            pedido_id = data.get('pedido_id')
            novo_status = data.get('status')

            pedidos = load_json(PEDIDOS_FILE, [])
            for p in pedidos:
                if p['id'] == pedido_id:
                    p['status'] = novo_status
                    break

            save_json(PEDIDOS_FILE, pedidos)

            # Registrar atividade
            atividades = load_json(ATIVIDADES_FILE, [])
            atividades.insert(0, {
                'id': str(len(atividades) + 1),
                'type': 'success',
                'message': f'Pedido #{pedido_id} atualizado para {novo_status}',
                'time': datetime.now().isoformat(),
                'read': False
            })
            save_json(ATIVIDADES_FILE, atividades)

            self._json_response({'success': True})
            return

        elif path == '/api/atividades/ler':
            # Marcar atividades como lidas
            atividades = load_json(ATIVIDADES_FILE, [])
            for a in atividades:
                a['read'] = True
            save_json(ATIVIDADES_FILE, atividades)
            self._json_response({'success': True})
            return

        elif path == '/api/conectar':
            # Conexão com Tray (simulada ou real)
            subdominio = data.get('subdominio', '')
            consumer_key = data.get('consumer_key', '')
            consumer_secret = data.get('consumer_secret', '')
            
            # Verificar se é modo demo
            if subdominio == 'demo' or not consumer_key or not consumer_secret:
                # Ativar modo demo
                save_json(CONFIG_FILE, {"demo_mode": True, "created_at": datetime.now().isoformat()})
                
                # Carregar dados demo
                save_json(LOJAS_FILE, [DEMO_LOJA])
                save_json(PEDIDOS_FILE, DEMO_PEDIDOS)
                save_json(PRODUTOS_FILE, DEMO_PRODUTOS)
                save_json(CLIENTES_FILE, DEMO_CLIENTES)
                save_json(ATIVIDADES_FILE, DEMO_ATIVIDADES)
                
                self._json_response({
                    'success': True, 
                    'demo_mode': True,
                    'loja': DEMO_LOJA,
                    'message': 'Modo demo ativado! Use dados de exemplo para testar o dashboard.'
                })
                return
            
            # Tentar conexão real com Tray
            try:
                # Aqui você implementaria a chamada real à API Tray
                # Por enquanto, salvamos as credenciais e retornamos sucesso simulado
                lojas = load_json(LOJAS_FILE, [])
                
                nova_loja = {
                    'id': subdominio,
                    'nome': f'Loja {subdominio}',
                    'subdominio': subdominio,
                    'status': 'connected',
                    'conectado_em': datetime.now().isoformat(),
                    'consumer_key': consumer_key,
                    'consumer_secret': consumer_secret,
                    'access_token': 'token_' + subdominio,
                    'demo_mode': False
                }
                
                # Atualizar ou adicionar
                existente = next((i for i, l in enumerate(lojas) if l['subdominio'] == subdominio), None)
                if existente is not None:
                    lojas[existente] = nova_loja
                else:
                    lojas.append(nova_loja)
                
                save_json(LOJAS_FILE, lojas)
                
                # Desativar modo demo
                save_json(CONFIG_FILE, {"demo_mode": False, "created_at": datetime.now().isoformat()})
                
                # Limpar dados demo (usuário deve sincronizar)
                save_json(PEDIDOS_FILE, [])
                save_json(PRODUTOS_FILE, [])
                save_json(CLIENTES_FILE, [])
                save_json(ATIVIDADES_FILE, [])
                
                self._json_response({
                    'success': True, 
                    'demo_mode': False,
                    'loja': nova_loja,
                    'message': f'Loja {subdominio} conectada! Agora sincronize seus dados.'
                })
                return
                
            except Exception as e:
                self._json_response({
                    'success': False,
                    'error': f'Erro ao conectar: {str(e)}'
                }, 500)
                return

        else:
            self._json_response({'error': 'Endpoint não encontrado'}, 404)

    def _processar_mensagem_ia(self, message_lower, original_message):
        """Processa mensagem e retorna resposta inteligente"""
        pedidos = load_json(PEDIDOS_FILE, [])
        produtos = load_json(PRODUTOS_FILE, [])
        clientes = load_json(CLIENTES_FILE, [])

        # Saudações
        if any(p in message_lower for p in ['oi', 'olá', 'ola', 'eae', 'hey', 'hi']):
            return "Olá! 👋 Como posso ajudar sua loja hoje? Posso verificar pedidos, estoque, vendas ou responder dúvidas!"

        # Pedidos
        if any(p in message_lower for p in ['pedido', 'venda', 'compra']):
            total = len(pedidos)
            pendentes = len([p for p in pedidos if p['status'] == 'pending'])
            aprovados = len([p for p in pedidos if p['status'] == 'approved'])
            return f"📦 **Status dos Pedidos:**\n\n• Total: {total} pedidos\n• Pendentes: {pendentes}\n• Aprovados: {aprovados}\n\nQuer que eu mostre os pedidos mais recentes ou filtre por status?"

        # Estoque
        if any(p in message_lower for p in ['estoque', 'produto', 'disponível', 'tem']):
            baixo = [p for p in produtos if p['stock'] <= 5]
            if baixo:
                lista = '\n'.join([f"• {p['name']}: {p['stock']} unidades" for p in baixo])
                return f"⚠️ **Produtos com estoque baixo:**\n\n{lista}\n\nRecomendo repor o estoque desses produtos para não perder vendas!"
            else:
                return "✅ **Estoque OK!** Todos os produtos estão com quantidade adequada."

        # Vendas / Faturamento
        if any(p in message_lower for p in ['venda', 'faturamento', 'receita', 'lucro', 'dinheiro', 'quanto vendi']):
            total = sum(p['total'] for p in pedidos if p['status'] in ['approved', 'shipped', 'delivered'])
            return f"💰 **Resumo de Vendas:**\n\n• Total faturado: R$ {total:,.2f}\n• Total de pedidos: {len(pedidos)}\n• Ticket médio: R$ {total/len(pedidos) if pedidos else 0:,.2f}\n\nQuer ver um relatório mais detalhado?"

        # Clientes
        if any(p in message_lower for p in ['cliente', 'comprador', 'pessoa']):
            return f"👥 **Base de Clientes:**\n\n• Total: {len(clientes)} clientes\n• Cliente mais valioso: {clientes[0]['name'] if clientes else 'N/A'} (R$ {clientes[0]['total_spent']:,.2f})\n\nQuer ver detalhes de algum cliente específico?"

        # Ajuda / Comandos
        if any(p in message_lower for p in ['ajuda', 'help', 'comando', 'o que você faz', 'o que faz']):
            return "🤖 **O que eu posso fazer:**\n\n• 📦 Ver status de pedidos\n• 📊 Mostrar vendas e faturamento\n• ⚠️ Alertar estoque baixo\n• 👥 Listar clientes\n• 📈 Gerar relatórios\n• 💡 Dar dicas de vendas\n\n**Exemplos:**\n• 'Quantos pedidos pendentes?'\n• 'Qual produto mais vendeu?'\n• 'Me dê uma dica de vendas'"

        # Dicas
        if any(p in message_lower for p in ['dica', 'sugestão', 'melhorar', 'aumentar venda']):
            dicas = [
                "💡 **Dica:** Produtos com frete grátis convertem 40% mais. Considere oferecer frete grátis acima de um valor mínimo!",
                "💡 **Dica:** Responder dúvidas de clientes em até 1 hora aumenta a taxa de conversão em 25%.",
                "💡 **Dica:** Produtos com fotos de alta qualidade vendem 3x mais. Invista em boas imagens!",
                "💡 **Dica:** Oferecer parcelamento sem juros aumenta o ticket médio em 30%.",
                "💡 **Dica:** Enviar e-mail de carrinho abandonado recupera 15% das vendas perdidas."
            ]
            import random
            return random.choice(dicas)

        # Produto mais vendido
        if any(p in message_lower for p in ['mais vendido', 'top produto', 'melhor produto']):
            top = sorted(produtos, key=lambda x: x['sales'], reverse=True)[:3]
            lista = '\n'.join([f"{i+1}. {p['name']} - {p['sales']} vendas" for i, p in enumerate(top)])
            return f"🏆 **Top Produtos:**\n\n{lista}"

        # Despedida
        if any(p in message_lower for p in ['tchau', 'adeus', 'até', 'ate logo', 'valeu']):
            return "Até logo! 👋 Se precisar de mais alguma coisa, é só chamar. Boa sorte com suas vendas! 🚀"

        # Padrão
        return f"Entendi! Você disse: '{original_message}'\n\nPosso ajudar com:\n• 📦 Pedidos e vendas\n• 📊 Relatórios e métricas\n• ⚠️ Alertas de estoque\n• 👥 Clientes\n• 💡 Dicas de vendas\n\nO que você precisa?"


def run_server():
    server = HTTPServer(('0.0.0.0', PORT), TrayHubHandler)
    print(f"🚀 TrayHub AI rodando em http://0.0.0.0:{PORT}")
    server.serve_forever()


if __name__ == '__main__':
    run_server()
