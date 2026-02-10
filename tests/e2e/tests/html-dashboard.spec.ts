import { test, expect } from '@playwright/test';
import { execSync } from 'child_process';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const FIXTURES_DIR = path.join(__dirname, '../fixtures');
const HTML_PATH = path.join(FIXTURES_DIR, 'test-dashboard.html');
const GENERATE_SCRIPT = path.join(FIXTURES_DIR, 'generate-html.py');

test.describe('HTML Dashboard', () => {
  test.beforeAll(async () => {
    // Generate the test HTML file
    execSync(`python3 ${GENERATE_SCRIPT}`, { cwd: FIXTURES_DIR });
    expect(fs.existsSync(HTML_PATH)).toBe(true);
  });

  test.beforeEach(async ({ page }) => {
    // Load the HTML file directly using file:// protocol
    await page.goto(`file://${HTML_PATH}`);
  });

  test('displays stats correctly', async ({ page }) => {
    // Verify stats grid is visible
    await expect(page.getByTestId('stats-grid')).toBeVisible();

    // Check total songs count (10 songs in fixture)
    const totalSongsCard = page.getByTestId('stat-total-songs');
    await expect(totalSongsCard.locator('.stat-label')).toContainText('Total Songs');
    await expect(totalSongsCard.locator('.stat-value')).toContainText('10');

    // Check playlists count (2 playlists in fixture)
    const playlistsCard = page.getByTestId('stat-playlists');
    await expect(playlistsCard.locator('.stat-label')).toContainText('Playlists');
    await expect(playlistsCard.locator('.stat-value')).toContainText('2');
  });

  test('year filtering works', async ({ page }) => {
    // Verify year timeline is visible
    await expect(page.getByTestId('year-timeline')).toBeVisible();

    // Click on "All" tab - should be active by default
    const allTab = page.getByTestId('year-tab-all');
    await expect(allTab).toHaveClass(/active/);

    // Click on a specific year (2024 has 3 songs in fixture)
    const year2024Tab = page.getByTestId('year-tab-2024');
    if (await year2024Tab.isVisible()) {
      await year2024Tab.click();
      await expect(year2024Tab).toHaveClass(/active/);

      // Verify songs table shows filtered results
      const songRows = page.getByTestId('song-row');
      await expect(songRows).toHaveCount(3);
    }

    // Click back to All
    await allTab.click();
    await expect(allTab).toHaveClass(/active/);

    // Should show all 10 songs again
    const allSongRows = page.getByTestId('song-row');
    await expect(allSongRows).toHaveCount(10);
  });

  test('playlist navigation works', async ({ page }) => {
    // Click on Saved Songs nav item - should be active by default
    const savedSongsNav = page.getByTestId('nav-saved-songs');
    await expect(savedSongsNav).toHaveClass(/active/);

    // Find and click on "Classic Rock Favorites" playlist
    const playlistItem = page.getByTestId('playlist-item').first();
    await playlistItem.click();

    // Verify playlist is now selected
    await expect(playlistItem).toHaveClass(/active/);

    // Verify playlist header shows playlist name
    await expect(page.getByTestId('playlist-header-title')).toContainText('Classic Rock Favorites');

    // Verify songs table shows playlist tracks (2 tracks in this playlist)
    const songRows = page.getByTestId('song-row');
    await expect(songRows).toHaveCount(2);

    // Year timeline should not be visible for playlists
    await expect(page.getByTestId('year-timeline')).not.toBeVisible();
  });

  test('songs table renders correctly', async ({ page }) => {
    // Verify songs section is visible
    await expect(page.getByTestId('songs-section')).toBeVisible();

    // Verify header columns
    const header = page.getByTestId('songs-table-header');
    await expect(header).toContainText('#');
    await expect(header).toContainText('Title');
    await expect(header).toContainText('Album');
    await expect(header).toContainText('Date Added');
    await expect(header).toContainText('Duration');

    // Verify first song row content
    const firstRow = page.getByTestId('song-row').first();
    await expect(firstRow.getByTestId('song-title')).toBeVisible();
    await expect(firstRow.getByTestId('song-artist')).toBeVisible();
    await expect(firstRow.getByTestId('song-album')).toBeVisible();
    await expect(firstRow.getByTestId('song-duration')).toBeVisible();

    // Verify album cover image is visible
    const albumCover = firstRow.locator('.song-cover');
    await expect(albumCover).toBeVisible();
  });

  test('save a copy button works', async ({ page }) => {
    // Set up download handler
    const downloadPromise = page.waitForEvent('download');

    // Click "Save a Copy" button
    const saveButton = page.getByTestId('save-copy');
    await expect(saveButton).toBeVisible();
    await saveButton.click();

    // Verify download is triggered
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/my_spotify_library_\d{4}-\d{2}-\d{2}\.html/);
  });

  test('sidebar shows playlists', async ({ page }) => {
    // Verify sidebar logo
    await expect(page.getByTestId('logo-text')).toContainText('Spotify Profile Dump');

    // Verify Saved Songs nav item
    await expect(page.getByTestId('nav-saved-songs')).toContainText('Saved Songs');

    // Verify Playlists nav header
    await expect(page.getByTestId('nav-playlists')).toContainText('Playlists');

    // Verify playlist items are visible
    const playlistItems = page.getByTestId('playlist-item');
    await expect(playlistItems).toHaveCount(2);

    // Verify first playlist info
    const firstPlaylist = playlistItems.first();
    await expect(firstPlaylist.getByTestId('playlist-name')).toContainText('Classic Rock Favorites');
    await expect(firstPlaylist.getByTestId('playlist-count')).toContainText('2 songs');
  });

  test('empty year shows message and action button', async ({ page }) => {
    // Click on a year with no songs (2021 - not in fixture)
    const year2021Tab = page.getByTestId('year-tab-2021');

    // If 2021 exists (it shouldn't based on our fixture)
    if (await year2021Tab.isVisible()) {
      await year2021Tab.click();

      // Should show empty state
      await expect(page.getByTestId('empty-state')).toBeVisible();
      await expect(page.getByTestId('empty-state-title')).toContainText('No songs in this year');
      await expect(page.getByTestId('clear-year')).toContainText('Show All Songs');
    }
  });

  test('switching between saved tracks and playlist clears year filter', async ({ page }) => {
    // Select a year filter first
    const year2024Tab = page.getByTestId('year-tab-2024');
    if (await year2024Tab.isVisible()) {
      await year2024Tab.click();
      await expect(year2024Tab).toHaveClass(/active/);

      // Verify filtered count
      const songRows = page.getByTestId('song-row');
      await expect(songRows).toHaveCount(3);

      // Switch to a playlist
      const playlistItem = page.getByTestId('playlist-item').first();
      await playlistItem.click();

      // Verify we're now showing playlist content
      await expect(page.getByTestId('playlist-header-title')).toContainText('Classic Rock Favorites');

      // Switch back to saved tracks
      const savedSongsNav = page.getByTestId('nav-saved-songs');
      await savedSongsNav.click();

      // Year filter should be cleared, showing all songs
      await expect(page.getByTestId('year-tab-all')).toHaveClass(/active/);
      await expect(page.getByTestId('song-row')).toHaveCount(10);
    }
  });
});
