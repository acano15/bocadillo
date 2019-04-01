import pytest

from bocadillo import view
from bocadillo.config import SettingsError
from bocadillo.testing import create_client
from bocadillo.utils import override_env


def test_sessions_enabled_no_secret_key(raw_app):
    with pytest.raises(SettingsError):
        raw_app.configure(sessions=True)


@pytest.mark.parametrize("from_env", (True, False))
def test_sessions_enabled_secret_key_empty(raw_app, from_env):
    if from_env:
        with override_env("SECRET_KEY", ""):
            with pytest.raises(SettingsError):
                raw_app.configure(sessions=True)
    else:
        with pytest.raises(SettingsError):
            raw_app.configure(sessions={"secret_key": ""})


@pytest.mark.parametrize("from_env", (True, False))
def test_sessions_enabled_secret_key_present(raw_app, from_env):
    if from_env:
        with override_env("SECRET_KEY", "not-so-secret"):
            app = raw_app.configure(sessions=True)
    else:
        app = raw_app.configure(sessions={"secret_key": "not-so-secret"})

    @app.route("/set")
    @view(methods=["post"])
    async def set_session(req, res):
        req.session["data"] = "something"
        res.text = "Saved"

    @app.route("/")
    async def index(req, res):
        data = req.session["data"]
        res.text = f"Hello {data}"

    client = create_client(app)
    client.post("/set")
    response = client.get("/")
    assert "something" in response.text
    assert "session" in response.cookies
