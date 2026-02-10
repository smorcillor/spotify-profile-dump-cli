# Spotify Profile Dump CLI

Export your Spotify library as a self-contained HTML dashboard. No server required — runs entirely on your machine.

## Prerequisites

- Python 3.10+
- A [Spotify Developer App](https://developer.spotify.com/dashboard)

## Setup

1. **Create a Spotify App** at https://developer.spotify.com/dashboard
   - Set the redirect URI to `http://localhost:8888/callback`

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

## Development

```bash
# Install with test dependencies
pip install -e ".[test]"

# Run unit tests
pytest tests/unit/ -v

# Run E2E tests (requires Node.js)
cd tests/e2e
npm install
npx playwright install chromium
cd ../..
python3 tests/e2e/fixtures/generate-html.py
cd tests/e2e && npx playwright test
```
