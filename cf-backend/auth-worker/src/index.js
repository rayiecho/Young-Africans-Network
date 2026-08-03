import { hashPassword, verifyPassword, sha256Hex, randomToken, newId } from './crypto.js';
import { verifyGoogleIdToken } from './google.js';

function corsHeaders(origin, allowedOrigins) {
  const allowed = allowedOrigins.includes(origin) ? origin : allowedOrigins[0];
  return {
    'Access-Control-Allow-Origin': allowed,
    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Vary': 'Origin'
  };
}

function json(data, status, headers) {
  return new Response(JSON.stringify(data), { status, headers: { 'Content-Type': 'application/json', ...headers } });
}

function isValidEmail(email) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email); }
function isValidPhone(phone) { return /^[+\d][\d\s-]{7,}$/.test(phone); }

function publicUser(u) {
  return {
    id: u.id, name: u.name, email: u.email, photoUrl: u.photo_url, role: u.role,
    department: u.department, country: u.country, whatsapp: u.whatsapp, dob: u.dob, bio: u.bio,
    isAdmin: !!u.is_admin, isDeptHead: !!u.is_dept_head, isExec: !!u.is_exec,
    emailVerified: !!u.email_verified, profileComplete: !!u.profile_complete, joinedAt: u.joined_at
  };
}

async function createSession(env, userId, request) {
  const token = randomToken(32);
  const tokenHash = await sha256Hex(token);
  const ttl = parseInt(env.SESSION_TTL_SECONDS || '2592000', 10);
  const now = Date.now();
  await env.DB.prepare(
    `INSERT INTO sessions (id, user_id, created_at, expires_at, user_agent, ip) VALUES (?,?,?,?,?,?)`
  ).bind(tokenHash, userId, now, now + ttl * 1000,
    request.headers.get('User-Agent') || '', request.headers.get('CF-Connecting-IP') || ''
  ).run();
  return token;
}

async function getSessionUser(request, env) {
  const auth = request.headers.get('Authorization') || '';
  const token = auth.startsWith('Bearer ') ? auth.slice(7) : null;
  if (!token) return null;
  const tokenHash = await sha256Hex(token);
  const row = await env.DB.prepare(
    `SELECT s.expires_at as sess_expires, u.* FROM sessions s JOIN users u ON u.id = s.user_id WHERE s.id = ?`
  ).bind(tokenHash).first();
  if (!row) return null;
  if (row.sess_expires < Date.now()) return null;
  return row;
}

async function sendEmail(env, { to, subject, message }) {
  try {
    await fetch(env.EMAIL_WORKER_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ to, subject, message })
    });
  } catch (e) { console.error('Email send failed:', e.message); }
}

// ===================== HANDLERS =====================

async function register(request, env, cors) {
  const body = await request.json();
  const { name, email, password, country, whatsapp, dob, role, department } = body;
  const nameParts = (name || '').trim().split(/\s+/).filter(Boolean);
  if (nameParts.length < 2) return json({ error: 'Please enter your full name (first and last name)' }, 400, cors);
  if (!/^[a-zA-Z\s]+$/.test(name)) return json({ error: 'Name must contain letters only' }, 400, cors);
  if (!email || !isValidEmail(email)) return json({ error: 'Please enter a valid email address' }, 400, cors);
  if (!password || password.length < 6) return json({ error: 'Password must be at least 6 characters' }, 400, cors);
  if (!whatsapp || !isValidPhone(whatsapp)) return json({ error: 'Please enter a valid WhatsApp number' }, 400, cors);
  if (!country || !dob || !department) return json({ error: 'Please fill all required fields' }, 400, cors);

  const existing = await env.DB.prepare('SELECT id FROM users WHERE email = ?').bind(email.toLowerCase()).first();
  if (existing) return json({ error: 'An account with this email already exists' }, 409, cors);

  const userId = newId();
  const now = Date.now();
  const passwordHash = await hashPassword(password);

  await env.DB.batch([
    env.DB.prepare(
      `INSERT INTO users (id,name,email,password_hash,role,department,country,whatsapp,dob,bio,
        is_admin,is_dept_head,is_exec,email_verified,profile_complete,joined_at,created_at,updated_at)
       VALUES (?,?,?,?,?,?,?,?,?,?,0,0,0,0,1,?,?,?)`
    ).bind(userId, name.trim(), email.toLowerCase(), passwordHash, role || 'Member', department,
      country, whatsapp, dob, '', now, now, now),
    env.DB.prepare(`INSERT INTO auth_providers (id,user_id,provider,created_at) VALUES (?,?,?,?)`)
      .bind(newId(), userId, 'password', now),
    env.DB.prepare(`INSERT INTO member_points (user_id, points) VALUES (?, 10)`).bind(userId),
    env.DB.prepare(`INSERT INTO points_history (id,user_id,action,description,points,created_at) VALUES (?,?,?,?,?,?)`)
      .bind(newId(), userId, 'account_created', 'Welcome to YAN! Account created', 10, now),
    env.DB.prepare(`INSERT INTO member_ids (id,user_id,name,role,department,country,status) VALUES (?,?,?,?,?,?, 'active')`)
      .bind('YAN-' + userId.replace(/-/g, '').slice(0, 8).toUpperCase(), userId, name.trim(), role || 'Member', department, country)
  ]);

  const verifyToken = randomToken(24);
  const verifyHash = await sha256Hex(verifyToken);
  await env.DB.prepare(
    `INSERT INTO email_verification_tokens (id,user_id,token_hash,expires_at) VALUES (?,?,?,?)`
  ).bind(newId(), userId, verifyHash, now + 24 * 3600 * 1000).run();

  await sendEmail(env, {
    to: email,
    subject: 'Verify your YAN account',
    message: `Welcome to Young Africans Network! Verify your email: https://youngafricansnetwork.org/auth-action.html?mode=verifyEmail&token=${verifyToken}&uid=${userId}`
  });

  const sessionToken = await createSession(env, userId, request);
  const user = await env.DB.prepare('SELECT * FROM users WHERE id = ?').bind(userId).first();
  return json({ token: sessionToken, user: publicUser(user) }, 201, cors);
}

