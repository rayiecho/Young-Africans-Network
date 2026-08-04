// Mints a Firebase Auth custom token so a D1-authenticated user can also get a real
// Firebase Auth session client-side (via signInWithCustomToken), keeping every
// not-yet-migrated Firestore feature in community.html working unchanged during the
// transition. Firebase verifies these tokens purely by their RS256 signature against
// the service account's public key - no network call to Firebase needed to mint one.

function pemToArrayBuffer(pem) {
  const b64 = pem.replace(/-----BEGIN PRIVATE KEY-----/, '')
    .replace(/-----END PRIVATE KEY-----/, '')
    .replace(/\s+/g, '');
  const bin = atob(b64);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return bytes.buffer;
}

function base64UrlEncode(bytesOrString) {
  let bytes;
  if (typeof bytesOrString === 'string') bytes = new TextEncoder().encode(bytesOrString);
  else bytes = bytesOrString;
  let bin = '';
  for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
  return btoa(bin).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

let cachedKey = null;
let cachedKeyId = null;

async function getSigningKey(privateKeyPem, keyId) {
  if (cachedKey && cachedKeyId === keyId) return cachedKey;
  const keyData = pemToArrayBuffer(privateKeyPem);
  cachedKey = await crypto.subtle.importKey(
    'pkcs8', keyData, { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' }, false, ['sign']
  );
  cachedKeyId = keyId;
  return cachedKey;
}

// serviceAccount: parsed serviceAccount.json ({ client_email, private_key, private_key_id, ... })
export async function mintFirebaseCustomToken(serviceAccount, uid, extraClaims) {
  const now = Math.floor(Date.now() / 1000);
  const header = { alg: 'RS256', typ: 'JWT' };
  const payload = {
    iss: serviceAccount.client_email,
    sub: serviceAccount.client_email,
    aud: 'https://identitytoolkit.googleapis.com/google.identity.identitytoolkit.v1.IdentityToolkit',
    iat: now,
    exp: now + 3600,
    uid,
    ...(extraClaims ? { claims: extraClaims } : {})
  };
  const headerB64 = base64UrlEncode(JSON.stringify(header));
  const payloadB64 = base64UrlEncode(JSON.stringify(payload));
  const signingInput = `${headerB64}.${payloadB64}`;

  const key = await getSigningKey(serviceAccount.private_key, serviceAccount.private_key_id);
  const signature = await crypto.subtle.sign(
    'RSASSA-PKCS1-v1_5', key, new TextEncoder().encode(signingInput)
  );
  const sigB64 = base64UrlEncode(new Uint8Array(signature));
  return `${signingInput}.${sigB64}`;
}
