from sqlalchemy.orm import Session
from aws_lambda_powertools import Logger
from models import Usuario
from schemas import UsuarioCreate, UsuarioResponse
from utils.auth import hash_password, verify_password, create_access_token
from utils.exceptions import ConflictException, UnauthorizedException, NotFoundException

logger = Logger(child=True)


class UsuarioService:
    @staticmethod
    def create_usuario(db: Session, data: UsuarioCreate) -> UsuarioResponse:
        # Check if email already exists
        existing = db.query(Usuario).filter(Usuario.email == data.email).first()
        if existing:
            logger.warning(f"Email already exists: {data.email}")
            raise ConflictException("Email já cadastrado")

        # Hash password
        senha_hash = hash_password(data.senha)

        # Create usuario
        usuario = Usuario(nome=data.nome, email=data.email, senha_hash=senha_hash)

        db.add(usuario)
        db.flush()  # Get ID without committing

        logger.info(f"Usuario created: {usuario.id}")
        return UsuarioResponse.model_validate(usuario)

    @staticmethod
    def authenticate(
        db: Session, email: str, senha: str
    ) -> tuple[UsuarioResponse, str]:
        # Find usuario by email
        usuario = db.query(Usuario).filter(Usuario.email == email).first()

        if not usuario:
            logger.warning(f"Login failed: email not found - {email}")
            raise UnauthorizedException("Email ou senha inválidos")

        # Verify password
        if not verify_password(senha, usuario.senha_hash):
            logger.warning(f"Login failed: invalid password - {email}")
            raise UnauthorizedException("Email ou senha inválidos")

        # Generate token
        access_token = create_access_token(usuario.id, usuario.email)

        logger.info(f"Usuario authenticated: {usuario.id}")
        return UsuarioResponse.model_validate(usuario), access_token

    @staticmethod
    def get_usuario_by_id(db: Session, usuario_id: str) -> UsuarioResponse:
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

        if not usuario:
            logger.warning(f"Usuario not found: {usuario_id}")
            raise NotFoundException("Usuário não encontrado")

        return UsuarioResponse.model_validate(usuario)