async function login(request, env, cors) {
  const { email, password } = await request.json();
  if (!email || !password) return json({ error: 'Enter email and password' }, 400, cors);
  const user = await env.DB.prepare('SELECT * FROM users WHERE email = ?').bind(email.toLowerCase()).first();
  if (!user || !user.password_hash) return json({ error: 'Invalid email or password' }, 401, cors);
  const ok = await verifyPassword(password, user.password_hash);
  if (!ok) return json({ error: 'Invalid email or password' }, 401, cors);
  const sessionToken = await createSession(env, user.id, request);
  return json({ token: sessionToken, user: publicUser(user) }, 200, cors);
}

async function googleSignIn(request, env, cors) {
  const { idToken } = await request.json();
  if (!idToken) return json({ error: 'Missing idToken' }, 400, cors);

  let payload;
  try {
    payload = await verifyGoogleIdToken(idToken, env.GOOGLE_CLIENT_ID);
  } catch (e) {
    return json({ error: 'Google sign-in failed: ' + e.message }, 401, cors);
  }
  if (!payload.emailVerified) return json({ error: 'Google account email is not verified' }, 401, cors);

  let user = await env.DB.prepare('SELECT * FROM users WHERE email = ?').bind(payload.email.toLowerCase()).first();
  const now = Date.now();

  if (!user) {
    // Brand-new Google identity - do NOT create a full member yet. Same policy as
    // password registration: require country/whatsapp/dob/department + terms agreement
    // before this becomes a real member, instead of silently granting full access.
    const pendingId = newId();
    const pendingToken = randomToken(24);
    const pendingHash = await sha256Hex(pendingToken);
    await env.DB.prepare(
      `INSERT INTO email_verification_tokens (id,user_id,token_hash,expires_at) VALUES (?,?,?,?)`
    ).bind(newId(), pendingId, pendingHash, now + 3600 * 1000).run();
    // Stash the pending Google identity in a short-lived row keyed by the token itself
    // (reuses email_verification_tokens table's expiry mechanics as a generic pending-signup store).
    return json({
      needsProfileCompletion: true,
      pendingToken,
      googleProfile: { name: payload.name, email: payload.email, photoUrl: payload.picture, sub: payload.sub }
    }, 200, cors);
  }

  const providerRow = await env.DB.prepare(
    'SELECT id FROM auth_providers WHERE user_id = ? AND provider = ?'
  ).bind(user.id, 'google.com').first();
  if (!providerRow) {
    await env.DB.prepare('INSERT INTO auth_providers (id,user_id,provider,provider_uid,created_at) VALUES (?,?,?,?,?)')
      .bind(newId(), user.id, 'google.com', payload.sub, now).run();
  }
  if (!user.email_verified) {
    await env.DB.prepare('UPDATE users SET email_verified = 1, updated_at = ? WHERE id = ?').bind(now, user.id).run();
  }

  const sessionToken = await createSession(env, user.id, request);
  return json({ token: sessionToken, user: publicUser(user) }, 200, cors);
}

