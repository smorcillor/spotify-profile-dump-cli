"""Tests for html_generator module."""

import json
import re

from spotify_dump.html_generator import generate_html


def test_generate_html_basic():
    """Test basic HTML generation with minimal data."""
    saved_tracks = [
        {
            "name": "Test Song",
            "album": {
                "name": "Test Album",
                "release_date": "2024-01-15",
                "image_url": None
            },
            "artists": [{"name": "Test Artist"}],
            "duration": "3:45",
            "added_at": "2024-01-15T10:30:00Z"
        }
    ]
    playlists = []

    html = generate_html(saved_tracks, playlists)

    assert "<!DOCTYPE html>" in html
    assert "<html" in html
    assert "</html>" in html
    assert "My Spotify Library" in html


def test_generate_html_contains_library_data():
    """Test that generated HTML contains embedded library data."""
    saved_tracks = [
        {
            "name": "Bohemian Rhapsody",
            "album": {
                "name": "A Night at the Opera",
                "release_date": "1975-11-21",
                "image_url": None
            },
            "artists": [{"name": "Queen"}],
            "duration": "5:55",
            "added_at": "2024-01-15T10:30:00Z"
        }
    ]
    playlists = [
        {
            "id": "playlist-1",
            "name": "Rock Classics",
            "image_url": None,
            "tracks": []
        }
    ]

    html = generate_html(saved_tracks, playlists)

    # Check that track data is embedded
    assert "Bohemian Rhapsody" in html
    assert "Queen" in html
    assert "A Night at the Opera" in html

    # Check that playlist data is embedded
    assert "Rock Classics" in html
    assert "playlist-1" in html


def test_generate_html_contains_css():
    """Test that generated HTML contains inlined CSS."""
    html = generate_html([], [])

    # Check for CSS custom properties
    assert "--dashboard-bg" in html
    assert "--dashboard-accent" in html

    # Check for essential CSS classes
    assert ".dashboard-layout" in html
    assert ".stats-grid" in html
    assert ".song-row" in html


def test_generate_html_contains_javascript():
    """Test that generated HTML contains vanilla JS logic."""
    html = generate_html([], [])

    # Check for JS functions
    assert "function calculateStats" in html
    assert "function render" in html
    assert "function getFilteredTracks" in html


def test_generate_html_escapes_script_tags():
    """Test that </script> tags in data are properly escaped."""
    saved_tracks = [
        {
            "name": "Song with </script> tag",
            "album": {
                "name": "Album </script>",
                "release_date": "2024-01-15",
                "image_url": None
            },
            "artists": [{"name": "Artist </script>"}],
            "duration": "3:00",
            "added_at": "2024-01-15T10:30:00Z"
        }
    ]

    html = generate_html(saved_tracks, [])

    # Should not contain unescaped </script> in the data section
    # The escape pattern is <\/script>
    assert "</script> tag" not in html or "<\\/script> tag" in html


def test_generate_html_handles_unicode():
    """Test that generated HTML properly handles unicode characters."""
    saved_tracks = [
        {
            "name": "Música con Ñ y Ü",
            "album": {
                "name": "Álbum Español",
                "release_date": "2024-01-15",
                "image_url": None
            },
            "artists": [{"name": "Artista Japonés 日本語"}],
            "duration": "4:00",
            "added_at": "2024-01-15T10:30:00Z"
        }
    ]

    html = generate_html(saved_tracks, [])

    assert "Música con Ñ y Ü" in html
    assert "Álbum Español" in html
    assert "日本語" in html


def test_generate_html_includes_export_timestamp():
    """Test that generated HTML includes export timestamp."""
    html = generate_html([], [])

    # Check for exportedAt in the embedded data
    assert "exportedAt" in html
    # Should be ISO format with Z suffix
    assert re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', html)


def test_generate_html_empty_library():
    """Test that HTML can be generated for empty library."""
    html = generate_html([], [])

    assert "<!DOCTYPE html>" in html
    assert "savedTracks" in html
    assert "playlists" in html
    assert "albums" in html
    assert "artists" in html


