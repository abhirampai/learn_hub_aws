import json


def success(status_code=200, message=json.dumps({"message": "Operation successfull"})):
    return {
        "statusCode": status_code,
        "body": message,
        "headers": {"Content-Type": "application/json"},
    }


def error(
    status_code=404, error_code="INVALID_JSON", message="Something went wrong, Please try later"
):
    return {
        "statusCode": status_code,
        "body": json.dumps({"error": {"code": error_code, "message": message}}),
        "headers": {"Content-Type": "application/json"},
    }


def validation_error(error_value, field, validation_type="INVALID_VALUE"):
    match validation_type:
        case "INVALID_VALUE":
            return {
                "valid": False,
                "error_message": f"validation failed '{error_value}' not a valid value for {field}",
            }
