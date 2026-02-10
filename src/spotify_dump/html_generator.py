"""Generate self-contained HTML dashboard for Spotify library."""

import json
from datetime import datetime, timezone

# Gradient placeholders for album covers without images
GRADIENTS = [
    "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
    "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
    "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
    "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",
    "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)",
    "linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)",
    "linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)",
]


def generate_html(saved_tracks: list, playlists: list, albums: list = None, artists: list = None) -> str:
    """Generate self-contained HTML dashboard.

    Args:
        saved_tracks: List of saved track objects from Spotify API
        playlists: List of playlist objects from Spotify API
        albums: List of saved album objects from Spotify API
        artists: List of followed artist objects from Spotify API

    Returns:
        Complete HTML string with embedded data, CSS, and JavaScript
    """
    library_data = {
        "savedTracks": saved_tracks,
        "playlists": playlists,
        "albums": albums or [],
        "artists": artists or [],
        "exportedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    # Escape the JSON for safe embedding in script tag
    library_json = json.dumps(library_data, ensure_ascii=False)
    # Escape </script> to prevent breaking out of script tag
    library_json = library_json.replace("</", "<\\/")

    return HTML_TEMPLATE.replace("{{LIBRARY_DATA}}", library_json)


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My Spotify Library</title>
  <style>
/* Dashboard Design Tokens */
:root {
  --dashboard-bg: #f5f5f5;
  --dashboard-card-bg: #ffffff;
  --dashboard-border: #e5e5e5;
  --dashboard-text-primary: #1a1a1a;
  --dashboard-text-secondary: #6b7280;
  --dashboard-text-muted: #9ca3af;
  --dashboard-accent: #10b981;
  --dashboard-accent-light: #ecfdf5;
  --dashboard-hover-bg: #f9fafb;
  --dashboard-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  --dashboard-radius: 12px;
  --dashboard-radius-sm: 8px;
  --dashboard-font: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

/* Base Styles */
body {
  font-family: var(--dashboard-font);
  background: var(--dashboard-bg);
  min-height: 100vh;
  color: var(--dashboard-text-primary);
}

/* Layout Grid */
.dashboard-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  min-height: 100vh;
}

@media (max-width: 900px) {
  .dashboard-layout {
    grid-template-columns: 1fr;
  }

  .dashboard-sidebar {
    display: none;
  }
}

/* Sidebar */
.dashboard-sidebar {
  background: var(--dashboard-card-bg);
  padding: 24px 16px;
  border-right: 1px solid var(--dashboard-border);
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.dashboard-logo {
  padding: 0 8px;
  margin-bottom: 32px;
}

.dashboard-logo-text {
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--dashboard-text-primary);
}

/* Navigation */
.dashboard-nav {
  flex: 1;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 8px;
  border-radius: var(--dashboard-radius-sm);
  cursor: pointer;
  color: var(--dashboard-text-secondary);
  transition: all 0.15s;
  font-weight: 500;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  font-size: 0.95rem;
  font-family: inherit;
}

.nav-item:hover {
  color: var(--dashboard-text-primary);
  background: var(--dashboard-hover-bg);
}

.nav-item.active {
  background: var(--dashboard-accent-light);
  color: var(--dashboard-accent);
}

.nav-item svg {
  width: 20px;
  height: 20px;
  fill: currentColor;
  flex-shrink: 0;
}

/* Playlist Items */
.playlist-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 8px 6px 36px;
  border-radius: var(--dashboard-radius-sm);
  cursor: pointer;
  transition: background 0.15s;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  font-family: inherit;
}

.playlist-item:hover {
  background: var(--dashboard-hover-bg);
}

.playlist-item.active {
  background: var(--dashboard-accent-light);
}

.playlist-cover {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  flex-shrink: 0;
  object-fit: cover;
}

.playlist-info {
  overflow: hidden;
}

.playlist-name {
  font-size: 0.85rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--dashboard-text-secondary);
}

.playlist-item:hover .playlist-name {
  color: var(--dashboard-text-primary);
}

.playlist-count {
  font-size: 0.7rem;
  color: var(--dashboard-text-muted);
}

/* Nav Action */
.nav-action {
  margin-top: auto;
  padding-top: 16px;
  border-top: 1px solid var(--dashboard-border);
}

/* Main Content */
.dashboard-main {
  padding: 32px 40px;
  overflow-y: auto;
  background: var(--dashboard-bg);
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--dashboard-text-primary);
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 28px;
}

@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.stat-card {
  background: var(--dashboard-card-bg);
  border-radius: var(--dashboard-radius);
  padding: 24px;
  box-shadow: var(--dashboard-shadow);
  border: 1px solid var(--dashboard-border);
}

.stat-label {
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--dashboard-text-muted);
  margin-bottom: 8px;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--dashboard-text-primary);
}

.stat-value-highlight {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--dashboard-accent);
  margin-left: 8px;
}

.stat-sub {
  font-size: 0.8rem;
  color: var(--dashboard-text-muted);
  margin-top: 4px;
}

/* Year Timeline */
.year-timeline {
  background: var(--dashboard-card-bg);
  border-radius: var(--dashboard-radius);
  padding: 24px;
  margin-bottom: 28px;
  box-shadow: var(--dashboard-shadow);
  border: 1px solid var(--dashboard-border);
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--dashboard-text-primary);
}

.timeline-info {
  font-size: 0.8rem;
  color: var(--dashboard-text-muted);
}

.year-tabs {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 4px;
}

.year-tabs::-webkit-scrollbar {
  height: 4px;
}

