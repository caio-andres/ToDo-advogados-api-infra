# Build, Deploy, Execução Local e Monitoramento

Guia completo de como fazer build, deploy, rodar localmente, testar e monitorar a aplicação.

## 1. Build

### 1.1 Build Básico

```bash
sam build
```

**O que acontece:**
- Lê o `template.yaml`
- Copia código de `src/` para `.aws-sam/build/`
- Instala dependências do `requirements.txt`
- Prepara pacote para deploy
- Usa cache se nada mudou (`cached = true` no samconfig.toml)
- Build paralelo habilitado (`parallel = true`)

**Saída:**
```
Building codeuri: src/ runtime: python3.12 architecture: x86_64 functions: TodoApiFunction
Running PythonPipBuilder:ResolveDependencies
Running PythonPipBuilder:CopySource

Build Succeeded

Built Artifacts  : .aws-sam/build
Built Template   : .aws-sam/build/template.yaml
```

### 1.2 Build com Container (recomendado)

```bash
sam build --use-container
```

**Quando usar:**
- Você está no Windows/Mac mas o Lambda roda em Linux
- Dependências com código nativo (psycopg2, bcrypt)
- Garantir compatibilidade exata com ambiente Lambda

**Requer:** Docker rodando

### 1.3 Build Limpo

```bash
sam build --use-container --cached false
```

Força rebuild completo, ignorando cache.

### 1.4 Validar Template

```bash
sam validate
```

Valida sintaxe do `template.yaml` antes do build.

```bash
sam validate --lint
```

Valida e faz lint (habilitado por padrão no samconfig.toml).

## 2. Deploy

### 2.1 Deploy Guiado (primeira vez)

```bash
sam deploy --guided
```

Faz perguntas interativas e salva respostas no `samconfig.toml`.

### 2.2 Deploy Normal

```bash
sam deploy
```

Usa configurações do `samconfig.toml`:
- Stack: `todo-advogados-mvp`
- Region: `us-east-1`
- Environment: `dev`
- Capabilities: `CAPABILITY_IAM`
- Confirm changeset: `true` (pede confirmação)

**O que acontece:**
1. Faz upload do código para S3
2. Cria/atualiza CloudFormation stack
3. Cria Lambda Function
4. Cria API Gateway
5. Cria Log Groups
6. Configura permissões IAM

**Saída:**
```
Deploying with following values
===============================
Stack name                   : todo-advogados-mvp
Region                       : us-east-1
Confirm changeset            : True
Deployment s3 bucket         : aws-sam-cli-managed-default-samclisourcebucket-xxx
Capabilities                 : ["CAPABILITY_IAM"]
Parameter overrides          : {"Environment": "dev"}

Changeset created successfully. arn:aws:cloudformation:...

Previewing CloudFormation changeset before deployment
======================================================
Deploy this changeset? [y/N]: y

CloudFormation stack changeset
-------------------------------------------------------------------------------------------------
Operation                LogicalResourceId        ResourceType             Replacement
-------------------------------------------------------------------------------------------------
+ Add                    TodoApiFunction          AWS::Lambda::Function    N/A
+ Add                    TodoApi                  AWS::ApiGatewayV2::Api   N/A
-------------------------------------------------------------------------------------------------

Successfully created/updated stack - todo-advogados-mvp in us-east-1
```

### 2.3 Deploy sem Confirmação

```bash
sam deploy --no-confirm-changeset
```

Deploy direto, sem pedir confirmação.

### 2.4 Deploy com Parâmetros Customizados

```bash
sam deploy --parameter-overrides Environment=staging
```

Sobrescreve parâmetros do template.

### 2.5 Build + Deploy em um Comando

```bash
sam build && sam deploy
```

Ou:
```bash
sam build --use-container && sam deploy --no-confirm-changeset
```

## 3. Execução Local

### 3.1 Rodar API Localmente

```bash
sam local start-api
```

**O que acontece:**
- Inicia servidor local na porta 3000
- Simula API Gateway
- Roda Lambda em container Docker
- Hot reload habilitado (`warm_containers = EAGER`)

**Saída:**
```
Mounting TodoApiFunction at http://127.0.0.1:3000/ [X-AMAZON-APIGATEWAY-ANY-METHOD]
Mounting TodoApiFunction at http://127.0.0.1:3000/{proxy+} [X-AMAZON-APIGATEWAY-ANY-METHOD]
You can now browse to the above endpoints to invoke your functions.
```

**Testar:**
```bash
curl http://localhost:3000/health
```

### 3.2 Rodar API com Variáveis de Ambiente

