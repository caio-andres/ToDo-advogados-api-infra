"""
Custom exceptions
"""


class AppException(Exception):
    """Base exception for application errors"""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class UnauthorizedException(AppException):
    """Unauthorized exception (401)"""

    def __init__(self, message: str = "Não autorizado"):
        super().__init__(message, status_code=401)


class ForbiddenException(AppException):
    """Forbidden exception (403)"""

    def __init__(self, message: str = "Acesso negado"):
        super().__init__(message, status_code=403)


class NotFoundException(AppException):
    """Not found exception (404)"""

    def __init__(self, message: str = "Recurso não encontrado"):
        super().__init__(message, status_code=404)


class ConflictException(AppException):
    """Conflict exception (409)"""

    def __init__(self, message: str = "Conflito de dados"):
        super().__init__(message, status_code=409)


class ValidationException(AppException):
    """Validation exception (422)"""

    def __init__(self, message: str = "Erro de validação"):
        super().__init__(message, status_code=422)