.year-tabs::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 2px;
}

.year-tab {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 14px 24px;
  background: var(--dashboard-hover-bg);
  border: 1px solid var(--dashboard-border);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  min-width: fit-content;
  font-family: inherit;
}

.year-tab:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.year-tab.active {
  background: var(--dashboard-accent);
  border-color: var(--dashboard-accent);
}

.year-tab.active .year-number,
.year-tab.active .year-count {
  color: #ffffff;
}

.year-tab.active .year-count {
  opacity: 0.8;
}

.year-number {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--dashboard-text-primary);
}

.year-count {
  font-size: 0.7rem;
  color: var(--dashboard-text-muted);
  margin-top: 2px;
}

.year-tab.all-years {
  background: transparent;
  border-style: dashed;
  border-color: #d1d5db;
}

.year-tab.all-years:hover {
  background: var(--dashboard-hover-bg);
}

.year-tab.all-years.active {
  background: var(--dashboard-accent);
  border-style: solid;
}

/* Songs Section */
.songs-section {
  background: var(--dashboard-card-bg);
  border-radius: var(--dashboard-radius);
  padding: 24px;
  box-shadow: var(--dashboard-shadow);
  border: 1px solid var(--dashboard-border);
}

.songs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

/* Songs Table */
.songs-table-header {
  display: grid;
  grid-template-columns: 16px 4fr 3fr 2fr 1fr;
  gap: 16px;
  padding: 0 16px 12px;
  border-bottom: 1px solid var(--dashboard-border);
  margin-bottom: 8px;
}

.songs-table-header span {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--dashboard-text-muted);
  font-weight: 600;
}

.songs-table-header .col-duration {
  text-align: right;
}

.song-row {
  display: grid;
  grid-template-columns: 16px 4fr 3fr 2fr 1fr;
  gap: 16px;
  padding: 10px 16px;
  border-radius: var(--dashboard-radius-sm);
  cursor: pointer;
  transition: background 0.15s;
  align-items: center;
}

.song-row:hover {
  background: var(--dashboard-hover-bg);
}

.song-row:hover .song-title {
  color: var(--dashboard-accent);
}

.col-number {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.song-number {
  font-size: 0.85rem;
  color: var(--dashboard-text-muted);
}

.col-title {
  display: flex;
  align-items: center;
  gap: 12px;
  overflow: hidden;
}

.song-cover {
  width: 44px;
  height: 44px;
  border-radius: 6px;
  flex-shrink: 0;
  object-fit: cover;
}

.song-info {
  overflow: hidden;
}

.song-title {
  font-size: 0.95rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--dashboard-text-primary);
  transition: color 0.15s;
}

.song-artist {
  font-size: 0.8rem;
  color: var(--dashboard-text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.col-album {
  font-size: 0.85rem;
  color: var(--dashboard-text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.col-date {
  font-size: 0.85rem;
  color: var(--dashboard-text-secondary);
}

.col-duration {
  font-size: 0.85rem;
  color: var(--dashboard-text-secondary);
  text-align: right;
}

/* Playlist Header */
.playlist-header {
  display: flex;
  gap: 24px;
  align-items: flex-end;
  margin-bottom: 28px;
  padding: 32px;
  background: var(--dashboard-card-bg);
  border-radius: var(--dashboard-radius);
  box-shadow: var(--dashboard-shadow);
  border: 1px solid var(--dashboard-border);
}

.playlist-header-cover {
  width: 192px;
  height: 192px;
  border-radius: 8px;
  flex-shrink: 0;
  object-fit: cover;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.playlist-header-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow: hidden;
}

.playlist-header-label {
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--dashboard-text-muted);
}

.playlist-header-title {
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--dashboard-text-primary);
  line-height: 1.1;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.playlist-header-description {
  font-size: 0.9rem;
  color: var(--dashboard-text-secondary);
  line-height: 1.4;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.playlist-header-meta {
  font-size: 0.85rem;
  color: var(--dashboard-text-muted);
  margin-top: 4px;
}

@media (max-width: 768px) {
  .playlist-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 24px;
  }

  .playlist-header-cover {
    width: 140px;
    height: 140px;
  }

  .playlist-header-title {
    font-size: 1.5rem;
  }
}

/* Album Grid */
.album-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 24px;
}

.album-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.album-cover-large {
  width: 100%;
  aspect-ratio: 1;
  border-radius: var(--dashboard-radius);
  object-fit: cover;
}

.album-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--dashboard-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.album-meta {
  font-size: 0.8rem;
  color: var(--dashboard-text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Artist Grid */
.artist-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 24px;
}

.artist-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  text-align: center;
}

.artist-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
}

.artist-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--dashboard-text-primary);
}

.artist-genres {
  font-size: 0.75rem;
  color: var(--dashboard-text-muted);
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px 32px;
  text-align: center;
  grid-column: 1 / -1;
}

.empty-state-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--dashboard-text-primary);
  margin-bottom: 12px;
}

.empty-state-description {
  font-size: 1rem;
  color: var(--dashboard-text-secondary);
  max-width: 400px;
  margin-bottom: 24px;
}

.empty-state-action {
  padding: 12px 24px;
  background: var(--dashboard-accent);
  color: white;
  border: none;
  border-radius: var(--dashboard-radius-sm);
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.15s;
  font-family: inherit;
}

.empty-state-action:hover {
  opacity: 0.9;
}

/* Header Actions */
.header-actions {
  display: flex;
  gap: 12px;
}

