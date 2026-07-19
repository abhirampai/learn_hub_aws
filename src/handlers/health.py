import json
from pathlib import Path


VERSION_FILE = Path(__file__).resolve().parent.parent / "VERSION"


def read_version():
    return VERSION_FILE.read_text(encoding="utf-8").strip()


def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(
            {
                "status": "ok",
                "service": "Learn Hub",
                "version": read_version(),
            }
        ),
    }
