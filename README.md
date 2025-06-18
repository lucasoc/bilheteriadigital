# 🎟️ Bilheteria Digital

Um sistema simples de bilhetagem digital que simula a reserva de cargos e compra de produtos adicionais, utilizando um backend em FastAPI e frontend em React.

---

## 📁 Estrutura do Projeto

```
bilheteriadigital/
├── backend/
│   ├── main.py               # API FastAPI com rotas de reserva, consulta e finalização
│   ├── auth.py               # Validacao e criacao do token jwt
│   ├── dynamodb.json         # Simulação de banco DynamoDB (reservas temporárias)
│   ├── rds.json              # Simulação de banco RDS (estoque, contagem de vagas, compras)
│   └── requirements.txt      # Dependências do backend
└── frontend/
    ├── package.json          # Dependências e scripts React
    ├── public/               # Arquivos estáticos
    └── src/
        ├── App.js            # Roteamento principal
        ├── index.js          # Ponto de entrada React
        ├── index.css         # Estilos globais
        ├── utils/
        │   └── authFetch.js  # Configuracao para adicionar o bearer token em todas as chamadas
        └── pages/
            ├── Home.js       # Página de seleção de cargo
            ├── Login.js      # Página de Login
            └── Produtos.js   # Página de seleção de produtos adicionais
```

---

## 🚀 Tecnologias Utilizadas

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** – API moderna, rápida e baseada em Python 3.9+
- Middleware personalizado para autenticação JWT
- Armazenamento local com arquivos `.json`:
  - `dynamodb.json`: simula reservas temporárias (estilo TTL do DynamoDB)
  - `rds.json`: simula estoque, controle de vagas e histórico de compras

### Frontend
- **[React](https://reactjs.org/)** com Create React App
- **React Router DOM** – para navegação entre páginas
- **Fetch API** – para integração com o backend
- CSS responsivo básico

---

## ⚙️ Como rodar localmente

### 1. Clonar o repositório

```bash
git clone https://github.com/lucasoc/bilheteriadigital.git
cd bilheteriadigital
```
Caso nao possua as credenciais, o repositorio tambem pode ser baixado como arquivo .zip

### 2. Rodar o backend (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate   # No Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

A API estará acessível em: [http://localhost:8000](http://localhost:8000)

### 3. Rodar o frontend (React)

Em outro terminal:

```bash
cd frontend
npm install
npm start
```

A aplicação será executada em: [http://localhost:3000](http://localhost:3000)

---

## 💡 Funcionalidades

- ✅ Login com autenticação via JWT  
- ✅ Reserva de cargos com tempo limite (TTL de 1 minuto)
- ✅ Consulta de disponibilidade de vagas
- ✅ Desabilita cargos já reservados ou esgotados
- ✅ Escolha de produtos adicionais (com controle de estoque)
- ✅ Finalização de compra com baixa no RDS

---

## 🧪 Simulação de Bancos

Este projeto não usa banco de dados real. Em vez disso, utiliza dois arquivos `.json` para simular:

### `dynamodb.json`
Simula o comportamento de um **DynamoDB**, com TTL para reservas:
```json
{
  "coordenador": [
    {
      "usuarioId": "lucas123",
      "expirationTime": 1750277626,
      "pedidoId": "bab023b1-4833-49cc-8cb0-026f3d34bf6c"
    }
  ],
  "senior": [], 
  "pleno": []
}
```

### `rds.json`
Simula um **banco relacional (RDS)**, controlando vagas e estoque:
```json
{
  "estoque": {
    "Consultoria com Michel": 7,
    "Cafe com Danilo": 3,
    "Bate Papo com Silva": 4,
    "Acompanhamento com Celso": 4,
    "Papo Carreira com Shindi": 5
  },
  "compras": [
    {
      "usuarioId": "lucas123",
      "cargoId": "senior",
      "pedidoId": "fe171e1c-aa24-4dfc-b945-fbe30994aabf",
      "produtos": {
        "Papo Carreira com Shindi": 1,
        "Consultoria com Michel": 1,
        "Cafe com Danilo": 1,
        "Bate Papo com Silva": 1,
        "Acompanhamento com Celso": 2
      },
      "statusPagamento": "true"
    }
  ],
  "vagas": {
    "junior": 2,
    "pleno": 2,
    "senior": 1,
    "coordenador": 2
  },
  "users": {
    "lucas123": {
      "password": "$2b$12$wdk5efOey9gZFdFu9./BPe0m0jfuMorDX37DUkNNmLIMOdGKFycka"
    },
    "lucas321": {
      "password": "$2b$12$wdk5efOey9gZFdFu9./BPe0m0jfuMorDX37DUkNNmLIMOdGKFycka"
    }
  }
}
```

---

## 📌 Regras do Sistema

- Cada **cargo** possui N vagas no total.
- A reserva expira em 1 minuto se o usuário não concluir a compra.
- A finalização de compra remove:
  - A vaga do cargo (decrementa no `rds.json`)
  - O estoque dos produtos selecionados
- A interface desabilita os cargos com 0 vagas disponíveis ou que estejam com todas as vagas reservadas.

---

## 🧠 Fluxo da Aplicação

### 🔐 Login
Usuário insere nome e senha. Se autenticado, recebe um token JWT que é armazenado no `localStorage`.

### 🏠 Home
Exibe os cargos disponíveis (Junior, Pleno, Senior, Coordenador). Ao clicar, uma reserva é feita no backend e o usuário é redirecionado.

### 📦 Produtos
Usuário escolhe produtos adicionais dentro de um tempo limite. Reserva é invalidada se o tempo expirar.

### ✅ Finalização
Ao finalizar, os dados são enviados para `/finaliza-compra`.

---

## 📡 Endpoints Backend

| Método | Rota                        | Descrição                                         |
|--------|-----------------------------|---------------------------------------------------|
| POST   | `/login`                    | Retorna JWT se usuário for válido                 |
| GET    | `/consulta-bilhete`         | Retorna cargos já ocupados                        |
| POST   | `/reserva`                  | Reserva temporariamente um cargo                  |
| GET    | `/consulta-reserva`         | Verifica se reserva ainda é válida                |
| GET    | `/consulta-produtos`        | Retorna produtos disponíveis                      |
| POST   | `/finaliza-compra`          | Finaliza a inscrição e reserva                    |
| POST   | `/conclui-pedido`           | Atualiza o status do pedido com sucesso ou falha  |

---

## 🔐 Autenticação JWT

- O backend possui um middleware que valida o token JWT para todas as rotas protegidas.
- O frontend envia o token no header `Authorization` via `utils/authFetch.js`.

---

## 🧪 Teste Rápido

1. Inicie o backend.
2. Inicie o frontend.
3. Acesse `http://localhost:3000/login`.
4. Use um login existente (ex: `lucas123` / `senha`) ou defina usuários válidos no backend.
5. Escolha um cargo.
6. Escolha produtos.
7. Finalize.

---

## 🧑‍💻 Autor

Desenvolvido por [Lucas Oliveira Conti](https://github.com/lucasoc)
