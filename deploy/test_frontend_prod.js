/**
 * Simple frontend production test using Node.js fetch (Node 18+).
 * It calls backend endpoints through NEXT_PUBLIC_API_BASE_URL to verify connectivity.
 *
 * Usage:
 *   node deploy/test_frontend_prod.js
 */

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
const TOKEN = process.env.TEST_JWT_TOKEN || '';

async function call(path, opts = {}) {
  const headers = { Accept: 'application/json', ...(opts.headers || {}) };
  if (TOKEN) headers.Authorization = `Bearer ${TOKEN}`;
  const res = await fetch(`${BASE}${path}`, { ...opts, headers });
  const contentType = res.headers.get('content-type') || '';
  const body = contentType.includes('application/json') ? await res.json() : await res.text();
  return { status: res.status, body };
}

(async () => {
  console.log('Using API base:', BASE);
  try {
    let r = await call('/health');
    console.log('\n=== GET /health ===');
    console.log(r);
  } catch (e) {
    console.error('Health failed', e);
  }

  try {
    let r = await call('/api/v1/transactions');
    console.log('\n=== GET /api/v1/transactions ===');
    console.log(r);
  } catch (e) {
    console.error('Transactions failed', e);
  }
})();
