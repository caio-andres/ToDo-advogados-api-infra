"""
Tarefa Routes
"""

from aws_lambda_powertools.event_handler import ApiGatewayResolver
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler.api_gateway import Router
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
    UnauthorizedError,
    NotFoundError,
    InternalServerError,
)
from pydantic import ValidationError

from database import get_db
from schemas import TarefaCreate, TarefaUpdate
from services import TarefaService
from utils.auth import get_current_user_id
from utils.exceptions import (
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
)
from models.tarefa import StatusTarefa

logger = Logger(child=True)
tracer = Tracer(disabled=True)

# Create router
router = Router()


def parse_json_body(schema_class):
    """Parse e valida o JSON body utilizando Pydantic schema"""

    try:
        body = ApiGatewayResolver.current_event.json_body
        return schema_class(**body)
    except ValidationError as e:
        logger.warning(f"Validation error: {e.errors()}")
        raise BadRequestError(f"Erro de validação: {e.errors()}")
    except Exception as e:
        logger.error(f"Error parsing body: {str(e)}")
        raise BadRequestError("Corpo da requisição inválido")


@router.post("/tarefas")
@tracer.capture_method
def create_tarefa():
    logger.info("Creating new tarefa")

    try:
        auth_header = ApiGatewayResolver.current_event.get_header_value("Authorization")
        usuario_id = get_current_user_id(auth_header)

        data = parse_json_body(TarefaCreate)

        with get_db() as db:
            tarefa = TarefaService.create_tarefa(db, data, usuario_id)

        return {
            "message": "Tarefa criada com sucesso",
            "data": tarefa,
        }, 201

    except UnauthorizedException as e:
        raise UnauthorizedError(e.message)
    except Exception as e:
        logger.exception("Error creating tarefa")
        raise InternalServerError(f"Erro ao criar tarefa: {str(e)}")


@router.get("/tarefas")
@tracer.capture_method
def list_tarefas():
    logger.info("Listing tarefas")

    try:
        auth_header = ApiGatewayResolver.current_event.get_header_value("Authorization")
        usuario_id = get_current_user_id(auth_header)

        query_params = ApiGatewayResolver.current_event.query_string_parameters or {}
        status_str = query_params.get("status")
        limit = int(query_params.get("limit", 100))
        offset = int(query_params.get("offset", 0))

        status = None
        if status_str:
            try:
                status = StatusTarefa(status_str)
            except ValueError:
                raise BadRequestError(f"Status inválido: {status_str}")

        with get_db() as db:
            tarefas = TarefaService.list_tarefas(
                db, usuario_id, status=status, limit=limit, offset=offset
            )

        return {
            "data": [t for t in tarefas],
            "count": len(tarefas),
            "limit": limit,
            "offset": offset,
        }

    except UnauthorizedException as e:
        raise UnauthorizedError(e.message)
    except Exception as e:
        logger.exception("Error listing tarefas")
        raise InternalServerError(f"Erro ao listar tarefas: {str(e)}")


@router.get("/tarefas/<id>")
@tracer.capture_method
def get_tarefa(id: str):
    """Get tarefa by ID"""

    logger.info(f"Getting tarefa: {id}")

    try:
        auth_header = ApiGatewayResolver.current_event.get_header_value("Authorization")
        usuario_id = get_current_user_id(auth_header)

        with get_db() as db:
            tarefa = TarefaService.get_tarefa_by_id(db, id, usuario_id)

        return {"data": tarefa}

    except UnauthorizedException as e:
        raise UnauthorizedError(e.message)
    except ForbiddenException as e:
        raise UnauthorizedError(e.message)
    except NotFoundException as e:
        raise NotFoundError(e.message)
    except Exception as e:
        logger.exception("Error getting tarefa")
        raise InternalServerError(f"Erro ao buscar tarefa: {str(e)}")


@router.put("/tarefas/<id>")
@tracer.capture_method
def update_tarefa(id: str):
    logger.info(f"Updating tarefa: {id}")

    try:
        auth_header = ApiGatewayResolver.current_event.get_header_value("Authorization")
        usuario_id = get_current_user_id(auth_header)

        data = parse_json_body(TarefaUpdate)

        with get_db() as db:
            tarefa = TarefaService.update_tarefa(db, id, data, usuario_id)

        return {"message": "Tarefa atualizada com sucesso", "data": tarefa}

    except UnauthorizedException as e:
        raise UnauthorizedError(e.message)
    except ForbiddenException as e:
        raise UnauthorizedError(e.message)
    except NotFoundException as e:
        raise NotFoundError(e.message)
    except Exception as e:
        logger.exception("Error updating tarefa")
        raise InternalServerError(f"Erro ao atualizar tarefa: {str(e)}")


@router.delete("/tarefas/<id>")
@tracer.capture_method
def delete_tarefa(id: str):
    logger.info(f"Deleting tarefa: {id}")

    try:
        auth_header = ApiGatewayResolver.current_event.get_header_value("Authorization")
        usuario_id = get_current_user_id(auth_header)

        with get_db() as db:
            TarefaService.delete_tarefa(db, id, usuario_id)

        return {"message": "Tarefa deletada com sucesso"}

    except UnauthorizedException as e:
        raise UnauthorizedError(e.message)
    except ForbiddenException as e:
        raise UnauthorizedError(e.message)
    except NotFoundException as e:
        raise NotFoundError(e.message)
    except Exception as e:
        logger.exception("Error deleting tarefa")
        raise InternalServerError(f"Erro ao deletar tarefa: {str(e)}")
