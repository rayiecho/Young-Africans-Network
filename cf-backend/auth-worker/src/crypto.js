// Password hashing (PBKDF2-SHA256) and token utilities using the Workers-native Web Crypto API.
// No external deps - avoids pulling in bcrypt/etc which don't run in the Workers runtime anyway.

const PBKDF2_ITERATIONS = 100000;

function bytesToHex(bytes) {
  return [...bytes].map(b => b.toString(16).padStart(2, '0')).join('');
}

function hexToBytes(hex) {
  const bytes = new Uint8Array(hex.length / 2);
  for (let i = 0; i < bytes.length; i++) bytes[i] = parseInt(hex.substr(i * 2, 2), 16);
  return bytes;
}

export async function hashPassword(password, saltHex) {
  const enc = new TextEncoder();
  const salt = saltHex ? hexToBytes(saltHex) : crypto.getRandomValues(new Uint8Array(16));
  const keyMaterial = await crypto.subtle.importKey('raw', enc.encode(password), 'PBKDF2', false, ['deriveBits']);
  const bits = await crypto.subtle.deriveBits(
    { name: 'PBKDF2', salt, iterations: PBKDF2_ITERATIONS, hash: 'SHA-256' },
    keyMaterial, 256
  );
  return `${bytesToHex(salt)}:${bytesToHex(new Uint8Array(bits))}`;
}

// stored is either our own "<saltHex>:<hashHex>" (PBKDF2) or a migrated Firebase
// account stored as "fbscrypt$<saltB64>$<hashB64>" (see firebase-scrypt.js). Returns
// { ok, isLegacy } so callers can transparently re-hash to PBKDF2 on a successful
// legacy login, draining the legacy population over time.
export async function verifyPasswordWithMigration(password, stored, verifyLegacy) {
  if (!stored) return { ok: false, isLegacy: false };
  if (stored.startsWith('fbscrypt$')) {
    const [, saltB64, hashB64] = stored.split('$');
    const ok = await verifyLegacy(password, hashB64, saltB64);
    return { ok, isLegacy: true };
  }
  if (!stored.includes(':')) return { ok: false, isLegacy: false };
  const [saltHex] = stored.split(':');
  const computed = await hashPassword(password, saltHex);
  return { ok: timingSafeEqual(computed, stored), isLegacy: false };
}

function timingSafeEqual(a, b) {
  if (a.length !== b.length) return false;
  let result = 0;
  for (let i = 0; i < a.length; i++) result |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return result === 0;
}

export async function sha256Hex(input) {
  const enc = new TextEncoder();
  const digest = await crypto.subtle.digest('SHA-256', enc.encode(input));
  return bytesToHex(new Uint8Array(digest));
}

export function randomToken(bytes = 32) {
  return bytesToHex(crypto.getRandomValues(new Uint8Array(bytes)));
}

export function newId() {
  return crypto.randomUUID();
}
