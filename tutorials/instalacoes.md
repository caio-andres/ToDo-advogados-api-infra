# Como Usar - Guia Completo do Zero

Este guia assume que você acabou de clonar o repositório e vai configurar tudo do zero.

## Pré-requisitos

Antes de começar, instale:

1. **Python 3.12**
   - Windows: https://www.python.org/downloads/
   - Linux: `sudo apt install python3.12`
   - Mac: `brew install python@3.12`

2. **AWS CLI**
   ```bash
   # Windows (PowerShell como admin)
   msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi
   
   # Linux
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip
   sudo ./aws/install
   
   # Mac
   brew install awscli
   ```

3. **SAM CLI**
   ```bash
   # Windows (PowerShell como admin)
   choco install aws-sam-cli
   
   # Linux
   pip install aws-sam-cli
   
   # Mac
   brew install aws-sam-cli
   ```

4. **Terraform**
   ```bash
   # Windows (PowerShell como admin)
   choco install terraform
   
   # Linux
   wget https://releases.hashicorp.com/terraform/1.7.0/terraform_1.7.0_linux_amd64.zip
   unzip terraform_1.7.0_linux_amd64.zip
   sudo mv terraform /usr/local/bin/
   
   # Mac
   brew install terraform
   ```

## Passo 1: Configurar AWS CLI

Configure suas credenciais da AWS:

```bash
aws configure
```

Informe:
- AWS Access Key ID: `sua-access-key`
- AWS Secret Access Key: `sua-secret-key`
- Default region: `us-east-1`
- Default output format: `json`

Teste a configuração:
```bash
aws sts get-caller-identity
```

## Passo 2: Clonar o Repositório

```bash
git clone <url-do-repositorio>
cd ToDo-advogados-api
```

## Passo 3: Deploy da Infraestrutura (Terraform)

### 3.1 Gerar Secrets

```bash
# Linux/Mac
export TF_VAR_db_password="MinhaS3nh@Segur@123"
export TF_VAR_jwt_secret_key=$(openssl rand -base64 32)
export TF_VAR_secret_key=$(openssl rand -base64 32)

# Windows PowerShell
$env:TF_VAR_db_password="MinhaS3nh@Segur@123"
$env:TF_VAR_jwt_secret_key=[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }))
$env:TF_VAR_secret_key=[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }))
```

**IMPORTANTE:** Anote esses valores em um local seguro! Você vai precisar deles.

### 3.2 Inicializar Terraform

```bash
cd terraform
terraform init
```

### 3.3 Revisar o Plano

```bash
terraform plan
```

Isso mostra o que será criado:
- VPC com subnets
- RDS PostgreSQL
- Security Groups
- SSM Parameters

### 3.4 Aplicar

```bash
terraform apply
```

Digite `yes` quando solicitado.

Aguarde ~10-15 minutos (RDS demora para criar).

### 3.5 Verificar Outputs

```bash
terraform output
```

Anote:
- `db_endpoint` - Endpoint do banco
- `db_name` - Nome do banco
- `vpc_id` - ID da VPC

## Passo 4: Deploy da Lambda e API Gateway (SAM)

### 4.1 Voltar para a raiz

```bash
cd ..
```

### 4.2 Build

```bash
sam build
```

Isso instala as dependências Python e prepara o pacote.

### 4.3 Deploy Guiado (primeira vez)

```bash
sam deploy --guided
```

Responda as perguntas:

```
Stack Name [sam-app]: todo-advogados-api
AWS Region [us-east-1]: us-east-1
Parameter Environment [dev]: dev
Confirm changes before deploy [y/N]: y
Allow SAM CLI IAM role creation [Y/n]: Y
Disable rollback [y/N]: N
TodoApiFunction may not have authorization defined, Is this okay? [y/N]: y
Save arguments to configuration file [Y/n]: Y
SAM configuration file [samconfig.toml]: samconfig.toml
SAM configuration environment [default]: default
```

Aguarde ~2-3 minutos.

### 4.4 Pegar a URL da API

```bash
aws cloudformation describe-stacks \
  --stack-name todo-advogados-api \
  --query 'Stacks[0].Outputs[?OutputKey==`TodoApiUrl`].OutputValue' \
  --output text
```

Anote essa URL! Exemplo: `https://abc123.execute-api.us-east-1.amazonaws.com/`