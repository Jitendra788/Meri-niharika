/**
 * Copies articles + site settings + images into public/ for Vercel when Render is not connected.
 */
import { cpSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = dirname(fileURLToPath(import.meta.url));
const webRoot = join(root, '..');
const repoRoot = join(webRoot, '..', '..');
const publicDir = join(webRoot, 'public');
const dataDir = join(publicDir, 'data');

const manifestPath = join(repoRoot, 'backend', 'uploads', 'articles_manifest.json');
const sitePath = join(repoRoot, 'backend', 'uploads', 'site_settings.json');
const imagesSrc = join(repoRoot, 'backend', 'uploads', 'images');
const imagesDest = join(publicDir, 'uploads', 'images');

mkdirSync(dataDir, { recursive: true });

const raw = JSON.parse(readFileSync(manifestPath, 'utf8'));
const published = raw.filter((a) => a.status === 'published');
writeFileSync(join(dataDir, 'articles.json'), JSON.stringify(published), 'utf8');

writeFileSync(join(dataDir, 'site.json'), readFileSync(sitePath, 'utf8'), 'utf8');

mkdirSync(dirname(imagesDest), { recursive: true });
cpSync(imagesSrc, imagesDest, { recursive: true, force: true });

console.log(`[sync-static-data] ${published.length} articles, site.json, images → public/`);
