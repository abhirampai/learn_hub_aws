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


def validation_error(errors):
    return {
        "statusCode": 400,
        "body": json.dumps({"errors": json.loads(errors)}),
        "headers": {"Content-Type": "application/json"},
    }

