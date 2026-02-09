# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "🔍 Testando conexão com RDS..."

# Pegar outputs
RDS_HOST=$(terraform output -raw rds_address 2>/dev/null)
RDS_PORT=$(terraform output -raw rds_port 2>/dev/null)
RDS_DB=$(terraform output -raw rds_database_name 2>/dev/null)
RDS_USER=$(terraform output -raw rds_username 2>/dev/null)

if [ -z "$RDS_HOST" ]; then
    echo -e "${RED}Erro: Não foi possível obter outputs do Terraform${NC}"
    echo "Execute 'terraform apply' primeiro"
    exit 1
fi

echo ""
echo "Informações do RDS:"
echo "  Host: $RDS_HOST"
echo "  Port: $RDS_PORT"
echo "  Database: $RDS_DB"
echo "  User: $RDS_USER"
echo ""

# Verificar se psql está instalado
if ! command -v psql &> /dev/null; then
    echo -e "${RED}psql não está instalado${NC}"
    echo ""
    echo "Instale o PostgreSQL client:"
    echo "  macOS:   brew install postgresql"
    echo "  Ubuntu:  sudo apt-get install postgresql-client"
    echo "  Windows: https://www.postgresql.org/download/windows/"
    exit 1
fi

# Pedir senha
echo "Digite a senha do banco (definida em TF_VAR_db_password):"
read -s DB_PASSWORD

echo ""
echo "Conectando ao RDS..."

# Testar conexão
PGPASSWORD=$DB_PASSWORD psql -h $RDS_HOST -p $RDS_PORT -U $RDS_USER -d $RDS_DB -c "SELECT version();" 2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Conexão bem-sucedida!${NC}"
    echo ""
    echo "Para conectar manualmente:"
    echo "  psql -h $RDS_HOST -p $RDS_PORT -U $RDS_USER -d $RDS_DB"
else
    echo -e "${RED}Falha na conexão${NC}"
    echo ""
    echo "Possíveis causas:"
    echo "  1. Senha incorreta"
    echo "  2. RDS ainda está sendo criado (aguarde ~5 min)"
    echo "  3. Security Group bloqueando seu IP"
    echo "  4. RDS não está publicly_accessible"
    echo ""
    echo "Verifique o status do RDS:"
    echo "  aws rds describe-db-instances --db-instance-identifier todo-advogados-dev-db --query 'DBInstances[0].DBInstanceStatus'"
fi