Crie arquivo `env.json`:
```json
{
  "TodoApiFunction": {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "DB_NAME": "todo_advogados",
    "DB_USER": "postgres",
    "DB_PASSWORD": "senha",
    "JWT_SECRET": "secret",
    "SECRET_KEY": "key",
    "ENVIRONMENT": "local"
  }
}
```

Execute:
```bash
sam local start-api --env-vars env.json
```

### 3.3 Invocar Lambda Diretamente

```bash
sam local invoke TodoApiFunction --event events/health.json
```

Crie `events/health.json`:
```json
{
  "version": "2.0",
  "routeKey": "GET /health",
  "rawPath": "/health",
  "requestContext": {
    "http": {
      "method": "GET",
      "path": "/health"
    }
  }
}
```

### 3.4 Debug Local

```bash
sam local start-api --debug
```

Mostra logs detalhados de execução.

### 3.5 Porta Customizada

```bash
sam local start-api --port 8080
```

API estará em `http://localhost:8080`

## 4. Testes

### 4.1 Teste Manual com curl

**Health Check:**
```bash
curl http://localhost:3000/health
```

**Registrar Usuário:**
```bash
curl -X POST http://localhost:3000/usuarios \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Teste",
    "email": "teste@example.com",
    "senha": "senha123"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:3000/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@example.com",
    "senha": "senha123"
  }'
```

Salve o token retornado.

**Criar Tarefa:**
```bash
TOKEN="seu-token-aqui"

curl -X POST http://localhost:3000/tarefas \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "titulo": "Tarefa teste",
    "descricao": "Descrição",
    "status": "pendente"
  }'
```

**Listar Tarefas:**
```bash
curl http://localhost:3000/tarefas \
  -H "Authorization: Bearer $TOKEN"
```

### 4.2 Teste com Postman/Insomnia

Importe esta collection:

```json
{
  "info": {
    "name": "Todo Advogados API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/health"
      }
    },
    {
      "name": "Registrar",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/usuarios",
        "body": {
          "mode": "raw",
          "raw": "{\n  \"nome\": \"João\",\n  \"email\": \"joao@example.com\",\n  \"senha\": \"senha123\"\n}"
        }
      }
    },
    {
      "name": "Login",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/login",
        "body": {
          "mode": "raw",
          "raw": "{\n  \"email\": \"joao@example.com\",\n  \"senha\": \"senha123\"\n}"
        }
      }
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:3000"
    },
    {
      "key": "token",
      "value": ""
    }
  ]
}
```

### 4.3 Testes Automatizados (futuro)

Estrutura recomendada:
```
tests/
├── unit/
│   ├── test_usuario_service.py
│   └── test_tarefa_service.py
├── integration/
│   ├── test_usuario_routes.py
│   └── test_tarefa_routes.py
└── conftest.py
```

Executar com pytest:
```bash
pytest tests/
```

## 5. Logs

### 5.1 Logs da Lambda (CloudWatch)

**Tail em tempo real:**
```bash
aws logs tail /aws/lambda/todo-advogados-mvp-api --follow
```

**Últimas 100 linhas:**
```bash
aws logs tail /aws/lambda/todo-advogados-mvp-api --since 1h
```

**Filtrar por erro:**
```bash
aws logs tail /aws/lambda/todo-advogados-mvp-api --filter-pattern "ERROR"
```

**Filtrar por request ID:**
```bash
aws logs tail /aws/lambda/todo-advogados-mvp-api --filter-pattern "request-id-123"
```

**Logs de um período específico:**
```bash
aws logs filter-log-events \
  --log-group-name /aws/lambda/todo-advogados-mvp-api \
  --start-time $(date -d '1 hour ago' +%s)000 \
  --filter-pattern "ERROR"
```

### 5.2 Logs do API Gateway

```bash
aws logs tail /aws/apigateway/todo-advogados-mvp --follow
```

### 5.3 Logs Locais (SAM)

Quando roda `sam local start-api`, os logs aparecem no terminal:

```
START RequestId: 52fdfc07-2182-154f-163f-5f0f9a621d72 Version: $LATEST
[INFO]  2024-01-15T10:30:00.123Z  Request received
[INFO]  2024-01-15T10:30:00.456Z  Database session created
[INFO]  2024-01-15T10:30:00.789Z  Query executed successfully
END RequestId: 52fdfc07-2182-154f-163f-5f0f9a621d72
REPORT RequestId: 52fdfc07-2182-154f-163f-5f0f9a621d72  Duration: 234.56 ms
```

### 5.4 Buscar Logs por Correlation ID

```bash
aws logs filter-log-events \
  --log-group-name /aws/lambda/todo-advogados-mvp-api \
  --filter-pattern "correlation_id=abc123"
```