def test_generate_html_with_image_urls():
    """Test that image URLs are included in generated HTML."""
    saved_tracks = [
        {
            "name": "Song with Image",
            "album": {
                "name": "Album with Cover",
                "release_date": "2024-01-15",
                "image_url": "https://example.com/album-cover.jpg"
            },
            "artists": [{"name": "Artist"}],
            "duration": "3:30",
            "added_at": "2024-01-15T10:30:00Z"
        }
    ]
    playlists = [
        {
            "id": "pl-1",
            "name": "Playlist with Cover",
            "image_url": "https://example.com/playlist-cover.jpg",
            "tracks": []
        }
    ]

    html = generate_html(saved_tracks, playlists)

    assert "https://example.com/album-cover.jpg" in html
    assert "https://example.com/playlist-cover.jpg" in html


def test_generate_html_gradient_placeholders():
    """Test that gradient placeholders are defined for missing images."""
    html = generate_html([], [])

    # Check for gradient definitions
    assert "linear-gradient(135deg" in html
    assert "#667eea" in html  # First gradient color


def test_generate_html_valid_json_in_library():
    """Test that the embedded LIBRARY constant contains valid JSON structure."""
    saved_tracks = [
        {
            "name": "Test",
            "album": {"name": "Album", "release_date": "2024", "image_url": None},
            "artists": [{"name": "Artist"}],
            "duration": "3:00",
            "added_at": "2024-01-15T10:30:00Z"
        }
    ]

    html = generate_html(saved_tracks, [])

    # Extract the LIBRARY JSON from the HTML
    match = re.search(r'const LIBRARY = ({.*?});', html, re.DOTALL)
    assert match is not None

    # Unescape the escaped script tags for JSON parsing
    library_json = match.group(1).replace("<\\/", "</")
    library_data = json.loads(library_json)

    assert "savedTracks" in library_data
    assert "playlists" in library_data
    assert "albums" in library_data
    assert "artists" in library_data
    assert "exportedAt" in library_data
    assert len(library_data["savedTracks"]) == 1


def test_generate_html_with_albums():
    """Test that album data is embedded in generated HTML."""
    albums = [
        {
            "name": "Abbey Road",
            "artists": [{"name": "The Beatles"}],
            "release_date": "1969-09-26",
            "total_tracks": 17,
            "image_url": "https://example.com/abbey-road.jpg",
            "added_at": "2024-03-10T12:00:00Z",
        }
    ]

    html = generate_html([], [], albums=albums)

    assert "Abbey Road" in html
    assert "The Beatles" in html
    assert "https://example.com/abbey-road.jpg" in html

    match = re.search(r'const LIBRARY = ({.*?});', html, re.DOTALL)
    library_data = json.loads(match.group(1).replace("<\\/", "</"))
    assert len(library_data["albums"]) == 1
    assert library_data["albums"][0]["name"] == "Abbey Road"


def test_generate_html_with_artists():
    """Test that artist data is embedded in generated HTML."""
    artists = [
        {
            "name": "Radiohead",
            "genres": ["alternative rock", "art rock"],
            "image_url": "https://example.com/radiohead.jpg",
            "followers": 5000000,
        }
    ]

    html = generate_html([], [], artists=artists)

    assert "Radiohead" in html
    assert "https://example.com/radiohead.jpg" in html

    match = re.search(r'const LIBRARY = ({.*?});', html, re.DOTALL)
    library_data = json.loads(match.group(1).replace("<\\/", "</"))
    assert len(library_data["artists"]) == 1
    assert library_data["artists"][0]["name"] == "Radiohead"
    assert "alternative rock" in library_data["artists"][0]["genres"]


def test_generate_html_download_filename():
    """Test that the download filename uses the correct format."""
    html = generate_html([], [])
    assert "my_spotify_library_" in html


def test_generate_html_scroll_preservation():
    """Test that render function preserves scroll position."""
    html = generate_html([], [])
    assert "navScroll" in html
    assert "mainScroll" in html


def test_generate_html_date_added_always_shown():
    """Test that date added column is always shown, including for playlists."""
    html = generate_html([], [])
    assert "const showDateAdded = true;" in html
