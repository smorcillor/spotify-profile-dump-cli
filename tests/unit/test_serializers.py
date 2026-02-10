import unittest

from spotify_dump.spotify_api import format_duration, serialize_album, serialize_artist, serialize_playlist, serialize_saved_track, serialize_track


class TestFormatDuration(unittest.TestCase):
    def test_format_duration_basic(self):
        self.assertEqual(format_duration(234000), "3:54")

    def test_format_duration_with_leading_zero_seconds(self):
        self.assertEqual(format_duration(180000), "3:00")

    def test_format_duration_under_one_minute(self):
        self.assertEqual(format_duration(45000), "0:45")

    def test_format_duration_long_track(self):
        self.assertEqual(format_duration(600000), "10:00")

    def test_format_duration_one_hour(self):
        self.assertEqual(format_duration(3600000), "1:00:00")

    def test_format_duration_one_hour_thirty_minutes(self):
        self.assertEqual(format_duration(5400000), "1:30:00")

    def test_format_duration_multi_hour(self):
        self.assertEqual(format_duration(7265000), "2:01:05")

    def test_format_duration_none(self):
        self.assertIsNone(format_duration(None))


class TestTrackSerialization(unittest.TestCase):
    def test_serialize_track(self):
        sample_track = {
            "name": "You Say Run",
            "album": {
                "name": "TVアニメ『僕のヒーローアカデミア』オリジナル・サウンドトラック",
                "release_date": "2016-07-13",
                "images": [
                    {"url": "https://i.scdn.co/image/abc123", "height": 640, "width": 640}
                ],
            },
            "artists": [{"name": "Yuki Hayashi"}, {"name": "Mock Yuki Hayashi"}],
            "duration_ms": 234000,
        }

        result = serialize_track(sample_track)

        self.assertEqual(result["name"], "You Say Run")
        self.assertEqual(
            result["album"]["name"],
            "TVアニメ『僕のヒーローアカデミア』オリジナル・サウンドトラック",
        )
        self.assertEqual(result["album"]["release_date"], "2016-07-13")
        self.assertEqual(result["album"]["image_url"], "https://i.scdn.co/image/abc123")
        self.assertEqual(len(result["artists"]), 2)
        self.assertEqual(result["artists"][0]["name"], "Yuki Hayashi")
        self.assertEqual(result["duration"], "3:54")

    def test_serialize_saved_track(self):
        sample_track = {
            "track": {
                "name": "You Say Run",
                "album": {
                    "name": "TVアニメ『僕のヒーローアカデミア』オリジナル・サウンドトラック",
                    "release_date": "2016-07-13",
                    "images": [
                        {"url": "https://i.scdn.co/image/abc123", "height": 640, "width": 640}
                    ],
                },
                "artists": [{"name": "Yuki Hayashi"}, {"name": "Mock Yuki Hayashi"}],
                "duration_ms": 234000,
            },
            "added_at": "2025-05-07T12:38:58Z",
        }

        result = serialize_saved_track(sample_track)

        self.assertEqual(result["name"], "You Say Run")
        self.assertEqual(
            result["album"]["name"],
            "TVアニメ『僕のヒーローアカデミア』オリジナル・サウンドトラック",
        )
        self.assertEqual(result["album"]["release_date"], "2016-07-13")
        self.assertEqual(result["album"]["image_url"], "https://i.scdn.co/image/abc123")
        self.assertEqual(len(result["artists"]), 2)
        self.assertEqual(result["artists"][0]["name"], "Yuki Hayashi")
        self.assertEqual(result["duration"], "3:54")
        self.assertEqual(result["added_at"], "2025-05-07T12:38:58Z")

    def test_serialize_missing_fields(self):
        incomplete_track = {"name": "Unknown Track", "album": {}, "artists": []}

        result = serialize_track(incomplete_track)

        self.assertEqual(result["album"]["name"], None)
        self.assertEqual(result["album"]["release_date"], None)
        self.assertEqual(result["album"]["image_url"], None)
        self.assertEqual(len(result["artists"]), 0)
        self.assertEqual(result["duration"], None)


class TestPlaylistSerialization(unittest.TestCase):
    def test_basic_playlist(self):
        playlist_data = {
            "id": "123",
            "name": "You Say Run + Jet Say Run",
            "description": "The two best songs in the world!",
            "images": [
                {"url": "https://i.scdn.co/image/playlist123", "height": 640, "width": 640}
            ],
        }

        tracks = [{"name": "You Say Run"}, {"name": "Jet Say Run"}]
        result = serialize_playlist(playlist_data, tracks)

        self.assertEqual(result["id"], "123")
        self.assertEqual(result["name"], "You Say Run + Jet Say Run")
        self.assertEqual(result["image_url"], "https://i.scdn.co/image/playlist123")
        self.assertEqual(len(result["tracks"]), 2)
        self.assertEqual(result["tracks"][1]["name"], "Jet Say Run")

    def test_playlist_without_image(self):
        playlist_data = {
            "id": "456",
            "name": "Empty Playlist",
            "description": "No image",
        }

        result = serialize_playlist(playlist_data, [])

        self.assertEqual(result["id"], "456")
        self.assertEqual(result["image_url"], None)


class TestAlbumSerialization(unittest.TestCase):
    def test_serialize_album(self):
        sample_album = {
            "album": {
                "name": "Abbey Road",
                "artists": [{"name": "The Beatles"}],
                "release_date": "1969-09-26",
                "total_tracks": 17,
                "images": [
                    {"url": "https://i.scdn.co/image/abbey123", "height": 640, "width": 640}
                ],
            },
            "added_at": "2024-03-10T12:00:00Z",
        }

        result = serialize_album(sample_album)

        self.assertEqual(result["name"], "Abbey Road")
        self.assertEqual(result["artists"][0]["name"], "The Beatles")
        self.assertEqual(result["release_date"], "1969-09-26")
        self.assertEqual(result["total_tracks"], 17)
        self.assertEqual(result["image_url"], "https://i.scdn.co/image/abbey123")
        self.assertEqual(result["added_at"], "2024-03-10T12:00:00Z")

    def test_serialize_album_without_image(self):
        sample_album = {
            "album": {
                "name": "Unknown Album",
                "artists": [],
                "release_date": None,
                "total_tracks": 0,
            },
            "added_at": "2024-01-01T00:00:00Z",
        }

        result = serialize_album(sample_album)

        self.assertIsNone(result["image_url"])


class TestArtistSerialization(unittest.TestCase):
    def test_serialize_artist(self):
        sample_artist = {
            "name": "Radiohead",
            "genres": ["alternative rock", "art rock", "experimental"],
            "images": [
                {"url": "https://i.scdn.co/image/radiohead123", "height": 640, "width": 640}
            ],
            "followers": {"total": 5000000},
        }

        result = serialize_artist(sample_artist)

        self.assertEqual(result["name"], "Radiohead")
        self.assertEqual(result["genres"], ["alternative rock", "art rock", "experimental"])
        self.assertEqual(result["image_url"], "https://i.scdn.co/image/radiohead123")
        self.assertEqual(result["followers"], 5000000)

    def test_serialize_artist_without_image(self):
        sample_artist = {
            "name": "Unknown Artist",
            "genres": [],
            "followers": {"total": 0},
        }

        result = serialize_artist(sample_artist)

        self.assertIsNone(result["image_url"])
        self.assertEqual(result["followers"], 0)


if __name__ == "__main__":
    unittest.main()
