"""
Routes package - Import all routers
"""

from .health import router as health_router
from .usuario_routes import router as usuario_router
from .tarefa_routes import router as tarefa_router

__all__ = ["health_router", "usuario_router", "tarefa_router"]
