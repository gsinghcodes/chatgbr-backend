from datetime import date, datetime
from enum import Enum
from decimal import Decimal
import uuid


def serialize_model(instance):
    def parse_array(value):
        """Converts PostgreSQL array string representation to a Python list"""
        if (
            isinstance(value, list)
            and len(value) == 1
            and isinstance(value[0], str)
            and "," in value[0]
        ):
            return [item.strip().strip('"') for item in value[0].split(",")]
        return value

    def convert_value(value):
        """Handles datetime, UUID, Enums, and PostgreSQL arrays correctly"""
        if isinstance(value, (datetime, date)):
            return value.isoformat()  # ✅ Convert datetime to ISO format
        elif isinstance(value, uuid.UUID):
            return str(value)  # ✅ Convert UUID to string
        elif isinstance(value, Enum):
            return value.value  # ✅ Convert Enum to string
        elif isinstance(value, Decimal):  # 👈 Add this line
            return float(value)
        return parse_array(value)

    if isinstance(instance, dict):
        # Already a dict, just convert values
        return {
            key: convert_value(value)
            for key, value in instance.items()
            if not key.startswith("_")
        }
    elif hasattr(instance, "__dict__"):
        return {
            key: convert_value(value)
            for key, value in instance.__dict__.items()
            if not key.startswith("_")
        }
    else:
        # Fallback: return as-is
        return instance
