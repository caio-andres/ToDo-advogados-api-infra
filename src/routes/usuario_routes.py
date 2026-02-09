"""
Usuario Routes
"""

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import ApiGatewayResolver
from aws_lambda_powertools.event_handler.api_gateway import Router
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
    UnauthorizedError,
    NotFoundError,
    InternalServerError,
)
from pydantic import ValidationError

from database import get_db
from schemas import UsuarioCreate, UsuarioLogin
from services import UsuarioService
from utils.auth import get_current_user_id
from utils.exceptions import UnauthorizedException, NotFoundException, ConflictException


logger = Logger(child=True)
tracer = Tracer(disabled=True)

router = Router()


def parse_json_body(schema_class):
    """Parse and validate JSON body using Pydantic schema"""

    try:
        body = ApiGatewayResolver.current_event.json_body
        return schema_class(**body)
    except ValidationError as e:
        logger.warning(f"Validation error: {e.errors()}")
        raise BadRequestError(f"Erro de validação: {e.errors()}")
    except Exception as e:
        logger.error(f"Error parsing body: {str(e)}")
        raise BadRequestError("Corpo da requisição inválido")


@router.post("/usuarios")
@tracer.capture_method
def create_usuario():
    logger.info("Creating new usuario")

    data = parse_json_body(UsuarioCreate)

    try:
        with get_db() as db:
            usuario = UsuarioService.create_usuario(db, data)

        return {
            "message": "Usuário criado com sucesso",
            "data": usuario,
        }, 201

    except ConflictException as e:
        raise BadRequestError(e.message)
    except Exception as e:
        logger.exception("Error creating usuario")
        raise InternalServerError(f"Erro ao criar usuário: {str(e)}")


@router.post("/login")
@tracer.capture_method
def login():
    logger.info("Usuario login attempt")

    data = parse_json_body(UsuarioLogin)

    try:
        with get_db() as db:
            usuario, access_token = UsuarioService.authenticate(
                db, data.email, data.senha
            )

        return {
            "message": "Login realizado com sucesso",
            "data": {
                "usuario": usuario,
                "access_token": access_token,
                "token_type": "Bearer",
            },
        }

    except UnauthorizedException as e:
        raise UnauthorizedError(e.message)
    except Exception as e:
        logger.exception("Error during login")
        raise InternalServerError(f"Erro ao realizar login: {str(e)}")


@router.get("/usuarios/me")
@tracer.capture_method
def get_current_usuario():
    """Get current authenticated usuario"""

    logger.info("Getting current usuario")

    try:
        auth_header = ApiGatewayResolver.current_event.get_header_value("Authorization")
        usuario_id = get_current_user_id(auth_header)

        with get_db() as db:
            usuario = UsuarioService.get_usuario_by_id(db, usuario_id)

        return {"data": usuario}

    except UnauthorizedException as e:
        raise UnauthorizedError(e.message)
    except NotFoundException as e:
        raise NotFoundError(e.message)
    except Exception as e:
        logger.exception("Error getting current usuario")
        raise InternalServerError(f"Erro ao buscar usuário: {str(e)}")
