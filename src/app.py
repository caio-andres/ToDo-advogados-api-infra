"""
Todo Advogados API - Lambda Handler
Entry point - Registers all routes
"""

import json
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver, Response
from aws_lambda_powertools.logging import correlation_paths

# Database initialization
from database import init_db

# Import routers
from routes.health import router as health_router
from routes.usuario_routes import router as usuario_router
from routes.tarefa_routes import router as tarefa_router

from utils.json_serializer import json_dumps

logger = Logger()
tracer = Tracer(disabled=True)

# Create main app with custom serializer
app = APIGatewayHttpResolver(serializer=json_dumps)

try:
    init_db()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {str(e)}")


# Register Routers
app.include_router(health_router)
app.include_router(usuario_router)
app.include_router(tarefa_router)
# Not Found
@app.route(".*", method=["GET", "POST", "PUT", "DELETE", "PATCH"])
def handle_not_found():
    # Retorna status 404 e mensagem de erro personalizada
    return Response(
        status_code=404,
        content_type="application/json",
        body={"message": "Rota não encontrada", "path": app.current_event.path},
    )


# Lambda Handler
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_HTTP)
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    """
    Lambda handler - Entry point for all requests
    """
    logger.info(
        "Request received",
        extra={
            "path": event.get("rawPath"),
            "method": event.get("requestContext", {}).get("http", {}).get("method"),
            "source_ip": event.get("requestContext", {})
            .get("http", {})
            .get("sourceIp"),
        },
    )

    try:
        return app.resolve(event, context)
    except Exception as e:
        logger.exception("Unhandled exception in lambda_handler")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json; charset=utf-8"},
            "body": json_dumps(
                {"message": "Erro interno do servidor", "error": str(e)}
            ),
        }
