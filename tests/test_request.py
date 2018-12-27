import json
from io import StringIO
import pytest

from bocadillo import API


@pytest.mark.parametrize("data, status", [("{", 400), ("{}", 200)])
def test_parse_json(api: API, data: str, status: int):
    @api.route("/")
    class Index:
        async def post(self, req, res):
            res.media = await req.json()

    assert api.client.post("/", data=data).status_code == status


def test_stream_request(api: API):
    @api.route("/")
    class Index:
        async def get(self, req, res):
            chunks = [chunk.decode() async for chunk in req.stream() if chunk]
            res.media = chunks

    # For testing, we use a chunk-encoded request. See:
    # http://docs.python-requests.org/en/master/user/advanced/#chunk-encoded-requests

    message = "Hello, world!"

    def stream():
        for _ in range(3):
            yield message

    response = api.client.get("/", data=stream())
    assert response.json() == [message] * 3
