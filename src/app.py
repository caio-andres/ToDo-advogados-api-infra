from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver, Response
from aws_lambda_powertools.logging import correlation_paths

from database import init_db

from routes.health import router as health_router
from routes.usuario_routes import router as usuario_router
from routes.tarefa_routes import router as tarefa_router

from utils.json_serializer import json_dumps

logger = Logger()
tracer = Tracer(disabled=True)

app = APIGatewayHttpResolver(serializer=json_dumps)

try:
    init_db()
    logger.info("Database inicializado.")
except Exception as e:
    logger.error(f"Falha ao iniciar database: {str(e)}")


# Register Routers
app.include_router(health_router)
app.include_router(usuario_router)
app.include_router(tarefa_router)


# Lambda Handler
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_HTTP)
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    logger.info(
        f"Request received: {event}",
    )

    try:
        return app.resolve(event, context)
    
    except Exception as e:
        logger.exception("Unhandled exception in lambda_handler")
        return {
            "statusCode": 500,
            "body": json_dumps(
                {"message": "Erro interno do servidor", "error": str(e)}
            ),
        }