.btn-secondary {
  padding: 8px 16px;
  background: transparent;
  color: var(--dashboard-text-secondary);
  border: 1px solid var(--dashboard-border);
  border-radius: var(--dashboard-radius-sm);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
  font-family: inherit;
}

.btn-secondary:hover {
  background: var(--dashboard-hover-bg);
  color: var(--dashboard-text-primary);
}

/* Scrollbar Styling */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--dashboard-text-muted);
}

@media (max-width: 768px) {
  .dashboard-main {
    padding: 24px 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .songs-table-header,
  .song-row {
    grid-template-columns: 16px 1fr 80px;
  }

  .col-album,
  .col-date {
    display: none;
  }
}
/* Lightbox */
.lightbox-overlay {
  display: none;
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.lightbox-overlay.active {
  display: flex;
}

.lightbox-img {
  max-width: 80vw;
  max-height: 80vh;
  border-radius: var(--dashboard-radius);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.4);
  object-fit: contain;
  cursor: default;
}

/* Playlist Nav Row */
.playlist-nav-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 8px;
}

.playlist-nav-label {
  display: flex;
  align-items: center;
  gap: 16px;
  font-weight: 500;
  font-size: 0.95rem;
  color: var(--dashboard-text-secondary);
}

.playlist-nav-label svg {
  width: 20px;
  height: 20px;
  fill: currentColor;
  flex-shrink: 0;
}

.playlist-search-toggle {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  color: var(--dashboard-text-muted);
  transition: color 0.15s, background 0.15s;
}

.playlist-search-toggle:hover {
  color: var(--dashboard-text-primary);
  background: var(--dashboard-hover-bg);
}

.playlist-search-toggle svg {
  width: 18px;
  height: 18px;
  fill: currentColor;
}

.playlist-search-wrapper {
  display: none;
  padding: 0 8px 8px 36px;
}

.playlist-search-wrapper.visible {
  display: block;
}

.playlist-search-wrapper input {
  width: 100%;
  padding: 6px 10px;
  border: 1px solid var(--dashboard-border);
  border-radius: 6px;
  background: var(--dashboard-hover-bg);
  color: var(--dashboard-text-primary);
  font-size: 0.8rem;
  font-family: inherit;
  outline: none;
  transition: border-color 0.15s;
}

.playlist-search-wrapper input:focus {
  border-color: var(--dashboard-accent);
}

.playlist-search-wrapper input::placeholder {
  color: var(--dashboard-text-muted);
}

.search-bar {
  position: relative;
  max-width: 300px;
}

.search-bar input {
  width: 100%;
  padding: 8px 12px 8px 36px;
  border: 1px solid var(--dashboard-border);
  border-radius: var(--dashboard-radius-sm);
  background: var(--dashboard-hover-bg);
  color: var(--dashboard-text-primary);
  font-size: 0.875rem;
  font-family: inherit;
  outline: none;
  transition: border-color 0.15s;
}

.search-bar input:focus {
  border-color: var(--dashboard-accent);
}

.search-bar input::placeholder {
  color: var(--dashboard-text-muted);
}

.search-bar svg {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  fill: var(--dashboard-text-muted);
  pointer-events: none;
}

/* Make all images with src clickable */
img.song-cover,
img.playlist-cover,
img.playlist-header-cover,
img.album-cover-large,
img.artist-avatar {
  cursor: pointer;
}
  </style>
