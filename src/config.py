"""
Configuration - Load secrets from SSM Parameter Store
"""

import os
import boto3
from functools import lru_cache
from aws_lambda_powertools import Logger

logger = Logger(child=True)

ssm = boto3.client("ssm")


@lru_cache(maxsize=128)
def get_ssm_parameter(parameter_name: str, with_decryption: bool = True) -> str:
    """
    Get parameter from SSM Parameter Store with caching

    Args:
        parameter_name: SSM parameter name
        with_decryption: Decrypt SecureString parameters

    Returns:
        Parameter value
    """
    try:
        logger.info(f"Fetching SSM parameter: {parameter_name}")
        response = ssm.get_parameter(
            Name=parameter_name, WithDecryption=with_decryption
        )
        return response["Parameter"]["Value"]
    except Exception as e:
        logger.error(f"Error fetching SSM parameter {parameter_name}: {str(e)}")
        raise


class Config:
    """Application configuration"""

    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")

    # Database configuration (from SSM)
    @property
    def DB_HOST(self) -> str:
        return get_ssm_parameter(os.getenv("SSM_DB_HOST"))

    @property
    def DB_PORT(self) -> str:
        return get_ssm_parameter(os.getenv("SSM_DB_PORT"))

    @property
    def DB_NAME(self) -> str:
        return get_ssm_parameter(os.getenv("SSM_DB_NAME"))

    @property
    def DB_USER(self) -> str:
        return get_ssm_parameter(os.getenv("SSM_DB_USER"))

    @property
    def DB_PASSWORD(self) -> str:
        return get_ssm_parameter(os.getenv("SSM_DB_PASSWORD"), with_decryption=True)

    # Application secrets (from SSM)
    @property
    def JWT_SECRET_KEY(self) -> str:
        return get_ssm_parameter(os.getenv("SSM_JWT_SECRET"), with_decryption=True)

    @property
    def SECRET_KEY(self) -> str:
        return get_ssm_parameter(os.getenv("SSM_SECRET_KEY"), with_decryption=True)

    # Database URL
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # JWT Configuration
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = 24


# Singleton instance
config = Config()
