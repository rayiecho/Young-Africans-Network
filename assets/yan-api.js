// Shared client for the new Cloudflare Workers backend (replaces direct Firebase SDK calls).
// Include with <script src="/assets/yan-api.js"></script> - exposes window.YanAPI.
// Session tokens are stored in localStorage and sent as a Bearer token, since the API
// worker lives on a different origin (workers.dev) than the site - cross-site cookies
// would need SameSite=None and are increasingly unreliable in browsers, so a bearer
// token in localStorage (mirroring how mobile/SPA clients typically talk to a separate
// API host) avoids that entirely.

(function () {
  const AUTH_BASE = 'https://yan-auth-worker.youngafricansn.workers.dev';
  const TOKEN_KEY = 'yan_session_token';
  const USER_CACHE_KEY = 'yan_session_user';

  function getToken() { return localStorage.getItem(TOKEN_KEY); }
  function setToken(token) { token ? localStorage.setItem(TOKEN_KEY, token) : localStorage.removeItem(TOKEN_KEY); }
  function getCachedUser() {
    try { return JSON.parse(localStorage.getItem(USER_CACHE_KEY) || 'null'); } catch (e) { return null; }
  }
  function setCachedUser(user) {
    user ? localStorage.setItem(USER_CACHE_KEY, JSON.stringify(user)) : localStorage.removeItem(USER_CACHE_KEY);
  }

  async function request(path, { method = 'GET', body, auth = true } = {}) {
    const headers = { 'Content-Type': 'application/json' };
    if (auth) {
      const token = getToken();
      if (token) headers['Authorization'] = 'Bearer ' + token;
    }
    const res = await fetch(AUTH_BASE + path, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined
    });
    let data = {};
    try { data = await res.json(); } catch (e) {}
    if (!res.ok) throw new Error(data.error || ('Request failed (' + res.status + ')'));
    return data;
  }

  function applySession(data) {
    if (data.token) setToken(data.token);
    if (data.user) setCachedUser(data.user);
    // data.firebaseToken (if present) is a Firebase custom token - the caller is
    // responsible for calling signInWithCustomToken(auth, data.firebaseToken) to
    // bridge into Firebase Auth for pages still using the Firestore SDK directly.
    return data;
  }

  const YanAPI = {
    // ---- state ----
    isLoggedIn() { return !!getToken(); },
    getCachedUser,

    // ---- auth ----
    async register({ name, email, password, country, whatsapp, dob, role, department, photoUrl }) {
      const data = await request('/api/auth/register', {
        method: 'POST', auth: false,
        body: { name, email, password, country, whatsapp, dob, role, department, photoUrl }
      });
      return applySession(data);
    },

    async login(email, password) {
      const data = await request('/api/auth/login', { method: 'POST', auth: false, body: { email, password } });
      return applySession(data);
    },

    // idToken comes from Google Identity Services (accounts.google.com/gsi/client),
    // NOT Firebase's signInWithPopup - see /assets/yan-google-signin.js for the client-side trigger.
    async googleSignIn(idToken) {
      const data = await request('/api/auth/google', { method: 'POST', auth: false, body: { idToken } });
      if (data.needsProfileCompletion) return data; // caller shows the "complete profile" form
      return applySession(data);
    },

    async completeProfile({ pendingToken, googleProfile, country, whatsapp, dob, department, agree }) {
      const data = await request('/api/auth/complete-profile', {
        method: 'POST', auth: false,
        body: { pendingToken, googleProfile, country, whatsapp, dob, department, agree }
      });
      return applySession(data);
    },

    async me() {
      if (!getToken()) return null;
      try {
        const data = await request('/api/auth/me');
        setCachedUser(data.user);
        return data.user;
      } catch (e) {
        setToken(null); setCachedUser(null);
        return null;
      }
    },

    async logout() {
      try { await request('/api/auth/logout', { method: 'POST' }); } catch (e) {}
      setToken(null); setCachedUser(null);
    },

    // Re-mints a Firebase custom token for the current D1 session, for pages that
    // need to (re)establish a Firebase Auth session without asking for the password
    // again - e.g. on load, when a D1 session exists but Firebase's own session
    // (session-only persistence) was cleared by a browser restart.
    async getBridgeToken() {
      const data = await request('/api/auth/bridge', { method: 'POST' });
      return data.firebaseToken;
    },

    async resendVerification() { return request('/api/auth/resend-verification', { method: 'POST' }); },
    async verifyEmail(token, uid) {
      return request('/api/auth/verify-email', { method: 'POST', auth: false, body: { token, uid } });
    },
    async forgotPassword(email) {
      return request('/api/auth/forgot-password', { method: 'POST', auth: false, body: { email } });
    },
    async resetPassword(token, uid, newPassword) {
      return request('/api/auth/reset-password', { method: 'POST', auth: false, body: { token, uid, newPassword } });
    }
  };

  window.YanAPI = YanAPI;
})();
