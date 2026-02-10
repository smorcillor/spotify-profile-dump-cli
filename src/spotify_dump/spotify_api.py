import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from typing import Callable, Dict, List

import requests

# Spotify API base URL - can be overridden for testing
SPOTIFY_API_URL = os.getenv("SPOTIFY_API_URL", "https://api.spotify.com")


class SpotifyForbiddenError(Exception):
    """Raised when Spotify returns 403 Forbidden (user not registered as tester)"""
    pass


class SpotifyUnauthorizedError(Exception):
    """Raised when Spotify returns 401 Unauthorized (token expired or invalid)"""
    pass


def retry_with_backoff(
    max_retries: int = 5,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
):
    """Decorador para reintentos con backoff exponencial y manejo de 429"""

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(max_retries + 1):
                response = func(*args, **kwargs)

                if response.status_code not in [429, 500, 502, 503, 504]:
                    return response

                if response.status_code == 429:
                    if retry_after := response.headers.get("Retry-After"):
                        wait_time = min(float(retry_after), max_delay)
                        logging.warning(f"Rate limited. Waiting {wait_time}s")
                        time.sleep(wait_time)
                        continue

                if attempt < max_retries:
                    wait_time = min(delay * (2**attempt), max_delay)
                    logging.warning(f"Attempt {attempt + 1} failed with status {response.status_code}. Retrying in {wait_time:.2f}s...")
                    time.sleep(wait_time)

            # After all retries, check if the final response is successful
            if response.status_code not in [429, 500, 502, 503, 504]:
                return response
            logging.error(f"All {max_retries + 1} attempts failed. Last status: {response.status_code}")
            return response

        return wrapper

    return decorator


@retry_with_backoff()
def safe_get(url: str, headers: dict, params: dict = None) -> requests.Response:
    return requests.get(url, headers=headers, params=params, timeout=30)


@retry_with_backoff()
def safe_post(url: str, data: dict, headers: dict) -> requests.Response:
    return requests.post(url, data=data, headers=headers, timeout=30)


def get_paginated_data(token: str, url: str) -> List[Dict]:
    """Obtiene datos paginados con manejo de reintentos"""
    headers = {"Authorization": f"Bearer {token}"}
    results = []

    while url:
        response = safe_get(url, headers=headers)

        # Check for 401 Unauthorized (token expired or invalid)
        if response.status_code == 401:
            raise SpotifyUnauthorizedError("Access token expired or invalid")

        # Check for 403 Forbidden (user not registered in Developer Dashboard)
        if response.status_code == 403:
            raise SpotifyForbiddenError(
                "User not registered in Spotify Developer Dashboard"
            )

        response.raise_for_status()
        data = response.json()
        results.extend(data.get("items", []))
        url = data.get("next")

    return results


def format_duration(ms: int | None) -> str | None:
    """Convert milliseconds to mm:ss or h:mm:ss format."""
    if ms is None:
        return None
    total_seconds = ms // 1000
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


def serialize_track(track: dict) -> dict:
    album = track.get("album", {})
    images = album.get("images", [])
    image_url = images[0].get("url") if images else None

    return {
        "name": track.get("name"),
        "album": {
            "name": album.get("name"),
            "release_date": album.get("release_date"),
            "image_url": image_url,
        },
        "artists": [
            {"name": artist.get("name")} for artist in track.get("artists", [])
        ],
        "duration": format_duration(track.get("duration_ms")),
    }


def serialize_saved_track(item: dict) -> dict:
    result = serialize_track(item.get("track", {}))
    result["added_at"] = item.get("added_at")
    return result


def serialize_playlist(playlist_info: dict, tracks: list) -> dict:
    images = playlist_info.get("images", [])
    image_url = images[0].get("url") if images else None

    owner = playlist_info.get("owner", {})

    return {
        "id": playlist_info.get("id"),
        "name": playlist_info.get("name"),
        "description": playlist_info.get("description"),
        "owner": owner.get("display_name") or owner.get("id"),
        "image_url": image_url,
        "tracks": tracks,
    }