## 6. Métricas e Monitoramento

### 6.1 Métricas da Lambda

**Invocações:**
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=todo-advogados-mvp-api \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

**Duração:**
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=todo-advogados-mvp-api \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average,Maximum
```

**Erros:**
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=todo-advogados-mvp-api \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

**Throttles:**
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Throttles \
  --dimensions Name=FunctionName,Value=todo-advogados-mvp-api \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

### 6.2 Métricas do API Gateway

**Requisições:**
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name Count \
  --dimensions Name=ApiId,Value=<api-id> \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

**Latência:**
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name Latency \
  --dimensions Name=ApiId,Value=<api-id> \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average,Maximum
```

**Erros 4xx:**
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name 4XXError \
  --dimensions Name=ApiId,Value=<api-id> \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

**Erros 5xx:**
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name 5XXError \
  --dimensions Name=ApiId,Value=<api-id> \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

## 7. Informações do Stack

### 7.1 Outputs do CloudFormation

```bash
aws cloudformation describe-stacks \
  --stack-name todo-advogados-mvp \
  --query 'Stacks[0].Outputs'
```

**Retorna:**
- `ApiUrl`: URL completa da API
- `ApiFqdn`: FQDN do API Gateway
- `LambdaFunctionArn`: ARN da Lambda
- `LambdaFunctionName`: Nome da Lambda
- `LambdaRoleArn`: ARN da IAM Role
- `AvailableRoutes`: Lista de rotas disponíveis

### 7.2 URL da API

```bash
aws cloudformation describe-stacks \
  --stack-name todo-advogados-mvp \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text
```

### 7.3 Nome da Lambda

```bash
aws cloudformation describe-stacks \
  --stack-name todo-advogados-mvp \
  --query 'Stacks[0].Outputs[?OutputKey==`LambdaFunctionName`].OutputValue' \
  --output text
```

### 7.4 Recursos do Stack

```bash
aws cloudformation list-stack-resources \
  --stack-name todo-advogados-mvp
```

## 8. Informações da Lambda

### 8.1 Configuração da Lambda

```bash
aws lambda get-function-configuration \
  --function-name todo-advogados-mvp-api
```

**Retorna:**
- Runtime
- Handler
- Timeout
- MemorySize
- Environment variables
- IAM Role
- Last modified

### 8.2 Código da Lambda

```bash
aws lambda get-function \
  --function-name todo-advogados-mvp-api
```

Retorna URL para download do código.

### 8.3 Invocar Lambda Remotamente

```bash
aws lambda invoke \
  --function-name todo-advogados-mvp-api \
  --payload '{"version":"2.0","routeKey":"GET /health","rawPath":"/health"}' \
  response.json

cat response.json
```

### 8.4 Variáveis de Ambiente

```bash
aws lambda get-function-configuration \
  --function-name todo-advogados-mvp-api \
  --query 'Environment.Variables'
```

## 9. Informações do RDS

### 9.1 Endpoint do Banco

```bash
aws ssm get-parameter \
  --name /todo-advogados/dev/db-host \
  --query 'Parameter.Value' \
  --output text
```

### 9.2 Credenciais (com decryption)

```bash
aws ssm get-parameter \
  --name /todo-advogados/dev/db-password \
  --with-decryption \
  --query 'Parameter.Value' \
  --output text
```

### 9.3 Todos os Parâmetros

```bash
aws ssm get-parameters-by-path \
  --path /todo-advogados/dev/ \
  --recursive
```

### 9.4 Status do RDS

```bash
aws rds describe-db-instances \
  --query 'DBInstances[?DBInstanceIdentifier==`todo-advogados-db`]'
```

### 9.5 Conectar no Banco

```bash
# Pegar credenciais
DB_HOST=$(aws ssm get-parameter --name /todo-advogados/dev/db-host --query 'Parameter.Value' --output text)
DB_PASSWORD=$(aws ssm get-parameter --name /todo-advogados/dev/db-password --with-decryption --query 'Parameter.Value' --output text)

# Conectar
psql -h $DB_HOST -U postgres -d todo_advogados -p 5432
```

## 10. Sync (Deploy Rápido)

### 10.1 Sync com Watch

```bash
sam sync --watch
```

**O que faz:**
- Monitora mudanças no código
- Faz deploy automático quando detecta mudança
- Muito mais rápido que `sam deploy`
- Ideal para desenvolvimento

**Saída:**
```
Syncing Lambda Function TodoApiFunction...
Manifest is not changed for (TodoApiFunction), running incremental build
Building codeuri: src/ runtime: python3.12
Sync flow completed successfully
```

