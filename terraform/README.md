# Terraform - RDS Infrastructure

## 📋 Pré-requisitos

- Terraform >= 1.0
- AWS CLI configurado
- Credenciais AWS com permissões para criar RDS, Security Groups, SSM

## 🚀 Deploy

### 1. Gerar secrets

```bash
# Gerar secrets fortes
export TF_VAR_db_password="senha aqui"
export TF_VAR_jwt_secret_key=$(openssl rand -base64 32)
export TF_VAR_secret_key=$(openssl rand -base64 32)

# Verificar
echo $TF_VAR_db_password
echo $TF_VAR_jwt_secret_key
echo $TF_VAR_secret_key

# Salvar em arquivo seguro (opcional)
echo "DB_PASSWORD=$TF_VAR_db_password" > .env
echo "JWT_SECRET=$TF_VAR_jwt_secret_key" >> .env
echo "SECRET_KEY=$TF_VAR_secret_key" >> .env
chmod 600 .env
```
