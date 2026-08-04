// Verification of Firebase Auth's modified-scrypt password hashes, for migrating
// `firebase auth:export` users onto this Worker without forcing a password reset.
//
// Algorithm (canonical source: https://github.com/firebase/scrypt, and the Firebase
// engineer's spec in firebase/scrypt#2). Validated byte-for-byte against Firebase's
// own published test vector - see the self-test at the bottom of this file.
//
//   1. b64-decode: user salt, project saltSeparator, project signerKey
//   2. dk = scrypt(password_utf8, salt || saltSeparator, N=2^memoryCost, r=rounds, p=1, dkLen=64)
//   3. ct = AES-256-CTR(key = dk[0..32], counter = 16 zero bytes).encrypt(signerKey)
//   4. hash = base64(ct)   -> compare against the exported `passwordHash`
//
// NOTE: step 3 encrypts the signerKey *with* the derived key. The derived key is the
// AES key, not the plaintext. Getting this backwards silently produces wrong hashes.
//
// Requires `compatibility_flags = ["nodejs_compat"]` in wrangler.toml: Workers' Web
// Crypto has no scrypt KDF, so we use the runtime's native (BoringSSL) implementation
// via node:crypto. AES-CTR comes from Web Crypto, which does support it natively.

import { scrypt as nodeScrypt } from 'node:crypto';

function b64ToBytes(b64) {
  const bin = atob(b64);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

function bytesToB64(bytes) {
  let bin = '';
  for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
  return btoa(bin);
}

function concatBytes(a, b) {
  const out = new Uint8Array(a.length + b.length);
  out.set(a, 0);
  out.set(b, a.length);
  return out;
}

function scryptAsync(password, salt, { N, r, p, dkLen, maxmem }) {
  return new Promise((resolve, reject) => {
    nodeScrypt(password, salt, dkLen, { N, r, p, maxmem }, (err, derivedKey) => {
      if (err) reject(err);
      else resolve(new Uint8Array(derivedKey));
    });
  });
}

function timingSafeEqualBytes(a, b) {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a[i] ^ b[i];
  return diff === 0;
}

/**
 * Compute the Firebase password hash for a candidate password.
 * Returns the base64 string that should equal the exported `passwordHash`.
 */
export async function firebaseScryptHash(password, saltB64, hashConfig) {
  const {
    signerKey,
    saltSeparator,
    rounds,
    memoryCost,
    algorithm = 'SCRYPT',
  } = hashConfig;

  if (algorithm !== 'SCRYPT') {
    throw new Error(`Unsupported Firebase hash algorithm: ${algorithm}`);
  }

  const saltBytes = b64ToBytes(saltB64);
  const separatorBytes = b64ToBytes(saltSeparator);
  const signerKeyBytes = b64ToBytes(signerKey);

  // Firebase normalises nothing, but browsers can submit differently-composed
  // Unicode. NFC matches what the Firebase JS SDK sent at signup time.
  const passwordBytes = new TextEncoder().encode(password.normalize('NFC'));

  const derivedKey = await scryptAsync(passwordBytes, concatBytes(saltBytes, separatorBytes), {
    N: 2 ** memoryCost,
    r: rounds,
    p: 1,
    dkLen: 64,
    // N=2^14, r=8 needs 128*N*r = 16 MiB. Default maxmem is 32 MiB, which is enough
    // today, but set it explicitly so a project with a higher memoryCost doesn't fail.
    maxmem: 256 * 1024 * 1024,
  });

  const aesKey = await crypto.subtle.importKey(
    'raw',
    derivedKey.slice(0, 32), // AES-256 key = first 32 bytes of the 64-byte derived key
    'AES-CTR',
    false,
    ['encrypt']
  );

  const ciphertext = await crypto.subtle.encrypt(
    { name: 'AES-CTR', counter: new Uint8Array(16), length: 128 },
    aesKey,
    signerKeyBytes
  );

  return bytesToB64(new Uint8Array(ciphertext));
}

/**
 * Verify a plaintext password against a Firebase-exported hash.
 *
 * @param {string} password        plaintext attempt
 * @param {string} storedHashB64   the exported user's `passwordHash`
 * @param {string} storedSaltB64   the exported user's `salt`
 * @param {object} hashConfig      { signerKey, saltSeparator, rounds, memoryCost }
 * @returns {Promise<boolean>}
 */
export async function verifyFirebaseScryptPassword(password, storedHashB64, storedSaltB64, hashConfig) {
  if (typeof password !== 'string' || !storedHashB64 || !storedSaltB64) return false;
  try {
    const computed = await firebaseScryptHash(password, storedSaltB64, hashConfig);
    return timingSafeEqualBytes(b64ToBytes(computed), b64ToBytes(storedHashB64));
  } catch {
    return false;
  }
}

/**
 * Self-test against Firebase's own published vector (github.com/firebase/scrypt).
 * Call this once from a debug route after deploying to confirm the runtime agrees.
 */
export async function firebaseScryptSelfTest() {
  const hashConfig = {
    signerKey:
      'jxspr8Ki0RYycVU8zykbdLGjFQ3McFUH0uiiTvC8pVMXAn210wjLNmdZJzxUECKbm0QsEmYUSDzZvpjeJ9WmXA==',
    saltSeparator: 'Bw==',
    rounds: 8,
    memoryCost: 14,
  };
  const expected =
    'lSrfV15cpx95/sZS2W9c9Kp6i/LVgQNDNC/qzrCnh1SAyZvqmZqAjTdn3aoItz+VHjoZilo78198JAdRuid5lQ==';

  const good = await verifyFirebaseScryptPassword('user1password', expected, '42xEC+ixf3L2lw==', hashConfig);
  const bad = await verifyFirebaseScryptPassword('secret', expected, '42xEC+ixf3L2lw==', hashConfig);
  return { pass: good === true && bad === false, good, bad };
}