### 10.2 Sync sem Watch

```bash
sam sync
```

Faz sync uma vez e para.

## 11. Deletar Stack

### 11.1 Deletar via SAM

```bash
sam delete
```

Deleta stack completo (Lambda, API Gateway, Log Groups).

### 11.2 Deletar via CloudFormation

```bash
aws cloudformation delete-stack --stack-name todo-advogados-mvp
```

### 11.3 Verificar Deleção

```bash
aws cloudformation describe-stacks --stack-name todo-advogados-mvp
```

Se retornar erro, stack foi deletado.

## 12. Troubleshooting

### 12.1 Build Falha

**Erro:** `Unable to import module 'app'`

**Solução:**
```bash
sam build --use-container
```

### 12.2 Deploy Falha

**Erro:** `Stack already exists`

**Solução:**
```bash
sam deploy --no-confirm-changeset
```

Ou delete e recrie:
```bash
sam delete
sam deploy --guided
```

### 12.3 Lambda Timeout

**Erro:** `Task timed out after 30.00 seconds`

**Solução:** Aumentar timeout no `template.yaml`:
```yaml
Timeout: 60
```

### 12.4 Memória Insuficiente

**Erro:** `Runtime exited with error: signal: killed`

**Solução:** Aumentar memória no `template.yaml`:
```yaml
MemorySize: 1024
```

### 12.5 Erro de Conexão com RDS

**Erro:** `could not connect to server`

**Verificar:**
```bash
# Security Group
aws ec2 describe-security-groups --group-ids <sg-id>

# Lambda VPC
aws lambda get-function-configuration \
  --function-name todo-advogados-mvp-api \
  --query 'VpcConfig'

# RDS Endpoint
aws ssm get-parameter --name /todo-advogados/dev/db-host
```

## 13. Comandos Úteis

### 13.1 Listar Stacks

```bash
aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE
```

### 13.2 Listar Lambdas

```bash
aws lambda list-functions --query 'Functions[*].[FunctionName,Runtime,LastModified]'
```

### 13.3 Listar APIs

```bash
aws apigatewayv2 get-apis
```

### 13.4 Listar Log Groups

```bash
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/todo
```

### 13.5 Tamanho do Código

```bash
aws lambda get-function \
  --function-name todo-advogados-mvp-api \
  --query 'Configuration.CodeSize'
```

### 13.6 Última Modificação

```bash
aws lambda get-function-configuration \
  --function-name todo-advogados-mvp-api \
  --query 'LastModified'
```

## 14. Workflow Completo

### Desenvolvimento Local

```bash
# 1. Fazer alterações no código
vim src/routes/tarefa_routes.py

# 2. Testar localmente
sam local start-api

# 3. Testar endpoint
curl http://localhost:3000/tarefas

# 4. Ver logs no terminal
```

### Deploy para Dev

```bash
# 1. Build
sam build --use-container

# 2. Deploy
sam deploy

# 3. Pegar URL
aws cloudformation describe-stacks \
  --stack-name todo-advogados-mvp \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text

# 4. Testar
curl https://sua-api.execute-api.us-east-1.amazonaws.com/dev/health

# 5. Ver logs
aws logs tail /aws/lambda/todo-advogados-mvp-api --follow
```

### Deploy Rápido (Sync)

```bash
# 1. Ativar watch mode
sam sync --watch

# 2. Fazer alterações no código
# Deploy automático acontece

# 3. Testar
curl https://sua-api.../health
```

## 15. Aliases e Scripts Úteis

Adicione ao `.bashrc` ou `.zshrc`:

```bash
# SAM
alias sb='sam build --use-container'
alias sd='sam deploy --no-confirm-changeset'
alias sbd='sam build --use-container && sam deploy --no-confirm-changeset'
alias sl='sam local start-api'
alias ss='sam sync --watch'

# Logs
alias logs-lambda='aws logs tail /aws/lambda/todo-advogados-mvp-api --follow'
alias logs-api='aws logs tail /aws/apigateway/todo-advogados-mvp --follow'

# Info
alias api-url='aws cloudformation describe-stacks --stack-name todo-advogados-mvp --query "Stacks[0].Outputs[?OutputKey==\`ApiUrl\`].OutputValue" --output text'
alias lambda-name='aws cloudformation describe-stacks --stack-name todo-advogados-mvp --query "Stacks[0].Outputs[?OutputKey==\`LambdaFunctionName\`].OutputValue" --output text'
```

Uso:
```bash
sbd  # Build e deploy
logs-lambda  # Ver logs
api-url  # Pegar URL da API
```

Tudo que você precisa para desenvolver, testar e monitorar a aplicação.
