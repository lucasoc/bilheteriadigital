# 🎟️ Bilheteria Digital

Um sistema simples de bilhetagem digital que simula a reserva de cargos e compra de produtos adicionais, utilizando um backend em FastAPI e frontend em React.

---

## 📁 Estrutura do Projeto

```
bilheteriadigital/
├── backend/
│   ├── main.py               # API FastAPI com rotas de reserva, consulta e finalização
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
        └── pages/
            ├── Home.js       # Página de seleção de cargo
            └── Produtos.js   # Página de seleção de produtos adicionais
```

---

## 🚀 Tecnologias Utilizadas

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** – API moderna, rápida e baseada em Python 3.9+
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

- ✅ Reserva de cargos com tempo limite (TTL de 3 minutos)
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
  "1234": {
    "cargo": "dev",
    "expira_em": 1718418000
  }
}
```

### `rds.json`
Simula um **banco relacional (RDS)**, controlando vagas e estoque:
```json
{
  "vagas": {
    "dev": 2,
    "qa": 2
  },
  "produtos": {
    "camiseta": 50,
    "caneca": 30
  },
  "compras": []
}
```

---

## 📌 Regras do Sistema

- Cada **cargo** possui N vagas no total.
- A reserva expira em 3 minutos se o usuário não concluir a compra.
- A finalização de compra remove:
  - A vaga do cargo (decrementa no `rds.json`)
  - O estoque dos produtos selecionados
- A interface desabilita os cargos com 0 vagas disponíveis ou que estejam com todas as vagas reservadas.

---

## ✅ Próximos Passos

Sugestões para evoluir o projeto:

- 🔐 Autenticação de usuários
- 💾 Integração real com bancos (DynamoDB, PostgreSQL, etc.)
- 📊 Painel administrativo para controle de estoque e compras
- 📧 Envio de e-mails de confirmação
- 📱 Interface mobile responsiva

---

## 🧑‍💻 Autor

Desenvolvido por [Lucas Oliveira Conti](https://github.com/lucasoc)
