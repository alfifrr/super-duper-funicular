from typing import Any, Dict, Optional
from flask import jsonify


def api_response(
    message: str,
    status_code: int,
    data: Optional[Dict[str, Any]] = None,
    errors: Optional[Dict[str, Any]] = None
):
    response = {
        "message": message,
        "status": "success" if 200 <= status_code < 300 else "error"
    }

    if data is not None:
        response["data"] = data
    if errors is not None:
        response["errors"] = errors

    return jsonify(response), status_code
