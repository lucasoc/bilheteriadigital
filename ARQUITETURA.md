# Arquitetura e Fluxo da Aplicação

## 1. Cliente e Frontend
- O cliente acessa o site hospedado como um Site Estático no Amazon S3.
- O conteúdo do site é entregue pelo CloudFront (CDN da AWS) para melhorar desempenho e segurança.

## 2. Autenticação
- Todas as requisições passam pelo API Gateway, que serve como porta de entrada para a API.
- O API Gateway usa um Lambda Authorizer para validar o token Bearer (JWT) em todas as rotas protegidas.
- O endpoint `/login` é chamado via POST para fazer login, e essa chamada vai para uma LambdaLogin que verifica credenciais no banco RDS BilheteriaDB.

## 3. Reserva e Consulta
- Para criar reservas, o cliente faz POST para `/reserva` que vai para LambdaCriaReserva, que grava as reservas no banco DynamoDB (usado aqui para controle rápido e escalável das reservas).
- Consultas de reserva são feitas via GET `/consulta-reserva` com a LambdaConsultaReserva consultando o DynamoDB.
- Consulta de bilhetes disponíveis é feita via GET `/consulta-bilhete`, atendida pela LambdaConsultaBilhetes que faz consulta no banco relacional RDS e no DynamoDB para vagas disponíveis e reservas ativas.

## 4. Produtos adicionais e Finalização da Compra
- Consulta de produtos adicionais disponíveis é feita via GET `/consulta-produtos` na LambdaConsultaProdutos, que consulta o banco RDS.
- Para finalizar a compra, o cliente faz POST `/finaliza-compra` na LambdaFinalizaCompra, que grava a compra no banco RDS e envia uma mensagem para a fila SQS Pagamentos para processar o pagamento.

## 5. Processamento de Pagamento e Confirmação
- O sistema de pagamento externo consome mensagens da fila SQS.
- Quando o pagamento é concluído (sucesso ou falha), o sistema de pagamento notifica a LambdaConcluiPedido.
- Essa Lambda atualiza o status do pedido no banco RDS.
- Também aciona o serviço SNS para enviar um e-mail de confirmação ao cliente.

## 6. Banco de Dados
- **RDS BilheteriaDB**: banco relacional para armazenar dados de usuários, pedidos, produtos.
- **DynamoDB**: banco NoSQL para controle rápido das reservas, porque oferece baixa latência e alta escalabilidade.

---

## Resumo do fluxo principal
1. Cliente acessa site estático via CloudFront.  
2. Cliente faz login, token JWT é validado via Lambda Authorizer no API Gateway.  
3. Cliente consulta e cria reservas, consulta e escolhe produtos.  
4. Cliente finaliza compra, que envia pedido para sistema de pagamento via SQS.  
5. Sistema de pagamento confirma status, Lambda atualiza banco e envia e-mail.

---

# Escolha dos Componentes AWS

## 1. Amazon S3 para Site Estático  
**Por quê?**  
O Amazon S3 é ideal para hospedar sites estáticos porque oferece alta disponibilidade, durabilidade e escalabilidade automática, além de ser altamente econômico.

**Benefícios:**  
- Sem necessidade de gerenciar servidores.  
- Integração direta com CloudFront para distribuição global rápida.  
- Custo muito baixo para armazenamento e transferência.

---

## 2. CloudFront (CDN)  
**Por quê?**  
CloudFront melhora a performance e segurança do site, entregando conteúdo em cache em servidores próximos ao usuário.

**Benefícios:**  
- Reduz latência para o usuário final.  
- Protege contra ataques comuns como DDoS (via AWS Shield).  
- Permite configurar SSL/TLS para HTTPS com facilidade.

---

## 3. API Gateway  
**Por quê?**  
Atua como a "porta de entrada" unificada para a API, gerenciando autenticação, throttling, e roteamento.

**Benefícios:**  
- Gerenciamento simplificado das rotas e segurança.  
- Suporte nativo para integração com Lambda e autorização via Lambda Authorizer.  
- Escala automaticamente conforme a demanda.

---

## 4. Lambda Authorizer para Validação JWT  
**Por quê?**  
Usar Lambda Authorizer para validar tokens JWT permite controle granular da autenticação, sem precisar gerenciar servidores dedicados.

**Benefícios:**  
- Flexível para customizar regras de validação.  
- Evita expor endpoints protegidos sem autenticação.  
- Escalabilidade automática, paga-se só pelo uso.

---

## 5. AWS Lambda para Lógica de Negócio  
**Por quê?**  
As Lambdas executam a lógica das operações (login, reserva, consulta, finalização) em um modelo serverless que reduz custo operacional.

**Benefícios:**  
- Não há necessidade de provisionar ou gerenciar servidores.  
- Escalabilidade automática e custo baseado em execução real.  
- Fácil integração com outros serviços AWS (DynamoDB, RDS, SQS).

---

## 6. Amazon DynamoDB para Controle Rápido e Escalável de Reservas  
**Por quê?**  
DynamoDB é uma base NoSQL rápida e altamente escalável, perfeita para operações frequentes de leitura e gravação com baixa latência.

**Benefícios:**  
- Baixa latência e alta performance para reservas.  
- Escalabilidade automática para picos de acesso.  
- Modelo de dados flexível que se adapta facilmente às mudanças.

---

## 7. Amazon RDS para Dados Relacionais  
**Por quê?**  
RDS é ideal para armazenar dados relacionais que exigem integridade, como usuários, pedidos e produtos.

**Benefícios:**  
- Gerenciamento simplificado do banco relacional (backup, patch, replicação).  
- Suporte a consultas complexas e relacionamentos.  
- Alta disponibilidade e durabilidade configuráveis.

---

## 8. Amazon SQS para Processamento Assíncrono de Pagamentos  
**Por quê?**  
SQS desacopla a finalização da compra do processamento do pagamento, permitindo maior resiliência e escalabilidade.

**Benefícios:**  
- Garante entrega confiável de mensagens entre sistemas.  
- Facilita a tolerância a falhas e processamento assíncrono.  
- Permite escalonar o consumo de mensagens conforme demanda.

---

## 9. Amazon SNS para Notificações  
**Por quê?**  
SNS permite envio de notificações por múltiplos canais, como e-mail, facilitando o envio do e-mail de confirmação.

**Benefícios:**  
- Fácil integração e configuração para envio de mensagens.  
- Suporta fan-out para múltiplos assinantes, caso seja necessário.  
- Alta disponibilidade e escalabilidade automática.

---

## Resumo  
Essa arquitetura aproveita ao máximo o modelo serverless e os serviços gerenciados da AWS para:

- Minimizar custos operacionais.  
- Aumentar escalabilidade e performance.  
- Garantir alta disponibilidade e segurança.  
- Facilitar manutenção e evolução do sistema.
