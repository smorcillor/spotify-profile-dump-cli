"""Tests for handling expired/invalid tokens (401 Unauthorized)."""

import unittest
from unittest.mock import Mock, patch

from spotify_dump.spotify_api import (
    SpotifyUnauthorizedError,
    get_paginated_data,
)


class TestTokenExpiration(unittest.TestCase):
    """Test handling of expired or invalid access tokens."""

    @patch("spotify_dump.spotify_api.safe_get")
    def test_get_paginated_data_raises_on_401(self, mock_safe_get):
        """get_paginated_data should raise SpotifyUnauthorizedError on 401."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_safe_get.return_value = mock_response

        with self.assertRaises(SpotifyUnauthorizedError) as context:
            get_paginated_data("expired_token", "http://api.spotify.com/v1/me/tracks")

        self.assertIn("expired", str(context.exception).lower())

    @patch("spotify_dump.spotify_api.safe_get")
    def test_401_during_pagination(self, mock_safe_get):
        """Token expiring mid-pagination should raise SpotifyUnauthorizedError."""
        # First page succeeds
        mock_response1 = Mock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = {
            "items": [{"id": "1"}],
            "next": "http://api.spotify.com/v1/me/tracks?offset=50",
        }

        # Second page fails with 401 (token expired mid-request)
        mock_response2 = Mock()
        mock_response2.status_code = 401

        mock_safe_get.side_effect = [mock_response1, mock_response2]

        with self.assertRaises(SpotifyUnauthorizedError):
            get_paginated_data("token_that_expires", "http://api.spotify.com/v1/me/tracks")


if __name__ == "__main__":
    unittest.main()
