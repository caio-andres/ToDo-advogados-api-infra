"""
Health Check Routes
"""

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler.api_gateway import Router
from database import get_db

logger = Logger(child=True)
tracer = Tracer(disabled=True)

# Create router
router = Router()


@router.get("/")
@tracer.capture_method
def root():
    """Root endpoint - Health check"""
    logger.info("Root endpoint called")
    return {
        "status": "healthy",
        "service": "todo-advogados-api",
        "version": "1.0.0",
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
    """Health check endpoint with database connection test"""
    logger.info("Health check called")

    try:
        # Test database connection
        with get_db() as db:
            from models import Usuario

            db.query(Usuario).first()

        return {
            "status": "healthy",
            "service": "todo-advogados-api",
            "version": "1.0.0",
            "database": {"connected": True},
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "todo-advogados-api",
            "version": "1.0.0",
            "database": {"connected": False, "error": str(e)},
        }