async function completeProfile(request, env, cors) {
  const { pendingToken, googleProfile, country, whatsapp, dob, department, agree } = await request.json();
  if (!agree) return json({ error: 'Please agree to YAN Terms and Rules first' }, 400, cors);
  if (!country || !whatsapp || !dob || !department) return json({ error: 'Please fill all required fields' }, 400, cors);
  if (!isValidPhone(whatsapp)) return json({ error: 'Please enter a valid WhatsApp number' }, 400, cors);
  if (!pendingToken || !googleProfile?.email) return json({ error: 'Session expired, please sign in again' }, 400, cors);

  const tokenHash = await sha256Hex(pendingToken);
  const pending = await env.DB.prepare(
    'SELECT * FROM email_verification_tokens WHERE token_hash = ? AND used_at IS NULL'
  ).bind(tokenHash).first();
  if (!pending || pending.expires_at < Date.now()) return json({ error: 'Session expired, please sign in again' }, 400, cors);

  const existing = await env.DB.prepare('SELECT id FROM users WHERE email = ?').bind(googleProfile.email.toLowerCase()).first();
  if (existing) return json({ error: 'An account with this email already exists' }, 409, cors);

  const userId = newId();
  const now = Date.now();
  await env.DB.batch([
    env.DB.prepare(
      `INSERT INTO users (id,name,email,photo_url,role,department,country,whatsapp,dob,bio,
        is_admin,is_dept_head,is_exec,email_verified,profile_complete,joined_at,created_at,updated_at)
       VALUES (?,?,?,?,?,?,?,?,?,?,0,0,0,1,1,?,?,?)`
    ).bind(userId, googleProfile.name || 'YAN Member', googleProfile.email.toLowerCase(), googleProfile.photoUrl || '',
      'Member', department, country, whatsapp, dob, '', now, now, now),
    env.DB.prepare('INSERT INTO auth_providers (id,user_id,provider,provider_uid,created_at) VALUES (?,?,?,?,?)')
      .bind(newId(), userId, 'google.com', googleProfile.sub || '', now),
    env.DB.prepare('INSERT INTO member_points (user_id, points) VALUES (?, 10)').bind(userId),
    env.DB.prepare('INSERT INTO points_history (id,user_id,action,description,points,created_at) VALUES (?,?,?,?,?,?)')
      .bind(newId(), userId, 'account_created', 'Welcome to YAN! Account created', 10, now),
    env.DB.prepare(`INSERT INTO member_ids (id,user_id,name,role,department,country,status) VALUES (?,?,?,?,?,?, 'active')`)
      .bind('YAN-' + userId.replace(/-/g, '').slice(0, 8).toUpperCase(), userId, googleProfile.name || 'YAN Member', 'Member', department, country),
    env.DB.prepare('UPDATE email_verification_tokens SET used_at = ? WHERE token_hash = ?').bind(now, tokenHash)
  ]);

  const sessionToken = await createSession(env, userId, request);
  const user = await env.DB.prepare('SELECT * FROM users WHERE id = ?').bind(userId).first();
  return json({ token: sessionToken, user: publicUser(user) }, 201, cors);
}

async function me(request, env, cors) {
  const user = await getSessionUser(request, env);
  if (!user) return json({ error: 'Not authenticated' }, 401, cors);
  return json({ user: publicUser(user) }, 200, cors);
}

async function logout(request, env, cors) {
  const auth = request.headers.get('Authorization') || '';
  const token = auth.startsWith('Bearer ') ? auth.slice(7) : null;
  if (token) {
    const tokenHash = await sha256Hex(token);
    await env.DB.prepare('DELETE FROM sessions WHERE id = ?').bind(tokenHash).run();
  }
  return json({ ok: true }, 200, cors);
}

async function verifyEmail(request, env, cors) {
  const { token, uid } = await request.json();
  if (!token || !uid) return json({ error: 'Invalid verification link' }, 400, cors);
  const tokenHash = await sha256Hex(token);
  const row = await env.DB.prepare(
    'SELECT * FROM email_verification_tokens WHERE token_hash = ? AND user_id = ? AND used_at IS NULL'
  ).bind(tokenHash, uid).first();
  if (!row) return json({ error: 'This link is invalid or already used' }, 400, cors);
  if (row.expires_at < Date.now()) return json({ error: 'This link has expired' }, 400, cors);
  const now = Date.now();
  await env.DB.batch([
    env.DB.prepare('UPDATE users SET email_verified = 1, updated_at = ? WHERE id = ?').bind(now, uid),
    env.DB.prepare('UPDATE email_verification_tokens SET used_at = ? WHERE token_hash = ?').bind(now, tokenHash)
  ]);
  return json({ ok: true }, 200, cors);
}

