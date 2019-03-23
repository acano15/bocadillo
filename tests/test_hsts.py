from bocadillo.testing import create_client


def test_if_hsts_enabled_and_request_is_on_http_then_redirects_to_https(app):
    app.configure(hsts=True)

    @app.route("/")
    async def index(req, res):
        pass

    client = create_client(app)
    response = client.get("/", allow_redirects=False)
    assert response.status_code == 301
    assert response.headers["location"] == "https://testserver/"
