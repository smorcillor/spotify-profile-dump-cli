import unittest
from unittest.mock import Mock, patch
from spotify_dump.spotify_api import get_paginated_data


class TestPaginationLogic(unittest.TestCase):
    @patch("spotify_dump.spotify_api.safe_get")
    def test_single_page(self, mock_safe_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [{"id": "1"}, {"id": "2"}],
            "next": None,
        }

        mock_safe_get.return_value = mock_response

        result = get_paginated_data("fake_token", "http://api.url")

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "1")

        mock_safe_get.assert_called_once_with(
            "http://api.url", headers={"Authorization": "Bearer fake_token"}
        )

    @patch("spotify_dump.spotify_api.safe_get")
    def test_multi_page_pagination(self, mock_safe_get):
        mock_response1 = Mock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = {
            "items": [{"id": "1"}, {"id": "2"}],
            "next": "http://api.url/page2",
        }

        mock_response2 = Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            "items": [{"id": "3"}, {"id": "4"}],
            "next": None,
        }

        mock_safe_get.side_effect = [mock_response1, mock_response2]

        result = get_paginated_data("fake_token", "http://api.url/page1")

        self.assertEqual(len(result), 4)
        self.assertEqual([item["id"] for item in result], ["1", "2", "3", "4"])

        self.assertEqual(mock_safe_get.call_count, 2)
        mock_safe_get.assert_any_call(
            "http://api.url/page1", headers={"Authorization": "Bearer fake_token"}
        )
        mock_safe_get.assert_any_call(
            "http://api.url/page2", headers={"Authorization": "Bearer fake_token"}
        )


if __name__ == "__main__":
    unittest.main()