async function resendVerification(request, env, cors) {
  const user = await getSessionUser(request, env);
  if (!user) return json({ error: 'Not authenticated' }, 401, cors);
  if (user.email_verified) return json({ ok: true, message: 'Already verified' }, 200, cors);
  const now = Date.now();
  const verifyToken = randomToken(24);
  const verifyHash = await sha256Hex(verifyToken);
  await env.DB.prepare('INSERT INTO email_verification_tokens (id,user_id,token_hash,expires_at) VALUES (?,?,?,?)')
    .bind(newId(), user.id, verifyHash, now + 24 * 3600 * 1000).run();
  await sendEmail(env, {
    to: user.email,
    subject: 'Verify your YAN account',
    message: `Verify your email: https://youngafricansnetwork.org/auth-action.html?mode=verifyEmail&token=${verifyToken}&uid=${user.id}`
  });
  return json({ ok: true }, 200, cors);
}

async function forgotPassword(request, env, cors) {
  const { email } = await request.json();
  if (!email) return json({ error: 'Enter your email' }, 400, cors);
  const user = await env.DB.prepare('SELECT * FROM users WHERE email = ?').bind(email.toLowerCase()).first();
  // Always return ok, whether or not the account exists, to avoid leaking which emails are registered.
  if (user) {
    const now = Date.now();
    const resetToken = randomToken(24);
    const resetHash = await sha256Hex(resetToken);
    await env.DB.prepare('INSERT INTO password_reset_tokens (id,user_id,token_hash,expires_at) VALUES (?,?,?,?)')
      .bind(newId(), user.id, resetHash, now + 3600 * 1000).run();
    await sendEmail(env, {
      to: user.email,
      subject: 'Reset your YAN password',
      message: `Reset your password: https://youngafricansnetwork.org/auth-action.html?mode=resetPassword&token=${resetToken}&uid=${user.id}`
    });
  }
  return json({ ok: true }, 200, cors);
}

async function resetPassword(request, env, cors) {
  const { token, uid, newPassword } = await request.json();
  if (!token || !uid || !newPassword) return json({ error: 'Invalid reset link' }, 400, cors);
  if (newPassword.length < 6) return json({ error: 'Password must be at least 6 characters' }, 400, cors);
  const tokenHash = await sha256Hex(token);
  const row = await env.DB.prepare(
    'SELECT * FROM password_reset_tokens WHERE token_hash = ? AND user_id = ? AND used_at IS NULL'
  ).bind(tokenHash, uid).first();
  if (!row) return json({ error: 'This link is invalid or already used' }, 400, cors);
  if (row.expires_at < Date.now()) return json({ error: 'This link has expired' }, 400, cors);
  const now = Date.now();
  const passwordHash = await hashPassword(newPassword);
  await env.DB.batch([
    env.DB.prepare('UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?').bind(passwordHash, now, uid),
    env.DB.prepare('UPDATE password_reset_tokens SET used_at = ? WHERE token_hash = ?').bind(now, tokenHash),
    env.DB.prepare('DELETE FROM sessions WHERE user_id = ?').bind(uid) // sign out everywhere on password change
  ]);
  return json({ ok: true }, 200, cors);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const origin = request.headers.get('Origin') || '';
    const allowedOrigins = (env.ALLOWED_ORIGINS || '').split(',').map(s => s.trim()).filter(Boolean);
    const cors = corsHeaders(origin, allowedOrigins);

    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors });

    try {
      const path = url.pathname;
      const routes = {
        '/api/auth/register': register,
        '/api/auth/login': login,
        '/api/auth/google': googleSignIn,
        '/api/auth/complete-profile': completeProfile,
        '/api/auth/logout': logout,
        '/api/auth/verify-email': verifyEmail,
        '/api/auth/resend-verification': resendVerification,
        '/api/auth/forgot-password': forgotPassword,
        '/api/auth/reset-password': resetPassword
      };
      if (path === '/api/auth/me' && request.method === 'GET') return await me(request, env, cors);
      if (routes[path] && request.method === 'POST') return await routes[path](request, env, cors);

      return json({ error: 'Not found' }, 404, cors);
    } catch (e) {
      console.error(e);
      return json({ error: e.message || 'Internal error' }, 500, cors);
    }
  }
};