</head>
<body>
  <div class="lightbox-overlay" id="lightbox" data-testid="lightbox">
    <img class="lightbox-img" id="lightbox-img" src="" alt="" data-testid="lightbox-img">
  </div>
  <div class="dashboard-layout">
    <aside class="dashboard-sidebar" id="sidebar">
      <!-- Populated by JavaScript -->
    </aside>
    <main class="dashboard-main" id="main">
      <!-- Populated by JavaScript -->
    </main>
  </div>

  <script>
    // Library data embedded at export time
    const LIBRARY = {{LIBRARY_DATA}};

    // Gradient placeholders for album covers
    const GRADIENTS = [
      "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
      "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
      "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
      "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",
      "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)",
      "linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)",
      "linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)",
    ];

    // State
    let state = {
      viewMode: 'saved', // 'saved', 'playlist', 'albums', or 'artists'
      selectedYear: null,
      selectedPlaylistId: null,
      searchQuery: '',
      playlistSearchQuery: '',
    };

    // Utility functions
    function extractYear(dateStr) {
      if (!dateStr) return null;
      const match = dateStr.match(/^(\\d{4})/);
      return match ? match[1] : null;
    }

    function hashString(str) {
      let hash = 0;
      for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
      }
      return Math.abs(hash);
    }

    function getGradient(seed) {
      return GRADIENTS[hashString(seed) % GRADIENTS.length];
    }

    function formatNumber(num) {
      return num.toLocaleString();
    }

    function formatDate(dateStr) {
      if (!dateStr) return '-';
      try {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
        });
      } catch {
        return '-';
      }
    }

    function formatArtists(artists) {
      return artists.map(a => a.name).join(', ');
    }

    function formatCount(count) {
      return count === 1 ? '1 song' : `${formatNumber(count)} songs`;
    }

    function parseDurationToSeconds(dur) {
      if (!dur) return 0;
      const parts = dur.split(':').map(Number);
      if (parts.length === 3) return parts[0] * 3600 + parts[1] * 60 + parts[2];
      if (parts.length === 2) return parts[0] * 60 + parts[1];
      return 0;
    }

    function formatTotalDuration(tracks) {
      const totalSec = tracks.reduce((sum, t) => sum + parseDurationToSeconds(t.duration), 0);
      const hours = Math.floor(totalSec / 3600);
      const minutes = Math.floor((totalSec % 3600) / 60);
      const seconds = totalSec % 60;
      if (hours > 0) return `${hours} hr ${minutes} min`;
      return `${minutes} min ${seconds} sec`;
    }

    // Calculate statistics
    function calculateStats() {
      const currentYear = new Date().getFullYear().toString();
      const lastYear = (new Date().getFullYear() - 1).toString();
      const yearCounts = {};

      for (const track of LIBRARY.savedTracks) {
        const year = extractYear(track.added_at);
        if (year) {
          yearCounts[year] = (yearCounts[year] || 0) + 1;
        }
      }

      let topYear = null;
      let topYearCount = 0;
      for (const [year, count] of Object.entries(yearCounts)) {
        if (count > topYearCount) {
          topYear = year;
          topYearCount = count;
        }
      }

      const playlistTrackCount = LIBRARY.playlists.reduce((sum, p) => sum + p.tracks.length, 0);

      return {
        totalSongs: LIBRARY.savedTracks.length,
        thisYearSongs: yearCounts[currentYear] || 0,
        lastYearSongs: yearCounts[lastYear] || 0,
        playlistCount: LIBRARY.playlists.length,
        playlistTrackCount,
        yearCounts,
        topYear,
        topYearCount,
      };
    }

    // Get available years sorted descending
    function getAvailableYears(stats) {
      return Object.keys(stats.yearCounts).sort((a, b) => parseInt(b) - parseInt(a));
    }

    // Get filtered tracks based on current state
    function getFilteredTracks() {
      let tracks;

      if (state.viewMode === 'playlist' && state.selectedPlaylistId) {
        const playlist = LIBRARY.playlists.find(p => p.id === state.selectedPlaylistId);
        tracks = playlist ? playlist.tracks : [];
      } else {
        tracks = LIBRARY.savedTracks;
      }

      // Apply year filter (only for saved tracks)
      if (state.selectedYear && state.viewMode === 'saved') {
        tracks = tracks.filter(track => extractYear(track.added_at) === state.selectedYear);
      }

      // Apply search filter
      if (state.searchQuery && (state.viewMode === 'saved' || state.viewMode === 'playlist')) {
        const q = state.searchQuery.toLowerCase();
        tracks = tracks.filter(track =>
          (track.name && track.name.toLowerCase().includes(q)) ||
          (track.album && track.album.name && track.album.name.toLowerCase().includes(q)) ||
          (track.artists && track.artists.some(a => a.name && a.name.toLowerCase().includes(q)))
        );
      }

      return tracks;
    }

    // Create album cover element
    function createAlbumCover(src, alt, seed, className) {
      if (src) {
        const img = document.createElement('img');
        img.src = src;
        img.alt = alt;
        img.className = className;
        img.loading = 'lazy';
        return img;
      } else {
        const div = document.createElement('div');
        div.className = className;
        div.style.background = getGradient(seed || alt);
        div.setAttribute('aria-label', alt);
        return div;
      }
    }

    // Render sidebar
    function renderSidebar() {
      const sidebar = document.getElementById('sidebar');
      const stats = calculateStats();

      sidebar.innerHTML = `
        <div class="dashboard-logo">
          <span class="dashboard-logo-text" data-testid="logo-text">Spotify Profile Dump</span>
        </div>
        <nav class="dashboard-nav" id="nav">
          <button class="nav-item ${state.viewMode === 'saved' ? 'active' : ''}" data-action="select-saved" data-testid="nav-saved-songs">
            <svg viewBox="0 0 24 24">
              <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
            </svg>
            <span>Saved Songs</span>
          </button>
          ${LIBRARY.albums.length > 0 ? `
            <button class="nav-item ${state.viewMode === 'albums' ? 'active' : ''}" data-action="select-albums" data-testid="nav-albums">
              <svg viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 14.5c-2.49 0-4.5-2.01-4.5-4.5S9.51 7.5 12 7.5s4.5 2.01 4.5 4.5-2.01 4.5-4.5 4.5zm0-5.5c-.55 0-1 .45-1 1s.45 1 1 1 1-.45 1-1-.45-1-1-1z" />
              </svg>
              <span>Albums</span>
            </button>
          ` : ''}
          ${LIBRARY.artists.length > 0 ? `
            <button class="nav-item ${state.viewMode === 'artists' ? 'active' : ''}" data-action="select-artists" data-testid="nav-artists">
              <svg viewBox="0 0 24 24">
                <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
              </svg>
              <span>Artists</span>
            </button>
          ` : ''}
          ${LIBRARY.playlists.length > 0 ? `
            <div class="playlist-nav-row" data-testid="nav-playlists">
              <span class="playlist-nav-label">
                <svg viewBox="0 0 24 24">
                  <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z" />
                </svg>
                Playlists
              </span>
              <button class="playlist-search-toggle" id="playlist-search-toggle" title="Search playlists" data-testid="playlist-search-toggle">
                <svg viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
              </button>
            </div>
            <div class="playlist-search-wrapper ${state.playlistSearchQuery ? 'visible' : ''}" id="playlist-search-wrapper" data-testid="playlist-search-wrapper">
              <input type="text" id="playlist-search-input" placeholder="Search playlists..." value="${escapeHtml(state.playlistSearchQuery)}" data-testid="playlist-search-input">
            </div>
            <div id="playlist-list"></div>
          ` : ''}
        </nav>
        <div class="nav-action">
          <button class="nav-item" data-action="save-copy" data-testid="save-copy">
            <svg viewBox="0 0 24 24">
              <path d="M19 12v7H5v-7H3v7c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2v-7h-2zm-6 .67l2.59-2.58L17 11.5l-5 5-5-5 1.41-1.41L11 12.67V3h2v9.67z" />
            </svg>
            <span>Save a Copy</span>
          </button>
        </div>
      `;

      // Add playlist items
      renderPlaylistList();

      // Add playlist search toggle handler
      const searchToggle = document.getElementById('playlist-search-toggle');
      const searchWrapper = document.getElementById('playlist-search-wrapper');
      if (searchToggle && searchWrapper) {
        searchToggle.addEventListener('click', function() {
          const isVisible = searchWrapper.classList.toggle('visible');
          if (isVisible) {
            const input = document.getElementById('playlist-search-input');
            if (input) input.focus();
          } else {
            const input = document.getElementById('playlist-search-input');
            if (input) {
              input.value = '';
              state.playlistSearchQuery = '';
              renderPlaylistList();
            }
          }
        });
      }

      // Add playlist search handler
      const playlistSearchInput = document.getElementById('playlist-search-input');
      if (playlistSearchInput) {
        playlistSearchInput.addEventListener('input', function(e) {
          state.playlistSearchQuery = e.target.value;
          renderPlaylistList();
        });
      }

      // Add event listeners
      sidebar.addEventListener('click', handleSidebarClick);
    }

    // Render main content
    function renderMain() {
      const main = document.getElementById('main');
      const stats = calculateStats();
      const years = getAvailableYears(stats);
      const tracks = getFilteredTracks();

      const currentYear = new Date().getFullYear().toString();
      const lastYear = (new Date().getFullYear() - 1).toString();
      const yearSpan = years.length === 0 ? '' : years.length === 1 ? `in ${years[0]}` : `Across ${years.length} years`;

      let yearOverYearChange = null;
      if (stats.lastYearSongs > 0) {
        yearOverYearChange = Math.round(((stats.thisYearSongs - stats.lastYearSongs) / stats.lastYearSongs) * 100);
      }

      const showDateAdded = true;

      // Get section title
      let sectionTitle;
      if (state.viewMode === 'playlist' && state.selectedPlaylistId) {
        const playlist = LIBRARY.playlists.find(p => p.id === state.selectedPlaylistId);
        sectionTitle = playlist ? playlist.name : 'Playlist';
      } else if (state.viewMode === 'albums') {
        sectionTitle = 'Saved Albums';
      } else if (state.viewMode === 'artists') {
        sectionTitle = 'Followed Artists';
      } else if (state.selectedYear) {
        sectionTitle = `Songs from ${state.selectedYear}`;
      } else {
        sectionTitle = 'All Saved Songs';
      }

      // Build playlist header if in playlist view
      let playlistHeaderHtml = '';
      if (state.viewMode === 'playlist' && state.selectedPlaylistId) {
        const playlist = LIBRARY.playlists.find(p => p.id === state.selectedPlaylistId);
        if (playlist) {
          playlistHeaderHtml = `
            <div class="playlist-header" data-testid="playlist-header">
              <div id="playlist-header-cover-slot" data-playlist-id="${playlist.id}"></div>
              <div class="playlist-header-info">
                <span class="playlist-header-label">Playlist</span>
                <h1 class="playlist-header-title" data-testid="playlist-header-title">${escapeHtml(playlist.name)}</h1>
                ${playlist.description ? `<p class="playlist-header-description">${escapeHtml(playlist.description)}</p>` : ''}
                <span class="playlist-header-meta" data-testid="playlist-header-meta">${playlist.owner ? escapeHtml(playlist.owner) + ' · ' : ''}${formatCount(playlist.tracks.length)} · ${formatTotalDuration(playlist.tracks)}</span>
              </div>
            </div>
          `;
        }
      }

      main.innerHTML = `
        ${state.viewMode === 'playlist' && playlistHeaderHtml ? playlistHeaderHtml : `
          <div class="dashboard-header">
            <h1 class="page-title">${escapeHtml(sectionTitle)}</h1>
            <div class="header-actions">
              <span style="font-size: 0.85rem; color: var(--dashboard-text-muted);">
                Exported ${formatDate(LIBRARY.exportedAt)}
              </span>
            </div>
          </div>
        `}

        ${state.viewMode === 'saved' ? `
          <div class="stats-grid" data-testid="stats-grid">
            <div class="stat-card" data-testid="stat-total-songs">
              <div class="stat-label">Total Songs</div>
              <div class="stat-value">${formatNumber(stats.totalSongs)}</div>
              <div class="stat-sub">${yearSpan}</div>
            </div>
            <div class="stat-card" data-testid="stat-this-year">
              <div class="stat-label">This Year</div>
              <div class="stat-value">
                ${formatNumber(stats.thisYearSongs)}
                ${yearOverYearChange !== null ? `<span class="stat-value-highlight">${yearOverYearChange >= 0 ? '+' : ''}${yearOverYearChange}%</span>` : ''}
              </div>
              <div class="stat-sub">vs last year</div>
            </div>
            <div class="stat-card" data-testid="stat-playlists">
              <div class="stat-label">Playlists</div>
              <div class="stat-value">${stats.playlistCount}</div>
              <div class="stat-sub">${formatNumber(stats.playlistTrackCount)} total tracks</div>
            </div>
            <div class="stat-card" data-testid="stat-top-year">
              <div class="stat-label">Top Year</div>
              <div class="stat-value">${stats.topYear || '-'}</div>
              <div class="stat-sub">${stats.topYearCount > 0 ? `${formatNumber(stats.topYearCount)} songs saved` : 'No data'}</div>
            </div>
          </div>
        ` : ''}

        ${state.viewMode === 'saved' ? `
          <div class="year-timeline" data-testid="year-timeline">
            <div class="timeline-header">
              <h2 class="section-title">Browse by Year</h2>
              <span class="timeline-info">Select a year to filter songs</span>
            </div>
            <div class="year-tabs" id="year-tabs">
              <button class="year-tab all-years ${state.selectedYear === null ? 'active' : ''}" data-year="" data-testid="year-tab-all">
                <span class="year-number">All</span>
                <span class="year-count">${formatCount(stats.totalSongs)}</span>
              </button>
              ${years.map(year => `
                <button class="year-tab ${state.selectedYear === year ? 'active' : ''}" data-year="${year}" data-testid="year-tab-${year}">
                  <span class="year-number">${year}</span>
                  <span class="year-count">${formatCount(stats.yearCounts[year] || 0)}</span>
                </button>
              `).join('')}
            </div>
          </div>
        ` : ''}

        ${state.viewMode === 'albums' ? `
          <section class="songs-section" data-testid="albums-section">
            <div class="songs-header">
              <h2 class="section-title">${escapeHtml(sectionTitle)}</h2>
              <div class="search-bar">
                <svg viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
                <input type="text" id="search-input" placeholder="Search albums, artists..." value="${escapeHtml(state.searchQuery)}" data-testid="search-input">
              </div>
            </div>
            <div class="album-grid" id="album-grid"></div>
          </section>
        ` : state.viewMode === 'artists' ? `
          <section class="songs-section" data-testid="artists-section">
            <div class="songs-header">
              <h2 class="section-title">${escapeHtml(sectionTitle)}</h2>
              <div class="search-bar">
                <svg viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
                <input type="text" id="search-input" placeholder="Search artists, genres..." value="${escapeHtml(state.searchQuery)}" data-testid="search-input">
              </div>
            </div>
            <div class="artist-grid" id="artist-grid"></div>
          </section>
        ` : `
          <section class="songs-section" data-testid="songs-section">
            <div class="songs-header">
              ${state.viewMode !== 'playlist' ? `
                <h2 class="section-title" data-testid="songs-section-title">${escapeHtml(sectionTitle)}</h2>
              ` : '<div></div>'}
              <div class="search-bar">
                <svg viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
                <input type="text" id="search-input" placeholder="Search songs, artists, albums..." value="${escapeHtml(state.searchQuery)}" data-testid="search-input">
              </div>
            </div>
            ${tracks.length > 0 ? `
              <div class="songs-table-header" data-testid="songs-table-header">
                <span>#</span>
                <span>Title</span>
                <span>Album</span>
                <span>${showDateAdded ? 'Date Added' : ''}</span>
                <span class="col-duration">Duration</span>
              </div>
              <div class="songs-table" id="songs-table"></div>
            ` : `
              <div class="empty-state" id="songs-empty-state" data-testid="empty-state">
                <div class="empty-state-title" data-testid="empty-state-title">${state.selectedYear ? 'No songs in this year' : 'No songs found'}</div>
                <div class="empty-state-description">
                  ${state.selectedYear
                    ? `You haven't saved any songs in ${state.selectedYear}. Try selecting 'All' to see your complete library.`
                    : 'No tracks available.'}
                </div>
                ${state.selectedYear ? `
                  <button class="empty-state-action" data-action="clear-year" data-testid="clear-year">Show All Songs</button>
                ` : ''}
              </div>
            `}
          </section>
        `}
      `;

      // Render song rows
      const songsTable = document.getElementById('songs-table');
      if (songsTable && tracks.length > 0) {
        for (let i = 0; i < tracks.length; i++) {
          const track = tracks[i];
          const row = document.createElement('div');
          row.className = 'song-row';
          row.dataset.testid = 'song-row';

          const cover = createAlbumCover(
            track.album.image_url,
            track.album.name,
            track.name + track.album.name,
            'song-cover'
          );

          row.innerHTML = `
            <div class="col-number">
              <span class="song-number">${i + 1}</span>
            </div>
            <div class="col-title">
              <div class="song-info">
                <div class="song-title" data-testid="song-title">${escapeHtml(track.name)}</div>
                <div class="song-artist" data-testid="song-artist">${escapeHtml(formatArtists(track.artists))}</div>
              </div>
            </div>
            <div class="col-album" data-testid="song-album">${escapeHtml(track.album.name)}</div>
            <div class="col-date">${showDateAdded ? formatDate(track.added_at) : '-'}</div>
            <div class="col-duration" data-testid="song-duration">${track.duration}</div>
          `;

          // Insert cover before song-info
          const colTitle = row.querySelector('.col-title');
          colTitle.insertBefore(cover, colTitle.firstChild);

          songsTable.appendChild(row);
        }
      }

      // Render playlist header cover
      const coverSlot = document.getElementById('playlist-header-cover-slot');
      if (coverSlot) {
        const playlist = LIBRARY.playlists.find(p => p.id === coverSlot.dataset.playlistId);
        if (playlist) {
          const cover = createAlbumCover(playlist.image_url, playlist.name, playlist.id, 'playlist-header-cover');
          coverSlot.replaceWith(cover);
        }
      }

      // Render album/artist grids
      renderAlbumGrid();
      renderArtistGrid();

      // Add event listeners for year tabs
      const yearTabs = document.getElementById('year-tabs');
      if (yearTabs) {
        yearTabs.addEventListener('click', handleYearClick);
      }

      // Add event listener for empty state action
      main.addEventListener('click', handleMainClick);

      // Add search input handler
      const searchInput = document.getElementById('search-input');
      if (searchInput) {
        searchInput.addEventListener('input', function(e) {
          state.searchQuery = e.target.value;
          if (state.viewMode === 'albums') renderAlbumGrid();
          else if (state.viewMode === 'artists') renderArtistGrid();
          else renderSongsTable();
        });
      }
    }

    // Re-render only the songs table (preserves search focus)
    function renderSongsTable() {
      const songsTable = document.getElementById('songs-table');
      const emptyState = document.getElementById('songs-empty-state');
      if (!songsTable && !emptyState) return;

      const tracks = getFilteredTracks();
      const showDateAdded = true;
      const container = songsTable ? songsTable.parentElement : emptyState.parentElement;

      // Remove old table or empty state
      if (songsTable) songsTable.remove();
      if (emptyState) emptyState.remove();

      // Also remove/add table header
      const oldHeader = container.querySelector('.songs-table-header');
      if (oldHeader) oldHeader.remove();

      if (tracks.length > 0) {
        const header = document.createElement('div');
        header.className = 'songs-table-header';
        header.dataset.testid = 'songs-table-header';
        header.innerHTML = `
          <span>#</span>
          <span>Title</span>
          <span>Album</span>
          <span>${showDateAdded ? 'Date Added' : ''}</span>
          <span class="col-duration">Duration</span>
        `;
        container.appendChild(header);

        const table = document.createElement('div');
        table.className = 'songs-table';
        table.id = 'songs-table';

        for (let i = 0; i < tracks.length; i++) {
          const track = tracks[i];
          const row = document.createElement('div');
          row.className = 'song-row';
          row.dataset.testid = 'song-row';

          const cover = createAlbumCover(
            track.album.image_url,
            track.album.name,
            track.name + track.album.name,
            'song-cover'
          );

          row.innerHTML = `
            <div class="col-number">
              <span class="song-number">${i + 1}</span>
            </div>
            <div class="col-title">
              <div class="song-info">
                <div class="song-title" data-testid="song-title">${escapeHtml(track.name)}</div>
                <div class="song-artist" data-testid="song-artist">${escapeHtml(formatArtists(track.artists))}</div>
              </div>
            </div>
            <div class="col-album" data-testid="song-album">${escapeHtml(track.album.name)}</div>
            <div class="col-date">${showDateAdded ? formatDate(track.added_at) : '-'}</div>
            <div class="col-duration" data-testid="song-duration">${track.duration}</div>
          `;

          const colTitle = row.querySelector('.col-title');
          colTitle.insertBefore(cover, colTitle.firstChild);
          table.appendChild(row);
        }
        container.appendChild(table);
      } else {
        const empty = document.createElement('div');
        empty.className = 'empty-state';
        empty.id = 'songs-empty-state';
        empty.dataset.testid = 'empty-state';
        empty.innerHTML = `
          <div class="empty-state-title">No matches found</div>
          <div class="empty-state-description">Try a different search term.</div>
        `;
        container.appendChild(empty);
      }
    }

    // Re-render playlist list in sidebar (preserves search focus)
    function renderPlaylistList() {
      const playlistList = document.getElementById('playlist-list');
      if (!playlistList) return;
      playlistList.innerHTML = '';

      const q = state.playlistSearchQuery.toLowerCase();
      const playlists = q
        ? LIBRARY.playlists.filter(p => p.name && p.name.toLowerCase().includes(q))
        : LIBRARY.playlists;

      for (const playlist of playlists) {
        const btn = document.createElement('button');
        btn.className = 'playlist-item' + (state.selectedPlaylistId === playlist.id ? ' active' : '');
        btn.dataset.action = 'select-playlist';
        btn.dataset.playlistId = playlist.id;
        btn.dataset.testid = 'playlist-item';

        const cover = createAlbumCover(playlist.image_url, playlist.name, playlist.id, 'playlist-cover');
        btn.appendChild(cover);

        const info = document.createElement('div');
        info.className = 'playlist-info';
        info.innerHTML = `
          <div class="playlist-name" data-testid="playlist-name">${escapeHtml(playlist.name)}</div>
          <div class="playlist-count" data-testid="playlist-count">${playlist.tracks.length} songs</div>
        `;
        btn.appendChild(info);

        playlistList.appendChild(btn);
      }
    }

    // Re-render album grid (preserves search focus)
    function renderAlbumGrid() {
      const grid = document.getElementById('album-grid');
      if (!grid) return;
      grid.innerHTML = '';

      const q = state.searchQuery.toLowerCase();
      const albums = q
        ? LIBRARY.albums.filter(a =>
            (a.name && a.name.toLowerCase().includes(q)) ||
            (a.artists && a.artists.some(ar => ar.name && ar.name.toLowerCase().includes(q)))
          )
        : LIBRARY.albums;

      for (const album of albums) {
        const card = document.createElement('div');
        card.className = 'album-card';
        card.dataset.testid = 'album-card';

        const cover = createAlbumCover(album.image_url, album.name, album.name, 'album-cover-large');
        card.appendChild(cover);

        const title = document.createElement('div');
        title.className = 'album-title';
        title.textContent = album.name;
        card.appendChild(title);

        const meta = document.createElement('div');
        meta.className = 'album-meta';
        meta.textContent = formatArtists(album.artists);
        card.appendChild(meta);

        if (album.release_date) {
          const date = document.createElement('div');
          date.className = 'album-meta';
          date.textContent = album.release_date;
          card.appendChild(date);
        }

        grid.appendChild(card);
      }

      if (albums.length === 0) {
        grid.innerHTML = '<div class="empty-state"><div class="empty-state-title">No matches found</div><div class="empty-state-description">Try a different search term.</div></div>';
      }
    }

    // Re-render artist grid (preserves search focus)
    function renderArtistGrid() {
      const grid = document.getElementById('artist-grid');
      if (!grid) return;
      grid.innerHTML = '';

      const q = state.searchQuery.toLowerCase();
      const artists = q
        ? LIBRARY.artists.filter(a =>
            (a.name && a.name.toLowerCase().includes(q)) ||
            (a.genres && a.genres.some(g => g.toLowerCase().includes(q)))
          )
        : LIBRARY.artists;

      for (const artist of artists) {
        const card = document.createElement('div');
        card.className = 'artist-card';
        card.dataset.testid = 'artist-card';

        const avatar = createAlbumCover(artist.image_url, artist.name, artist.name, 'artist-avatar');
        card.appendChild(avatar);

        const name = document.createElement('div');
        name.className = 'artist-name';
        name.textContent = artist.name;
        card.appendChild(name);

        if (artist.genres && artist.genres.length > 0) {
          const genres = document.createElement('div');
          genres.className = 'artist-genres';
          genres.textContent = artist.genres.slice(0, 3).join(', ');
          card.appendChild(genres);
        }

        grid.appendChild(card);
      }

      if (artists.length === 0) {
        grid.innerHTML = '<div class="empty-state"><div class="empty-state-title">No matches found</div><div class="empty-state-description">Try a different search term.</div></div>';
      }
    }

    // Event handlers
    function handleSidebarClick(e) {
      const btn = e.target.closest('[data-action]');
      if (!btn) return;

      const action = btn.dataset.action;

      if (action === 'select-saved') {
        state.viewMode = 'saved';
        state.selectedPlaylistId = null;
        state.searchQuery = '';
        render();
      } else if (action === 'select-playlist') {
        state.viewMode = 'playlist';
        state.selectedPlaylistId = btn.dataset.playlistId;
        state.selectedYear = null;
        state.searchQuery = '';
        render();
      } else if (action === 'select-albums') {
        state.viewMode = 'albums';
        state.selectedPlaylistId = null;
        state.selectedYear = null;
        state.searchQuery = '';
        render();
      } else if (action === 'select-artists') {
        state.viewMode = 'artists';
        state.selectedPlaylistId = null;
        state.selectedYear = null;
        state.searchQuery = '';
        render();
      } else if (action === 'save-copy') {
        saveACopy();
      }
    }

    function handleYearClick(e) {
      const btn = e.target.closest('.year-tab');
      if (!btn) return;

      const year = btn.dataset.year;
      state.selectedYear = year === '' ? null : year;

      // Update active tab without full re-render
      const yearTabs = document.getElementById('year-tabs');
      if (yearTabs) {
        yearTabs.querySelectorAll('.year-tab').forEach(tab => {
          tab.classList.toggle('active', tab.dataset.year === (state.selectedYear || ''));
        });
      }

      // Update section title
      const titleEl = document.querySelector('[data-testid="songs-section-title"]');
      if (titleEl) {
        titleEl.textContent = state.selectedYear ? 'Songs from ' + state.selectedYear : 'All Saved Songs';
      }

      renderSongsTable();
    }

    function handleMainClick(e) {
      const btn = e.target.closest('[data-action]');
      if (!btn) return;

      if (btn.dataset.action === 'clear-year') {
        state.selectedYear = null;
        render();
      }
    }

    // Save a copy of the HTML file
    function saveACopy() {
      const html = document.documentElement.outerHTML;
      const blob = new Blob(['<!DOCTYPE html>' + html], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `my_spotify_library_${new Date().toISOString().split('T')[0]}.html`;
      a.click();
      URL.revokeObjectURL(url);
    }

    // HTML escaping
    function escapeHtml(str) {
      if (!str) return '';
      const div = document.createElement('div');
      div.textContent = str;
      return div.innerHTML;
    }

    // Render everything
    function render() {
      const nav = document.getElementById('nav');
      const main = document.getElementById('main');
      const navScroll = nav ? nav.scrollTop : 0;
      const mainScroll = main ? main.scrollTop : 0;

      renderSidebar();
      renderMain();

      const newNav = document.getElementById('nav');
      if (newNav) newNav.scrollTop = navScroll;
      if (main) main.scrollTop = mainScroll;
    }

    // Lightbox
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = document.getElementById('lightbox-img');

    document.addEventListener('click', function(e) {
      const img = e.target.closest('img.song-cover, img.playlist-cover, img.playlist-header-cover, img.album-cover-large, img.artist-avatar');
      if (img) {
        lightboxImg.src = img.src;
        lightboxImg.alt = img.alt;
        lightbox.classList.add('active');
        e.stopPropagation();
      }
    });

    lightbox.addEventListener('click', function(e) {
      if (e.target !== lightboxImg) {
        lightbox.classList.remove('active');
      }
    });

    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') lightbox.classList.remove('active');
    });

    // Initialize
    render();
  </script>
</body>
</html>
"""
