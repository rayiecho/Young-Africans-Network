// Shared client for the new Cloudflare Workers backend (replaces direct Firebase SDK calls).
// Include with <script src="/assets/yan-api.js"></script> - exposes window.YanAPI.
// Session tokens are stored in localStorage and sent as a Bearer token, since the API
// worker lives on a different origin (workers.dev) than the site - cross-site cookies
// would need SameSite=None and are increasingly unreliable in browsers, so a bearer
// token in localStorage (mirroring how mobile/SPA clients typically talk to a separate
// API host) avoids that entirely.

(function () {
  const AUTH_BASE = 'https://yan-auth-worker.youngafricansn.workers.dev';
  const CONTENT_BASE = 'https://yan-content-worker.youngafricansn.workers.dev';
  const OPS_BASE = 'https://yan-ops-worker.youngafricansn.workers.dev';
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

  async function requestTo(base, path, { method = 'GET', body, auth = true } = {}) {
    const headers = { 'Content-Type': 'application/json' };
    if (auth) {
      const token = getToken();
      if (token) headers['Authorization'] = 'Bearer ' + token;
    }
    const res = await fetch(base + path, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined
    });
    let data = {};
    try { data = await res.json(); } catch (e) {}
    if (!res.ok) throw new Error(data.error || ('Request failed (' + res.status + ')'));
    return data;
  }
  const request = (path, opts) => requestTo(AUTH_BASE, path, opts);
  const contentRequest = (path, opts) => requestTo(CONTENT_BASE, path, opts);
  const opsRequest = (path, opts) => requestTo(OPS_BASE, path, opts);

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
    },

    // ---- feed ----
    async getPosts({ department, limit } = {}) {
      const params = new URLSearchParams();
      if (department) params.set('department', department);
      if (limit) params.set('limit', limit);
      const qs = params.toString();
      const data = await contentRequest('/api/posts' + (qs ? '?' + qs : ''));
      return data.posts;
    },
    async createPost({ content, category, link, imageUrl, department }) {
      return contentRequest('/api/posts', { method: 'POST', body: { content, category, link, imageUrl, department } });
    },
    async deletePost(postId) {
      return contentRequest('/api/posts/' + postId, { method: 'DELETE' });
    },
    async toggleLike(postId) {
      return contentRequest('/api/posts/' + postId + '/like', { method: 'POST' });
    },
    async getReplies(postId) {
      const data = await contentRequest('/api/posts/' + postId + '/replies', { auth: false });
      return data.replies;
    },
    async createReply(postId, content) {
      return contentRequest('/api/posts/' + postId + '/replies', { method: 'POST', body: { content } });
    },

    // ---- notifications ----
    async createNotification({ userId, department, title, message, type, url, postedBy }) {
      return contentRequest('/api/notifications', { method: 'POST', body: { userId, department, title, message, type, url, postedBy } });
    },
    async getNotifications({ scope, limit } = {}) {
      const params = new URLSearchParams();
      if (scope) params.set('scope', scope);
      if (limit) params.set('limit', limit);
      const qs = params.toString();
      const data = await contentRequest('/api/notifications' + (qs ? '?' + qs : ''));
      return data.notifications;
    },
    async markNotificationRead(id) { return contentRequest('/api/notifications/' + id + '/read', { method: 'POST' }); },
    async deleteNotification(id) { return contentRequest('/api/notifications/' + id, { method: 'DELETE' }); },

    // ---- session coordination ----
    async createSession({ sessionDate, department, topic, meetLink, assignedHeadId }) {
      return opsRequest('/api/sessions', { method: 'POST', body: { sessionDate, department, topic, meetLink, assignedHeadId } });
    },
    async getSessions({ department, headId } = {}) {
      const params = new URLSearchParams();
      if (department) params.set('department', department);
      if (headId) params.set('headId', headId);
      const qs = params.toString();
      const data = await opsRequest('/api/sessions' + (qs ? '?' + qs : ''));
      return data.sessions;
    },
    async getSession(id) {
      const data = await opsRequest('/api/sessions/' + id);
      return data.session;
    },
    async confirmSession(id) { return opsRequest('/api/sessions/' + id + '/confirm', { method: 'POST' }); },
    async markSessionPrepComplete(id) { return opsRequest('/api/sessions/' + id + '/prep-complete', { method: 'POST' }); },
    async flagSessionNeedsHelp(id, note, taskType) {
      return opsRequest('/api/sessions/' + id + '/needs-help', { method: 'POST', body: { note, taskType } });
    },
    async addSessionGuest(id, name, contact) {
      return opsRequest('/api/sessions/' + id + '/guests', { method: 'POST', body: { name, contact } });
    },
    async confirmSessionGuest(id, guestId) {
      return opsRequest('/api/sessions/' + id + '/guests/' + guestId + '/confirm', { method: 'POST' });
    },
    async addSessionRole(id, roleName) {
      return opsRequest('/api/sessions/' + id + '/roles', { method: 'POST', body: { roleName } });
    },
    async claimSessionRole(id, roleId) {
      return opsRequest('/api/sessions/' + id + '/roles/' + roleId + '/claim', { method: 'POST' });
    },
    async checkInSession(id) { return opsRequest('/api/sessions/' + id + '/checkin', { method: 'POST' }); },
    async getSessionAttendance(id) {
      const data = await opsRequest('/api/sessions/' + id + '/attendance');
      return data.attendance;
    },
    async deleteSession(id) { return opsRequest('/api/sessions/' + id, { method: 'DELETE' }); },
    async markSessionAttendance(id, userId) {
      return opsRequest('/api/sessions/' + id + '/attendance/mark', { method: 'POST', body: { userId } });
    },
    async unmarkSessionAttendance(id, userId) {
      return opsRequest('/api/sessions/' + id + '/attendance/' + userId, { method: 'DELETE' });
    },
    async getAttendanceRegister({ department, from, to } = {}) {
      const params = new URLSearchParams();
      if (department) params.set('department', department);
      if (from) params.set('from', from);
      if (to) params.set('to', to);
      const qs = params.toString();
      return opsRequest('/api/attendance-register' + (qs ? '?' + qs : ''));
    },
    async getHeads() {
      const data = await opsRequest('/api/heads');
      return data.heads;
    },
    async assignHead(userId, department) {
      return opsRequest('/api/heads', { method: 'POST', body: { userId, department } });
    },
    async removeHead(userId) {
      return opsRequest('/api/heads/' + userId, { method: 'DELETE' });
    },
    async searchUsers(q) {
      const data = await opsRequest('/api/users/search?q=' + encodeURIComponent(q));
      return data.users;
    },
    async checkRegisteredEmails(emails) {
      const data = await opsRequest('/api/users/check-emails', { method: 'POST', body: { emails } });
      return data.registered;
    },
    async getVolunteerQueue(month) {
      const data = await opsRequest('/api/volunteer-queue' + (month ? '?month=' + encodeURIComponent(month) : ''));
      return data.queue;
    },
    async emailVolunteerQueue(subject, message, month) {
      return opsRequest('/api/volunteer-queue/email', { method: 'POST', body: { subject, message, month } });
    },
    async messagePerson(email, subject, message) {
      return opsRequest('/api/message', { method: 'POST', body: { email, subject, message } });
    },
    async getVolunteerCandidates(month) {
      const data = await opsRequest('/api/volunteer-candidates' + (month ? '?month=' + encodeURIComponent(month) : ''));
      return data.candidates;
    },
    async addVolunteerToRoster(month, email, name) {
      return opsRequest('/api/volunteer-roster', { method: 'POST', body: { month, email, name } });
    },
    async removeVolunteerFromRoster(id) {
      return opsRequest('/api/volunteer-roster/' + id, { method: 'DELETE' });
    },

    // ---- volunteer room ----
    async createVolunteerTask({ taskType, title, brief, rawFileUrl, dueDate, relatedSessionId, hasRawFile }) {
      return opsRequest('/api/volunteer-tasks', { method: 'POST', body: { taskType, title, brief, rawFileUrl, dueDate, relatedSessionId, hasRawFile } });
    },
    async getVolunteerTasks({ status, mine } = {}) {
      const params = new URLSearchParams();
      if (status) params.set('status', status);
      if (mine) params.set('mine', '1');
      const qs = params.toString();
      const data = await opsRequest('/api/volunteer-tasks' + (qs ? '?' + qs : ''));
      return data.tasks;
    },
    async claimVolunteerTask(id) { return opsRequest('/api/volunteer-tasks/' + id + '/claim', { method: 'POST' }); },
    async deleteVolunteerTask(id) { return opsRequest('/api/volunteer-tasks/' + id, { method: 'DELETE' }); },
    async submitVolunteerTask(id, submittedFileUrl) {
      // submittedFileUrl omitted = phase 1 (mark submitted-but-uploading, don't notify yet);
      // present = phase 2 (finalize + notify) - see submitTask() in ops-worker.
      return opsRequest('/api/volunteer-tasks/' + id + '/submit', { method: 'POST', body: submittedFileUrl ? { submittedFileUrl } : {} });
    },
    async attachRawFile(id, rawFileUrl) {
      return opsRequest('/api/volunteer-tasks/' + id + '/raw-file', { method: 'POST', body: { rawFileUrl } });
    },
    async reviewVolunteerTask(id, approved, note) {
      return opsRequest('/api/volunteer-tasks/' + id + '/review', { method: 'POST', body: { approved, note } });
    },
    async recordYoutubePublish(id, youtubeUrl) {
      return opsRequest('/api/volunteer-tasks/' + id + '/youtube', { method: 'POST', body: { youtubeUrl } });
    }
  };

  window.YanAPI = YanAPI;
})();
