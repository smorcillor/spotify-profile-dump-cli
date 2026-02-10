"""OAuth flow for Spotify CLI authentication."""

import secrets
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional

import requests

SCOPES = (
    "user-read-private user-read-email user-library-read "
    "user-follow-read playlist-read-private playlist-read-collaborative"
)

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"


def get_token_via_oauth(client_id: str, client_secret: str, port: int = 8888) -> str:
    """Run local OAuth flow: open browser, handle callback, return access token."""
    redirect_uri = f"http://127.0.0.1:{port}/callback"
    state = secrets.token_urlsafe(16)

    auth_url = _build_auth_url(client_id, redirect_uri, state)

    # Will be set by the callback handler
    result: dict = {}

    class CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)

            if parsed.path != "/callback":
                self.send_response(404)
                self.end_headers()
                return

            error = params.get("error", [None])[0]
            if error:
                result["error"] = error
                self._respond("Authorization denied. You can close this tab.")
                return

            code = params.get("code", [None])[0]
            returned_state = params.get("state", [None])[0]

            if returned_state != state:
                result["error"] = "State mismatch — possible CSRF attack."
                self._respond("State mismatch error. You can close this tab.")
                return

            if not code:
                result["error"] = "No authorization code received."
                self._respond("No code received. You can close this tab.")
                return

            result["code"] = code
            self._respond(
                "Authorization successful! You can close this tab and return to the terminal."
            )

        def _respond(self, message: str) -> None:
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            html = f"<html><body><h2>{message}</h2></body></html>"
            self.wfile.write(html.encode())

        def log_message(self, format: str, *args: object) -> None:
            pass  # Suppress default logging

    server = HTTPServer(("127.0.0.1", port), CallbackHandler)
    webbrowser.open(auth_url)

    # Handle exactly one request (the callback)
    server.handle_request()
    server.server_close()

    if "error" in result:
        raise RuntimeError(f"OAuth failed: {result['error']}")

    return exchange_code_for_token(result["code"], client_id, client_secret, redirect_uri)


def _build_auth_url(client_id: str, redirect_uri: str, state: str) -> str:
    """Build the Spotify authorization URL."""
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": SCOPES,
        "state": state,
    }
    return f"{SPOTIFY_AUTH_URL}?{urllib.parse.urlencode(params)}"


def exchange_code_for_token(
    code: str, client_id: str, client_secret: str, redirect_uri: str
) -> str:
    """Exchange authorization code for an access token."""
    response = requests.post(
        SPOTIFY_TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "client_secret": client_secret,
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    return data["access_token"]
