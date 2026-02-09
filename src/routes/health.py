"""
Health Check Routes
"""

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler.api_gateway import Router
from database import get_db
from models import Usuario

logger = Logger(child=True)
tracer = Tracer(disabled=True)

# Create router
router = Router()


@router.get("/")
@tracer.capture_method
def root():
    logger.info("Root endpoint called - Informações da API")
    return {
        "api": "todo-advogados-api",
        "message": "API is running",
        "endpoints": {
            "health": "GET /health",
            "usuarios": "POST /usuarios",
            "login": "POST /login",
            "me": "GET /usuarios/me",
            "tarefas": "GET /tarefas, POST /tarefas",
            "tarefa": "GET /tarefas/{id}, PUT /tarefas/{id}, DELETE /tarefas/{id}",
        },
    }


@router.get("/health")
@tracer.capture_method
def health_check():
    logger.info("Health check called")

    try:
        with get_db() as db:
            db.query(Usuario).first()

        return {
            "status": "healthy",
            "api": "todo-advogados-api",
            "database": {"connected": True},
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "api": "todo-advogados-api",
            "database": {"connected": False, "error": str(e)},
        }
