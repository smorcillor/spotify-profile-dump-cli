"""CLI entry point for Spotify Profile Dump."""

import logging
import os
import sys

import click
from dotenv import find_dotenv, load_dotenv

from spotify_dump.auth import get_token_via_oauth
from spotify_dump.html_generator import generate_html
from spotify_dump.spinner import Spinner
from spotify_dump.spotify_api import (
    SpotifyForbiddenError,
    SpotifyUnauthorizedError,
    get_followed_artists,
    get_saved_albums,
    get_saved_tracks,
    get_user_playlists,
)


@click.command()
@click.option("--client-id", default=None, help="Spotify Client ID")
@click.option("--client-secret", default=None, help="Spotify Client Secret")
@click.option("--token", default=None, help="Use existing access token (skips OAuth)")
@click.option("--output", default="spotify_profile.html", help="Output file path")
@click.option("--port", default=8888, type=int, help="OAuth callback port")
def main(
    client_id: str | None,
    client_secret: str | None,
    token: str | None,
    output: str,
    port: int,
) -> None:
    """Export your Spotify library as a self-contained HTML dashboard."""
    load_dotenv(find_dotenv(usecwd=True))

    # Suppress rate-limiting and retry warnings from polluting the terminal
    logging.getLogger().setLevel(logging.ERROR)

    client_id = client_id or os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = client_secret or os.environ.get("SPOTIFY_CLIENT_SECRET")

    if not token:
        if not client_id or not client_secret:
            click.echo(
                "Error: --client-id and --client-secret are required (or set "
                "SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET env vars).",
                err=True,
            )
            sys.exit(1)

        click.echo("Opening browser for Spotify authorization...")
        try:
            token = get_token_via_oauth(client_id, client_secret, port)
        except Exception as e:
            click.echo(f"Error during OAuth: {e}", err=True)
            sys.exit(1)
        click.echo("Authorization successful!\n")

    try:
        with Spinner("Fetching saved tracks") as s:
            saved_tracks = get_saved_tracks(token)
            s.done(f"{len(saved_tracks)} saved tracks")

        with Spinner("Fetching playlists") as s:
            playlists = get_user_playlists(token)
            s.done(f"{len(playlists)} playlists")

        with Spinner("Fetching albums") as s:
            albums = get_saved_albums(token)
            s.done(f"{len(albums)} albums")

        with Spinner("Fetching artists") as s:
            artists = get_followed_artists(token)
            s.done(f"{len(artists)} artists")

    except SpotifyUnauthorizedError:
        click.echo("\nError: Access token expired or invalid.", err=True)
        sys.exit(1)
    except SpotifyForbiddenError:
        click.echo(
            "\nError: User not registered in Spotify Developer Dashboard.",
            err=True,
        )
        sys.exit(1)

    with Spinner("Generating HTML") as s:
        html = generate_html(saved_tracks, playlists, albums=albums, artists=artists)
        with open(output, "w", encoding="utf-8") as f:
            f.write(html)
        s.done(f"Saved to {output}")

    click.echo(f"\nDone! Open {output} in your browser.")
