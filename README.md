# Spotify Profile Dump CLI

[![Nightly](https://github.com/smorcillor/spotify-profile-dump-cli/actions/workflows/nightly.yml/badge.svg)](https://github.com/smorcillor/spotify-profile-dump-cli/actions/workflows/nightly.yml)
[![CI](https://github.com/smorcillor/spotify-profile-dump-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/smorcillor/spotify-profile-dump-cli/actions/workflows/ci.yml)

Export your Spotify library as a self-contained HTML dashboard. No server required — runs entirely on your machine.

## Prerequisites

- Python 3.10+
- A [Spotify Premium account](https://www.spotify.com/premium/) (required for app owners in development mode)
- A [Spotify Developer App](https://developer.spotify.com/dashboard)

## Spotify API Limits (Development Mode)

Spotify apps run in **development mode** by default. Be aware of these limits:

- **5 users max** — up to 5 Spotify accounts can use your app
- **Users must be allowlisted** — each user must be added manually via the Developer Dashboard under **Settings > User Management** (name + Spotify email). Without this, API requests return a `403` error
- **Premium required** — the app owner must have a Spotify Premium account
- **1 app per developer** — limited to one development mode Client ID
- **Restricted API endpoints** — some endpoints are not available in development mode ([see full list](https://developer.spotify.com/documentation/web-api/references/changes/february-2026))

For more details, see the [Spotify quota modes documentation](https://developer.spotify.com/documentation/web-api/concepts/quota-modes) and the [February 2026 platform update](https://developer.spotify.com/blog/2026-02-06-update-on-developer-access-and-platform-security).

## Setup

1. **Create a Spotify App** at https://developer.spotify.com/dashboard
   - Set the redirect URI to `http://127.0.0.1:8888/callback`
   - Add yourself (and any other users) under **Settings > User Management**

2. **Install the CLI:**

   ```bash
   pip install .
   ```

3. **Configure credentials:**

   ```bash
   cp .env.example .env
   # Edit .env and add your Client ID and Client Secret
   ```

4. **Run:**

   ```bash
   spotify-dump
   ```

   Your browser will open for Spotify authorization. After approving, the CLI fetches your library and generates an HTML file.

## Usage

```
Usage: spotify-dump [OPTIONS]

Options:
  --client-id TEXT      Spotify Client ID (or SPOTIFY_CLIENT_ID env var)
  --client-secret TEXT  Spotify Client Secret (or SPOTIFY_CLIENT_SECRET env var)
  --token TEXT          Use existing access token (skips OAuth)
  --output TEXT         Output file path (default: spotify_profile.html)
  --port INTEGER        OAuth callback port (default: 8888)
  --help                Show this message and exit.
```

### Using an existing token

If you already have a Spotify access token, you can skip OAuth entirely:

```bash
spotify-dump --token <your-access-token>
```
