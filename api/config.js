/** Vercel serverless — runtime BACKEND_URL (Settings → Environment Variables). */
module.exports = (req, res) => {
  const apiBaseUrl = (process.env.BACKEND_URL || '').trim().replace(/\/$/, '');
  res.setHeader('Cache-Control', 'no-store');
  res.status(200).json({ apiBaseUrl });
};
