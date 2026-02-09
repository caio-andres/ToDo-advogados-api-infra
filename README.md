# Todo Advogados API

API REST serverless para gerenciamento de tarefas de advogados, construída com AWS Lambda, API Gateway e PostgreSQL.

### Excalidraw workspace

https://link.excalidraw.com/l/92vNxGmOx1N/93m5jsFp710

### Atual

Permite **advogados** criarem, listarem, modificarem e deletarem **tarefas**.

### Futuro

Permite **advogados** criarem, listarem, modificarem e deletarem **tarefas** em **boards** específicos.

## Stack Tecnológica

- **Runtime:** Python 3.12
- **Framework:** AWS Lambda Powertools
- **API:** API Gateway HTTP API (v2)
- **Database:** RDS PostgreSQL 15.14
- **ORM:** SQLAlchemy 2.0
- **Validação:** Pydantic
- **Auth:** JWT + bcrypt
- **IaC:** SAM (Lambda/API) + Terraform (RDS)
- **Logs:** CloudWatch

## Funcionalidades

- Registro e autenticação de usuários
- CRUD completo de tarefas
- Autenticação JWT com expiração
- Isolamento de dados por usuário
- Logs estruturados e rastreamento de requisições

## Arquitetura

```
Cliente → API Gateway → Lambda → PostgreSQL
                          ↓
                    CloudWatch Logs
                          ↓
                    SSM Parameter Store
```

A aplicação segue o padrão MVCS:

- **Models:** Definição das tabelas (SQLAlchemy)
- **Views:** Endpoints REST (routes/)
- **Controllers:** Lógica de roteamento
- **Services:** Regras de negócio

## Endpoints

### Públicos

- `GET /` - Root
- `GET /health` - Health check
- `POST /usuarios/registrar` - Criar conta
- `POST /usuarios/login` - Autenticar

### Protegidos (requer JWT)

- `GET /usuarios/me` - Dados do usuário
- `GET /tarefas` - Listar tarefas
- `POST /tarefas` - Criar tarefa
- `GET /tarefas/{id}` - Buscar tarefa
- `PUT /tarefas/{id}` - Atualizar tarefa
- `DELETE /tarefas/{id}` - Deletar tarefa

## Deploy

### 1. Infraestrutura (Terraform)

```bash
cd terraform

export TF_VAR_db_password="sua-senha-segura"
export TF_VAR_jwt_secret_key=$(openssl rand -base64 32)
export TF_VAR_secret_key=$(openssl rand -base64 32)

terraform init
terraform plan
terraform apply
```

Isso cria:

- VPC com subnets públicas e privadas
- RDS PostgreSQL
- Security Groups
- SSM Parameters com secrets

### 2. Lambda e API Gateway (SAM)

```bash
sam build
sam deploy --guided
```

Na primeira execução, configure:

- Stack name: `todo-advogados-mvp`
- Region: `us-east-1`
- Environment: `dev`
- Confirm changes: `Y`
- Allow SAM CLI IAM role creation: `Y`
- Save arguments to config: `Y`

Deploys subsequentes:

```bash
sam build && sam deploy
```

### 3. Verificar Deploy

```bash
aws cloudformation describe-stacks \
  --stack-name todo-advogados-mvp \
  --query 'Stacks[0].Outputs'
```

Anote a URL do API Gateway.

## Desenvolvimento Local

### Requisitos

- Python 3.12
- Docker (se quiser utilizar SAM localmente)
- AWS CLI configurado
- SAM CLI
- Terraform

### Setup

```bash
cd src
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Testes Locais

```bash
sam local start-api
```

A API estará disponível em `http://localhost:3000`

## Uso da API

### Registrar Usuário

```bash
curl -X POST https://sua-api.execute-api.us-east-1.amazonaws.com/usuarios\
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva",
    "email": "joao@example.com",
    "senha": "senha123"
  }'
```

### Login

```bash
curl -X POST https://sua-api.execute-api.us-east-1.amazonaws.com/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "joao@example.com",
    "senha": "senha123"
  }'
```

Resposta:

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "usuario": {
    "id": "uuid",
    "nome": "João Silva",
    "email": "joao@example.com"
  }
}
```

### Criar Tarefa

```bash
curl -X POST https://sua-api.execute-api.us-east-1.amazonaws.com/tarefas \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -d '{
    "titulo": "Revisar contrato",
    "descricao": "Contrato de prestação de serviços",
    "status": "pendente"
  }'
```

### Listar Tarefas

```bash
curl https://sua-api.execute-api.us-east-1.amazonaws.com/tarefas \
  -H "Authorization: Bearer SEU_TOKEN"
```

### Atualizar Tarefa

```bash
curl -X PUT https://sua-api.execute-api.us-east-1.amazonaws.com/tarefas/{id} \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -d '{
    "status": "concluida"
  }'
```

### Deletar Tarefa

```bash
curl -X DELETE https://sua-api.execute-api.us-east-1.amazonaws.com/tarefas/{id} \
  -H "Authorization: Bearer SEU_TOKEN"
```

## Segurança

- Senhas hasheadas com bcrypt
- Tokens JWT com expiração de 7 dias
- Secrets no SSM Parameter Store (não no código)
- Validação de entrada com Pydantic
- Isolamento de dados por usuário
- HTTPS obrigatório
- CORS configurado

## Monitoramento

### CloudWatch Logs

```bash
aws logs tail /aws/lambda/todo-advogados-mvp-api --follow
# se der erro no comando, utilize MSYS2_ARG_CONV_EXCL="*" antes do comando inteiro
```

### Métricas

- Invocações da Lambda
- Duração de execução
- Erros e throttling
- Requisições do API Gateway
- Conexões do RDS

## Custos Estimados

Para uso moderado (1000 req/dia):

- Lambda: ~$0.20/mês
- API Gateway: ~$3.50/mês
- RDS (db.t3.micro): ~$15/mês
- **Total: ~$19/mês**

## Troubleshooting

### Lambda não conecta no RDS

- Verificar Security Group permite conexão da Lambda
- Verificar Lambda está na mesma VPC do RDS
- Verificar credenciais no SSM Parameter Store

### Erro 401 Unauthorized

- Token expirado (7 dias)
- Token inválido ou malformado
- Header Authorization ausente

### Erro 500 Internal Server Error

- Verificar logs no CloudWatch
- Verificar conexão com banco
- Verificar secrets no SSM

## Limpeza

Para remover toda a infraestrutura:

```bash
sam delete

cd terraform
terraform destroy
```

> Feito por Caio André. 😼👊🏻