def fetch_playlist_tracks_data(token: str, playlist_id: str) -> list:
    fields = "items(added_at,track(name,duration_ms,album(name,release_date,images),artists(name))),next"
    url = f"{SPOTIFY_API_URL}/v1/playlists/{playlist_id}/tracks?fields={fields}"
    return get_paginated_data(token, url)


def process_single_playlist(token: str, playlist_info: dict) -> dict:
    try:
        raw_tracks = fetch_playlist_tracks_data(token, playlist_info["id"])
        tracks = [
            serialize_saved_track(item)
            for item in raw_tracks
            if item.get("track")
        ]
        return serialize_playlist(playlist_info, tracks)

    except requests.exceptions.HTTPError as e:
        logging.exception(f"HTTP error en playlist {playlist_info['id']}")
        return serialize_playlist(playlist_info, []) | {
            "error": f"HTTP Error {e.response.status_code}"
        }
    except Exception as e:
        logging.exception(f"Error inesperado en playlist {playlist_info['id']}")
        return serialize_playlist(playlist_info, []) | {"error": str(e)}


def serialize_album(item: dict) -> dict:
    album = item.get("album", {})
    images = album.get("images", [])
    image_url = images[0].get("url") if images else None

    return {
        "name": album.get("name"),
        "artists": [
            {"name": artist.get("name")} for artist in album.get("artists", [])
        ],
        "release_date": album.get("release_date"),
        "total_tracks": album.get("total_tracks"),
        "image_url": image_url,
        "added_at": item.get("added_at"),
    }


def serialize_artist(item: dict) -> dict:
    images = item.get("images", [])
    image_url = images[0].get("url") if images else None

    return {
        "name": item.get("name"),
        "genres": item.get("genres", []),
        "image_url": image_url,
        "followers": item.get("followers", {}).get("total", 0),
    }


def get_saved_tracks(token: str) -> List[Dict]:
    start = time.time()
    raw_tracks = get_paginated_data(
        token, f"{SPOTIFY_API_URL}/v1/me/tracks?limit=50"
    )
    result = [serialize_saved_track(item) for item in raw_tracks]
    end = time.time()
    logging.info(f"Processed {len(result)} saved songs in {end - start:.2f} seconds")
    return result


def get_user_playlists(token: str) -> List[Dict]:
    start = time.time()
    playlists = get_paginated_data(
        token, f"{SPOTIFY_API_URL}/v1/me/playlists?limit=50"
    )
    with ThreadPoolExecutor(max_workers=10) as executor:
        args = [(token, playlist) for playlist in playlists]
        result = list(executor.map(lambda x: process_single_playlist(*x), args))
    end = time.time()
    logging.info(f"Processed {len(result)} playlists in {end - start:.2f} seconds")
    return result


def get_saved_albums(token: str) -> List[Dict]:
    start = time.time()
    raw_albums = get_paginated_data(
        token, f"{SPOTIFY_API_URL}/v1/me/albums?limit=50"
    )
    result = [serialize_album(item) for item in raw_albums]
    end = time.time()
    logging.info(f"Processed {len(result)} saved albums in {end - start:.2f} seconds")
    return result


def get_followed_artists(token: str) -> List[Dict]:
    """Fetch followed artists using cursor-based pagination."""
    start = time.time()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{SPOTIFY_API_URL}/v1/me/following?type=artist&limit=50"
    results = []

    while url:
        response = safe_get(url, headers=headers)

        if response.status_code == 401:
            raise SpotifyUnauthorizedError("Access token expired or invalid")
        if response.status_code == 403:
            raise SpotifyForbiddenError(
                "User not registered in Spotify Developer Dashboard"
            )

        response.raise_for_status()
        data = response.json()
        artists_data = data.get("artists", {})
        results.extend(artists_data.get("items", []))

        cursors = artists_data.get("cursors", {})
        after = cursors.get("after")
        if after:
            url = f"{SPOTIFY_API_URL}/v1/me/following?type=artist&limit=50&after={after}"
        else:
            url = None

    result = [serialize_artist(item) for item in results]
    end = time.time()
    logging.info(f"Processed {len(result)} followed artists in {end - start:.2f} seconds")
    return result
