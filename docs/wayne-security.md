# Wayne Security System
🦇 Wayne Industries - Sistema de Segurança

Sistema completo de gerenciamento de segurança e controle de acesso para as Indústrias Wayne, desenvolvido com Flask no backend e JavaScript vanilla no frontend.

📋 Índice
Visão Geral

Funcionalidades

Tecnologias

Estrutura do Projeto

Instalação e Configuração

Uso do Sistema

API Endpoints

Desenvolvimento

Contribuição

🎯 Visão Geral
O Sistema Wayne Industries é uma plataforma de segurança corporativa que oferece:

Controle de acesso baseado em funções

Gestão de recursos internos

Dashboard administrativo em tempo real

Autenticação segura com JWT

Interface responsiva e intuitiva

⚡ Funcionalidades
🔐 Sistema de Autenticação
Login seguro com JWT

Diferentes níveis de acesso

Logout automático

Proteção de rotas

🛡️ Controle de Acesso
Áreas Restritas com permissões granulares

Verificação em tempo real de autorização

Registro de auditoria de acessos

Hierarquia de funções:

Administrador

Admin de Segurança

Gerente

Funcionário

📦 Gestão de Recursos
CRUD completo de recursos internos

Interface administrativa dedicada

Permissões visuais baseadas em função

Atualização em tempo real

📊 Dashboard
Status de segurança em tempo real

Visualização de recursos acessíveis

Painel administrativo condicional

Design responsivo

🛠 Tecnologias
Backend
Python 3.x

Flask - Framework web

Flask-JWT-Extended - Autenticação JWT

Flask-CORS - Controle de CORS

Python-dotenv - Variáveis de ambiente

Frontend
HTML5 - Estrutura

CSS3 - Estilos e design responsivo

JavaScript ES6+ - Lógica da aplicação

Fetch API - Comunicação com backend

📁 Estrutura do Projeto
text
project_wayne/
├── project_wayne/
│   ├── backend/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # Rotas de autenticação
│   │   │   ├── access.py        # Rotas de controle de acesso
│   │   │   └── ...              # Outros módulos
│   │   └── app.py               # Aplicação principal Flask
│   ├── frontend/
│   │   ├── index.html           # Página de login
│   │   ├── dashboard.html       # Painel principal
│   │   ├── css/
│   │   │   └── style.css        # Estilos principais
│   │   └── js/
│   │       └── auth.js          # Lógica de autenticação
│   ├── requirements.txt         # Dependências Python
│   └── README.md               # Este arquivo
└── venv/                       # Ambiente virtual Python
🚀 Instalação e Configuração
Pré-requisitos
Python 3.8+

pip (gerenciador de pacotes Python)

Navegador web moderno

1. Clone o repositório
bash
git clone <url-do-repositorio>
cd project_wayne
2. Configure o ambiente virtual
bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
3. Instale as dependências
bash
pip install -r requirements.txt
4. Execute a aplicação
bash
cd project_wayne/backend
python app.py
5. Acesse o sistema
Frontend: http://localhost:3000 (ou servidor estático)

Backend: http://localhost:5000

👥 Uso do Sistema
Credenciais de Teste
Usuário	Senha	Função	Acesso
bruce	batman123	Administrador	Total
alfred	mayordomo	Admin Segurança	Administrativo
lucius	techmaster	Gerente	Gerencial
selina	gato123	Funcionária	Básico
Fluxo de Uso
Login: Acesse a página inicial e faça login

Dashboard: Visualize seu status e recursos acessíveis

Navegação:

Administradores: Botão "Gerenciar Recursos" disponível

Outros usuários: Apenas visualização de recursos

Gestão (apenas admins):

Adicionar novos recursos

Editar permissões existentes

Remover recursos

🌐 API Endpoints
Autenticação
POST /api/login - Autenticar usuário

GET /api/areas - Listar áreas acessíveis

GET /api/verificar-acesso/<area> - Verificar acesso específico

Administração
GET /api/admin/recursos - Listar todos os recursos

POST /api/admin/recursos - Criar novo recurso

PUT /api/admin/recursos/<id> - Atualizar recurso

DELETE /api/admin/recursos/<id> - Excluir recurso

Auditoria
GET /api/registros - Visualizar registros de acesso (apenas admins)

🔧 Desenvolvimento
Estrutura de Desenvolvimento
python
# Backend - Padrão MVC com Blueprints
app.py                 # Aplicação principal
api/
  auth.py             # Autenticação e usuários
  access.py           # Controle de acesso e recursos
Variáveis de Ambiente
bash
# Criar arquivo .env na raiz do backend
SECRET_KEY=chave-secreta-aqui
JWT_SECRET_KEY=chave-jwt-secreta-aqui
Comandos Úteis
bash
# Desenvolvimento
python app.py                    # Iniciar servidor
python -m pytest tests/         # Executar testes

# Produção
gunicorn app:app               # Servidor production
🎨 Personalização
Cores e Tema
O sistema usa variáveis CSS para fácil customização:

css
:root {
    --wayne-blue: #0A192F;
    --wayne-yellow: #FFD700;
    --text-light: #E6E6FA;
    /* Personalize estas cores */
}
Adicionar Novas Funções
Modifique auth.py - dicionário de usuários

Atualize access.py - matriz de permissões

Teste as novas permissões

🤝 Contribuição
Reportar Problemas
Verifique se o problema já existe nas issues

Crie uma nova issue com:

Descrição detalhada

Passos para reproduzir

Comportamento esperado vs atual

Sugerir Melhorias
Fork o projeto

Crie uma branch feature (git checkout -b feature/nova-funcionalidade)

Commit suas mudanças (git commit -m 'Adiciona nova funcionalidade')

Push para a branch (git push origin feature/nova-funcionalidade)

Abra um Pull Request

📄 Licença
Este projeto é desenvolvido para fins educacionais e demonstrativos.

🆘 Suporte
Problemas Comuns
Erro de Conexão Recusada

bash
# Verificar se o servidor está rodando
python app.py
# Acesse: http://localhost:5000
Erro de Módulo Não Encontrado

bash
# Reinstalar dependências
pip install -r requirements.txt
Problemas de CORS

Verifique se Flask-CORS está instalado

Confirme as configurações no app.py