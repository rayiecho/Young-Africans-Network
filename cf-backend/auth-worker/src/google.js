// Verifies a Google Sign-In ID token server-side (replaces Firebase Auth's Google provider).
// Fetches Google's published JWKS, checks the RS256 signature, then validates iss/aud/exp.

const JWKS_URL = 'https://www.googleapis.com/oauth2/v3/certs';
const ISSUERS = new Set(['accounts.google.com', 'https://accounts.google.com']);

function base64UrlToBytes(b64url) {
  const b64 = b64url.replace(/-/g, '+').replace(/_/g, '/').padEnd(Math.ceil(b64url.length / 4) * 4, '=');
  const bin = atob(b64);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return bytes;
}

function base64UrlToJson(b64url) {
  return JSON.parse(new TextDecoder().decode(base64UrlToBytes(b64url)));
}

let cachedJwks = null;
let cachedJwksAt = 0;

async function getJwks() {
  if (cachedJwks && Date.now() - cachedJwksAt < 3600_000) return cachedJwks;
  const res = await fetch(JWKS_URL);
  if (!res.ok) throw new Error('Failed to fetch Google JWKS');
  cachedJwks = await res.json();
  cachedJwksAt = Date.now();
  return cachedJwks;
}

export async function verifyGoogleIdToken(idToken, clientId) {
  const parts = idToken.split('.');
  if (parts.length !== 3) throw new Error('Malformed ID token');
  const [headerB64, payloadB64, sigB64] = parts;
  const header = base64UrlToJson(headerB64);
  const payload = base64UrlToJson(payloadB64);

  if (!ISSUERS.has(payload.iss)) throw new Error('Invalid issuer');
  if (payload.aud !== clientId) throw new Error('Invalid audience');
  if (payload.exp * 1000 < Date.now()) throw new Error('Token expired');

  const jwks = await getJwks();
  const jwk = jwks.keys.find(k => k.kid === header.kid);
  if (!jwk) throw new Error('No matching signing key');

  const key = await crypto.subtle.importKey(
    'jwk', jwk, { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' }, false, ['verify']
  );
  const signature = base64UrlToBytes(sigB64);
  const signedData = new TextEncoder().encode(`${headerB64}.${payloadB64}`);
  const valid = await crypto.subtle.verify('RSASSA-PKCS1-v1_5', key, signature, signedData);
  if (!valid) throw new Error('Invalid signature');

  return {
    sub: payload.sub,
    email: payload.email,
    emailVerified: !!payload.email_verified,
    name: payload.name,
    picture: payload.picture
  };
}
