"""
Custom JSON Serializer for datetime objects
"""

import json
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID
from enum import Enum


def custom_serializer(obj):
    """
    Custom JSON serializer for objects not serializable by default json code
    """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, UUID):
        return str(obj)
    elif isinstance(obj, Enum):
        return obj.value
    elif hasattr(obj, "model_dump"):
        # Pydantic v2
        return obj.model_dump(mode="json")
    elif hasattr(obj, "dict"):
        # Pydantic v1
        return obj.dict()

    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def json_dumps(obj):
    """
    Custom JSON dumps with UTF-8 support
    """
    return json.dumps(obj, default=custom_serializer, ensure_ascii=False)
