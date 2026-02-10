#!/usr/bin/env python3
"""Generate test HTML dashboard from sample library fixture."""

import json
import os
import sys

# Add the CLI package src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))

from spotify_dump.html_generator import generate_html

def main():
    fixture_path = os.path.join(os.path.dirname(__file__), 'sample-library.json')
    output_path = os.path.join(os.path.dirname(__file__), 'test-dashboard.html')

    with open(fixture_path, 'r') as f:
        data = json.load(f)

    html = generate_html(
        data['savedTracks'],
        data['playlists'],
        data.get('albums', []),
        data.get('artists', []),
    )

    with open(output_path, 'w') as f:
        f.write(html)

    print(f"Generated: {output_path}")

if __name__ == '__main__':
    main()
