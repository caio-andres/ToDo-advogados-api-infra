# Todo Advogados MVP

### Excalidraw workspace

https://link.excalidraw.com/l/92vNxGmOx1N/93m5jsFp710

### Atual

Permite **advogados** criarem, listarem, modificarem e deletarem **tarefas**.

### Futuro

Permite **advogados** criarem, listarem, modificarem e deletarem **tarefas** em **boards** específicos.

## 🏗️ Arquitetura

- **Backend:** AWS Lambda (Python 3.12)
- **API:** API Gateway HTTP API (v2)
- **Database:** RDS PostgreSQL 15.14
- **IaC:** SAM (Lambda/API) + Terraform (RDS)
- **Auth:** JWT + bcrypt
- **Logs:** CloudWatch + Powertools

## 🚀 Deploy

### 1. Deploy Terraform (RDS)

```bash
cd terraform

# Gerar secrets
export TF_VAR_db_password="sua senha"
export TF_VAR_jwt_secret_key=$(openssl rand -base64 32)
export TF_VAR_secret_key=$(openssl rand -base64 32)

# Deploy
terraform init
terraform apply
```
