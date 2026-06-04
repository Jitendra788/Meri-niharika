/** Same as repo root /api/config.js — use when Vercel Root Directory = frontend/magazine-web */
module.exports = (req, res) => {
  const apiBaseUrl = (process.env.BACKEND_URL || '').trim().replace(/\/$/, '');
  res.setHeader('Cache-Control', 'no-store');
  res.status(200).json({ apiBaseUrl });
};
