"""
Authentication utilities - JWT + bcrypt
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from aws_lambda_powertools import Logger
from config import config
from utils.exceptions import UnauthorizedException

logger = Logger(child=True)


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password

    Returns:
        True if password matches, False otherwise
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def create_access_token(usuario_id: str, email: str) -> str:
    """
    Create JWT access token

    Args:
        usuario_id: Usuario ID
        email: Usuario email

    Returns:
        JWT token
    """
    payload = {
        "sub": usuario_id,
        "email": email,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=config.JWT_EXPIRATION_HOURS),
    }

    token = jwt.encode(payload, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)

    logger.info(f"Access token created for user {usuario_id}")
    return token


def decode_access_token(token: str) -> dict:
    """
    Decode and verify JWT token

    Args:
        token: JWT token

    Returns:
        Token payload

    Raises:
        UnauthorizedException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        raise UnauthorizedException("Token expirado")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        raise UnauthorizedException("Token inválido")


def get_current_user_id(authorization_header: Optional[str]) -> str:
    """
    Extract user ID from Authorization header

    Args:
        authorization_header: Authorization header value (Bearer <token>)

    Returns:
        User ID

    Raises:
        UnauthorizedException: If token is missing or invalid
    """
    if not authorization_header:
        raise UnauthorizedException("Token não fornecido")

    parts = authorization_header.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedException("Formato de token inválido. Use: Bearer <token>")

    token = parts[1]
    payload = decode_access_token(token)

    return payload["sub"]
