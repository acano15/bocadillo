from typing import Type, Any

import pytest

from bocadillo import HTTPError, WebSocketDisconnect
from bocadillo.testing import create_client
from bocadillo.error_handlers import error_to_media


def setup_http(app, annotation):
    @app.route("/{value}")
    async def index(req, res, value: annotation):
        res.media = {"value": value}


def setup_websocket(app, annotation):
    @app.websocket_route("/{value}")
    async def index(ws, value: annotation):
        await ws.send_json({"value": value})


def get_http_json(client, url) -> dict:
    r = client.get(url)
    assert r.status_code == 200
    return r.json()


def get_websocket_json(client, url) -> dict:
    with client.websocket_connect(url) as ws:
        return ws.receive_json()


@pytest.mark.parametrize(
    "setup, get_json",
    [(setup_http, get_http_json), (setup_websocket, get_websocket_json)],
)
@pytest.mark.parametrize(
    "annotation, string_value, converted_value",
    [
        (int, "42", 42),
        (int, "4.2", 4),
        (float, "4.2", 4.2),
        (bool, "TRUE", True),
        (bool, "true", True),
        (bool, "1", True),
        (bool, "FALSE", False),
        (bool, "false", False),
        (bool, "0", False),
        (str, "foo", "foo"),
    ],
)
def test_convert_route_parameters(
    app,
    client,
    setup,
    get_json,
    annotation: Type,
    string_value: str,
    converted_value: Any,
):
    setup(app, annotation)
    json = get_json(client, f"/{string_value}")
    assert json["value"] == converted_value


def setup_http_error_handler(app):
    app.add_error_handler(HTTPError, error_to_media)


def setup_websocket_error_handler(app):
    pass


def check_http_status(client, url):
    r = client.get(url)
    assert r.status_code == 400
    return r


def check_websocket_status(client, url):
    with client.websocket_connect(url) as ws:
        message = ws.receive()
        assert message["code"] == 403


@pytest.mark.parametrize(
    "setup, setup_error_handler, check_status",
    [
        (setup_http, setup_http_error_handler, check_http_status),
        (
            setup_websocket,
            setup_websocket_error_handler,
            check_websocket_status,
        ),
    ],
)
@pytest.mark.parametrize(
    "annotation, string_value",
    [(int, "a1"), (float, "foo"), (bool, "12"), (bool, "yes"), (bool, "no")],
)
def test_if_invalid_route_parameter_then_error_response(
    app,
    setup,
    setup_error_handler,
    check_status,
    annotation: Type,
    string_value: str,
):
    setup_error_handler(app)
    setup(app, annotation)
    client = create_client(app, raise_server_exceptions=False)
    r = check_status(client, f"/{string_value}")
    if r is not None:
        assert "value" in r.json()["detail"]
