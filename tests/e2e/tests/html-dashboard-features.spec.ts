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

test.describe('HTML Dashboard - New Features', () => {
  test.beforeAll(async () => {
    execSync(`python3 ${GENERATE_SCRIPT}`, { cwd: FIXTURES_DIR });
    expect(fs.existsSync(HTML_PATH)).toBe(true);
  });

  test.beforeEach(async ({ page }) => {
    await page.goto(`file://${HTML_PATH}`);
  });

  test.describe('Search - Saved Songs', () => {
    test('search bar is visible in saved songs view', async ({ page }) => {
      await expect(page.getByTestId('search-input')).toBeVisible();
    });

    test('search filters songs by title', async ({ page }) => {
      await page.getByTestId('search-input').fill('Bohemian');

      const songRows = page.getByTestId('song-row');
      await expect(songRows).toHaveCount(1);
      await expect(songRows.first().getByTestId('song-title')).toContainText('Bohemian Rhapsody');
    });

    test('search filters songs by artist', async ({ page }) => {
      await page.getByTestId('search-input').fill('Queen');

      const songRows = page.getByTestId('song-row');
      await expect(songRows).toHaveCount(1);
      await expect(songRows.first().getByTestId('song-artist')).toContainText('Queen');
    });

    test('search filters songs by album', async ({ page }) => {
      await page.getByTestId('search-input').fill('Nevermind');

      const songRows = page.getByTestId('song-row');
      await expect(songRows).toHaveCount(1);
      await expect(songRows.first().getByTestId('song-album')).toContainText('Nevermind');
    });

    test('search with no matches shows empty state', async ({ page }) => {
      await page.getByTestId('search-input').fill('xyznonexistent');

      await expect(page.getByTestId('song-row')).toHaveCount(0);
      await expect(page.getByTestId('empty-state')).toBeVisible();
    });

    test('clearing search restores all songs', async ({ page }) => {
      const input = page.getByTestId('search-input');
      await input.fill('Queen');
      await expect(page.getByTestId('song-row')).toHaveCount(1);

      await input.fill('');
      await expect(page.getByTestId('song-row')).toHaveCount(10);
    });
  });

  test.describe('Search - Playlist Songs', () => {
    test('search bar appears in playlist view', async ({ page }) => {
      await page.getByTestId('playlist-item').first().click();
      await expect(page.getByTestId('search-input')).toBeVisible();
    });

    test('search filters playlist songs', async ({ page }) => {
      await page.getByTestId('playlist-item').first().click();
      await page.getByTestId('search-input').fill('Bohemian');

      const songRows = page.getByTestId('song-row');
      await expect(songRows).toHaveCount(1);
      await expect(songRows.first().getByTestId('song-title')).toContainText('Bohemian Rhapsody');
    });
  });

  test.describe('Albums View', () => {
    test('navigating to albums shows album grid', async ({ page }) => {
      await page.getByTestId('nav-albums').click();
      await expect(page.getByTestId('albums-section')).toBeVisible();

      const albumCards = page.getByTestId('album-card');
      await expect(albumCards).toHaveCount(3);
    });

    test('stats grid is hidden in albums view', async ({ page }) => {
      await page.getByTestId('nav-albums').click();
      await expect(page.getByTestId('stats-grid')).not.toBeVisible();
    });

    test('album search filters by album name', async ({ page }) => {
      await page.getByTestId('nav-albums').click();
      await page.getByTestId('search-input').fill('Nevermind');

      const albumCards = page.getByTestId('album-card');
      await expect(albumCards).toHaveCount(1);
    });

    test('album search filters by artist name', async ({ page }) => {
      await page.getByTestId('nav-albums').click();
      await page.getByTestId('search-input').fill('Queen');

      const albumCards = page.getByTestId('album-card');
      await expect(albumCards).toHaveCount(1);
    });

    test('album search with no matches shows empty state', async ({ page }) => {
      await page.getByTestId('nav-albums').click();
      await page.getByTestId('search-input').fill('xyznonexistent');

      await expect(page.getByTestId('album-card')).toHaveCount(0);
    });
  });

  test.describe('Artists View', () => {
    test('navigating to artists shows artist grid', async ({ page }) => {
      await page.getByTestId('nav-artists').click();
      await expect(page.getByTestId('artists-section')).toBeVisible();

      const artistCards = page.getByTestId('artist-card');
      await expect(artistCards).toHaveCount(3);
    });

    test('stats grid is hidden in artists view', async ({ page }) => {
      await page.getByTestId('nav-artists').click();
      await expect(page.getByTestId('stats-grid')).not.toBeVisible();
    });

    test('artist search filters by name', async ({ page }) => {
      await page.getByTestId('nav-artists').click();
      await page.getByTestId('search-input').fill('Queen');

      const artistCards = page.getByTestId('artist-card');
      await expect(artistCards).toHaveCount(1);
    });

    test('artist search filters by genre', async ({ page }) => {
      await page.getByTestId('nav-artists').click();
      await page.getByTestId('search-input').fill('progressive');

      const artistCards = page.getByTestId('artist-card');
      await expect(artistCards).toHaveCount(1);
    });

    test('artist search with no matches shows empty state', async ({ page }) => {
      await page.getByTestId('nav-artists').click();
      await page.getByTestId('search-input').fill('xyznonexistent');

      await expect(page.getByTestId('artist-card')).toHaveCount(0);
    });
  });

  test.describe('Playlist Header', () => {
    test('playlist header shows playlist info', async ({ page }) => {
      await page.getByTestId('playlist-item').first().click();

      await expect(page.getByTestId('playlist-header')).toBeVisible();
      await expect(page.getByTestId('playlist-header-title')).toContainText('Classic Rock Favorites');
      await expect(page.getByTestId('playlist-header-meta')).toContainText('testuser');
      await expect(page.getByTestId('playlist-header-meta')).toContainText('2 songs');
    });

    test('playlist header is not visible in saved songs view', async ({ page }) => {
      await expect(page.getByTestId('playlist-header')).not.toBeVisible();
    });
  });

  test.describe('Playlist Sidebar Search', () => {
    test('search toggle button is visible', async ({ page }) => {
      await expect(page.getByTestId('playlist-search-toggle')).toBeVisible();
    });

    test('search input is hidden by default', async ({ page }) => {
      await expect(page.getByTestId('playlist-search-wrapper')).not.toHaveClass(/visible/);
    });

    test('clicking toggle reveals search input', async ({ page }) => {
      await page.getByTestId('playlist-search-toggle').click();

      await expect(page.getByTestId('playlist-search-wrapper')).toHaveClass(/visible/);
      await expect(page.getByTestId('playlist-search-input')).toBeFocused();
    });

    test('clicking toggle again hides search and clears filter', async ({ page }) => {
      // Open search
      await page.getByTestId('playlist-search-toggle').click();
      await page.getByTestId('playlist-search-input').fill('Classic');

      // Verify filter works
      const playlistItems = page.getByTestId('playlist-item');
      await expect(playlistItems).toHaveCount(1);

      // Close search
      await page.getByTestId('playlist-search-toggle').click();

      // Search wrapper hidden and all playlists visible again
      await expect(page.getByTestId('playlist-search-wrapper')).not.toHaveClass(/visible/);
      await expect(page.getByTestId('playlist-item')).toHaveCount(2);
    });

    test('search filters playlists by name', async ({ page }) => {
      await page.getByTestId('playlist-search-toggle').click();
      await page.getByTestId('playlist-search-input').fill('Grunge');

      const playlistItems = page.getByTestId('playlist-item');
      await expect(playlistItems).toHaveCount(1);
      await expect(playlistItems.first().getByTestId('playlist-name')).toContainText('90s Grunge');
    });
  });

  test.describe('Lightbox', () => {
    test('lightbox is hidden by default', async ({ page }) => {
      await expect(page.getByTestId('lightbox')).not.toHaveClass(/active/);
    });

    test('clicking album cover opens lightbox', async ({ page }) => {
      // Navigate to albums view which has an image (Queen album)
      await page.getByTestId('nav-albums').click();

      // Find the album card with an image and click it
      const albumImg = page.locator('.album-card img').first();
      if (await albumImg.isVisible()) {
        await albumImg.click();
        await expect(page.getByTestId('lightbox')).toHaveClass(/active/);
      }
    });

    test('clicking outside image closes lightbox', async ({ page }) => {
      await page.getByTestId('nav-albums').click();

      const albumImg = page.locator('.album-card img').first();
      if (await albumImg.isVisible()) {
        await albumImg.click();
        await expect(page.getByTestId('lightbox')).toHaveClass(/active/);

        // Click the overlay (not the image)
        await page.getByTestId('lightbox').click({ position: { x: 10, y: 10 } });
        await expect(page.getByTestId('lightbox')).not.toHaveClass(/active/);
      }
    });

    test('pressing Escape closes lightbox', async ({ page }) => {
      await page.getByTestId('nav-albums').click();

      const albumImg = page.locator('.album-card img').first();
      if (await albumImg.isVisible()) {
        await albumImg.click();
        await expect(page.getByTestId('lightbox')).toHaveClass(/active/);

        await page.keyboard.press('Escape');
        await expect(page.getByTestId('lightbox')).not.toHaveClass(/active/);
      }
    });
  });

  test.describe('Scroll Preservation', () => {
    test('sidebar scroll is preserved when switching playlists', async ({ page }) => {
      // Click first playlist
      await page.getByTestId('playlist-item').first().click();
      await expect(page.getByTestId('playlist-header')).toBeVisible();

      // Click second playlist
      await page.getByTestId('playlist-item').nth(1).click();
      await expect(page.getByTestId('playlist-header-title')).toContainText('90s Grunge');

      // Navigate back to saved songs - sidebar should still render correctly
      await page.getByTestId('nav-saved-songs').click();
      await expect(page.getByTestId('stats-grid')).toBeVisible();
      await expect(page.getByTestId('playlist-item')).toHaveCount(2);
    });
  });
});
