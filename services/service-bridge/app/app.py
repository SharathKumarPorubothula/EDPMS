import json
import os

import requests
from flask import Flask, request, Response, jsonify

app = Flask(__name__)
#this is app
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "bridge_config.json")


def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


@app.route("/<path:route>", methods=[
    "GET",
    "POST",
    "PUT",
    "DELETE",
    "PATCH",
    "OPTIONS"
])
def bridge(route):
    
    """
    Forward incoming HTTP requests to the configured backend service.

    This endpoint performs the following steps:

    1. Loads service mappings from bridge_config.json.
    2. Finds the target service for the requested route.
    3. Constructs the destination URL.
    4. Forwards the incoming request while preserving:
       - HTTP method
       - Headers
       - Query parameters
       - Request body
       - Cookies
    5. Returns the backend service response to the client.

    Args:
        route (str):
            Route extracted from the incoming request URL.

    Returns:
        flask.Response:
            Response received from the target backend service.

    HTTP Responses:
        200-499
            Returns the backend service response.

        404
            Returned when no route mapping exists.

        500
            Returned if the backend service is unreachable
            or another request exception occurs.
    """

    configs = load_config()

    service = None

    for item in configs:
        if route in item:
            service = item[route]
            break

    if service is None:
        return jsonify({
            "status": "error",
            "message": f"No mapping found for '{route}'"
        }), 404

    host = service["HOST"]
    port = service["PORT"]

    target_url = f"http://{host}:{port}/{route}"

    try:

        response = requests.request(
            method=request.method,
            url=target_url,
            headers={
                key: value
                for key, value in request.headers
                if key.lower() != "host"
            },
            params=request.args,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            timeout=30
        )

        excluded_headers = [
            "content-encoding",
            "content-length",
            "transfer-encoding",
            "connection"
        ]

        headers = [
            (name, value)
            for name, value in response.raw.headers.items()
            if name.lower() not in excluded_headers
        ]

        return Response(
            response.content,
            response.status_code,
            headers
        )

    except requests.exceptions.RequestException as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8761
    )
