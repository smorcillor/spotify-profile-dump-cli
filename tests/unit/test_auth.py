"""Tests for OAuth authentication flow."""

import unittest
from unittest.mock import Mock, patch, MagicMock
from urllib.parse import parse_qs, urlparse

from spotify_dump.auth import (
    SCOPES,
    SPOTIFY_AUTH_URL,
    _build_auth_url,
    exchange_code_for_token,
)


class TestBuildAuthUrl(unittest.TestCase):
    """Test OAuth URL construction."""

    def test_auth_url_has_correct_base(self):
        url = _build_auth_url("test_client_id", "http://127.0.0.1:8888/callback", "test_state")
        self.assertTrue(url.startswith(SPOTIFY_AUTH_URL))

    def test_auth_url_contains_client_id(self):
        url = _build_auth_url("my_client_id", "http://127.0.0.1:8888/callback", "state123")
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        self.assertEqual(params["client_id"], ["my_client_id"])

    def test_auth_url_contains_redirect_uri(self):
        redirect = "http://localhost:9999/callback"
        url = _build_auth_url("cid", redirect, "state")
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        self.assertEqual(params["redirect_uri"], [redirect])

    def test_auth_url_contains_state(self):
        url = _build_auth_url("cid", "http://127.0.0.1:8888/callback", "my_state")
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        self.assertEqual(params["state"], ["my_state"])

    def test_auth_url_contains_scopes(self):
        url = _build_auth_url("cid", "http://127.0.0.1:8888/callback", "state")
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        self.assertEqual(params["scope"], [SCOPES])

    def test_auth_url_response_type_is_code(self):
        url = _build_auth_url("cid", "http://127.0.0.1:8888/callback", "state")
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        self.assertEqual(params["response_type"], ["code"])


class TestExchangeCodeForToken(unittest.TestCase):
    """Test token exchange with mocked HTTP."""

    @patch("spotify_dump.auth.requests.post")
    def test_successful_token_exchange(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_access_token_123",
            "token_type": "Bearer",
            "expires_in": 3600,
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        token = exchange_code_for_token(
            "auth_code_123", "client_id", "client_secret", "http://127.0.0.1:8888/callback"
        )

        self.assertEqual(token, "test_access_token_123")
        mock_post.assert_called_once()

        # Verify the POST data
        call_kwargs = mock_post.call_args
        post_data = call_kwargs.kwargs.get("data") or call_kwargs[1].get("data")
        self.assertEqual(post_data["grant_type"], "authorization_code")
        self.assertEqual(post_data["code"], "auth_code_123")
        self.assertEqual(post_data["client_id"], "client_id")
        self.assertEqual(post_data["client_secret"], "client_secret")

    @patch("spotify_dump.auth.requests.post")
    def test_token_exchange_raises_on_error(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = Exception("Bad Request")
        mock_post.return_value = mock_response

        with self.assertRaises(Exception):
            exchange_code_for_token(
                "bad_code", "cid", "secret", "http://127.0.0.1:8888/callback"
            )


if __name__ == "__main__":
    unittest.main()
