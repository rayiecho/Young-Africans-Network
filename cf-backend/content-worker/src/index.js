// Public content + form-submission API: read-only endpoints for events/gallery/team/stories
// (previously direct Firestore reads from events.html/gallery.html/team.html/Journey_Stories.html)
// and write endpoints for join.html/contact.html's forms.

function corsHeaders(origin, allowedOrigins) {
  const allowed = allowedOrigins.includes(origin) ? origin : allowedOrigins[0];
  return {
    'Access-Control-Allow-Origin': allowed,
    'Access-Control-Allow-Methods': 'GET,POST,DELETE,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Vary': 'Origin'
  };
}

function json(data, status, headers) {
  return new Response(JSON.stringify(data), { status, headers: { 'Content-Type': 'application/json', ...headers } });
}

function newId() { return crypto.randomUUID(); }
function isValidEmail(email) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email); }

async function sha256Hex(input) {
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(input));
  return [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join('');
}

// Sessions live in the same D1 database the auth worker writes to, so any worker with
// the DB binding can validate a Bearer token the same way without needing to call the
// auth worker over HTTP.
async function getSessionUser(request, env) {
  const authHeader = request.headers.get('Authorization') || '';
  const token = authHeader.startsWith('Bearer ') ? authHeader.slice(7) : null;
  if (!token) return null;
  const tokenHash = await sha256Hex(token);
  const row = await env.DB.prepare(
    `SELECT s.expires_at as sess_expires, u.* FROM sessions s JOIN users u ON u.id = s.user_id WHERE s.id = ?`
  ).bind(tokenHash).first();
  if (!row || row.sess_expires < Date.now()) return null;
  return row;
}

async function requireUser(request, env, cors) {
  const user = await getSessionUser(request, env);
  if (!user) return { error: json({ error: 'Not authenticated' }, 401, cors) };
  return { user };
}

async function sendEmail(env, { to, name, subject, message }) {
  try {
    // Same two bugs already found and fixed in ops-worker: (1) the email worker expects
    // to_email/name/type, not {to,subject,message}; (2) fetching its public workers.dev
    // URL directly from another Worker on the same account hits Cloudflare's
    // loop-prevention (error 1042) and never actually reaches it - needs a service binding.
    const res = await env.EMAIL_WORKER.fetch('https://yan-email-worker.youngafricansn.workers.dev', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ to_email: to, name: name || '', subject, message, type: 'general' })
    });
    if (!res.ok) console.error('Email send failed:', res.status, await res.text());
  } catch (e) { console.error('Email send failed:', e.message); }
}

// ---- reads ----

async function getEvents(env, cors) {
  const { results } = await env.DB.prepare(
    'SELECT * FROM events ORDER BY created_at DESC'
  ).all();
  return json(results.map(e => ({
    id: e.id, title: e.title, photoUrl: e.photo_url, status: e.status,
    date: e.event_date, lead: e.lead, description: e.description, videoUrl: e.video_url, createdAt: e.created_at
  })), 200, cors);
}

async function getGallery(env, cors) {
  const { results } = await env.DB.prepare(
    'SELECT * FROM gallery ORDER BY created_at DESC'
  ).all();
  return json(results.map(g => ({
    id: g.id, type: g.type, url: g.url, caption: g.caption, category: g.category, createdAt: g.created_at
  })), 200, cors);
}

async function getTeam(env, cors) {
  const { results } = await env.DB.prepare(
    'SELECT * FROM team ORDER BY sort_order ASC'
  ).all();
  return json(results.map(t => ({
    id: t.id, name: t.name, role: t.role, category: t.category, department: t.department,
    country: t.country, email: t.email, photoUrl: t.photo_url
  })), 200, cors);
}

async function getStories(env, cors) {
  const { results } = await env.DB.prepare(
    'SELECT * FROM stories ORDER BY created_at DESC'
  ).all();
  return json(results.map(s => ({
    id: s.id, name: s.name, role: s.role, country: s.country, photoUrl: s.photo_url,
    tag: s.tag, quote: s.quote, message: s.message, createdAt: s.created_at
  })), 200, cors);
}

// ---- feed: posts / likes / replies ----

function postRow(row, likeCount, likedByMe) {
  return {
    id: row.id, content: row.content, category: row.category, link: row.link,
    youtubeId: row.youtube_id, imageUrl: row.image_url, createdAt: row.created_at,
    authorId: row.author_id, authorName: row.author_name, authorPhoto: row.author_photo,
    department: row.department, likeCount, likedByMe
  };
}

async function getPosts(request, env, cors, url) {
  const user = await getSessionUser(request, env); // optional - anonymous callers just get likedByMe:false
  const department = url.searchParams.get('department');
  const limitParam = Math.min(parseInt(url.searchParams.get('limit') || '30', 10) || 30, 50);

  const { results } = department
    ? await env.DB.prepare(
        `SELECT p.*, u.name as author_name, u.photo_url as author_photo
         FROM posts p JOIN users u ON u.id = p.author_id
         WHERE p.department = ? ORDER BY p.created_at DESC LIMIT ?`
      ).bind(department, limitParam).all()
    : await env.DB.prepare(
        `SELECT p.*, u.name as author_name, u.photo_url as author_photo
         FROM posts p JOIN users u ON u.id = p.author_id
         ORDER BY p.created_at DESC LIMIT ?`
      ).bind(limitParam).all();
  if (results.length === 0) return json({ posts: [] }, 200, cors);

  const ids = results.map(r => r.id);
  const placeholders = ids.map(() => '?').join(',');
  const likeCounts = await env.DB.prepare(
    `SELECT post_id, COUNT(*) as c FROM post_likes WHERE post_id IN (${placeholders}) GROUP BY post_id`
  ).bind(...ids).all();
  const countByPost = Object.fromEntries(likeCounts.results.map(r => [r.post_id, r.c]));

  let likedSet = new Set();
  if (user) {
    const mine = await env.DB.prepare(
      `SELECT post_id FROM post_likes WHERE user_id = ? AND post_id IN (${placeholders})`
    ).bind(user.id, ...ids).all();
    likedSet = new Set(mine.results.map(r => r.post_id));
  }

  return json({ posts: results.map(r => postRow(r, countByPost[r.id] || 0, likedSet.has(r.id))) }, 200, cors);
}

// Runs the same moderation check the client used to run on its own (bypassable, since
// anyone could just call this endpoint directly and skip a client-side check) - now the
// worker itself checks before ever writing the post, using the same AI worker/prompt.
async function moderateContent(env, text) {
  try {
    // Service binding, not fetch() to the public workers.dev URL - see wrangler.toml.
    const response = await env.AI_WORKER.fetch('https://yan-ai-worker.youngafricansn.workers.dev', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'claude-haiku-4-5-20251001',
        max_tokens: 100,
        messages: [{
          role: 'user',
          content: 'You are a content moderator for a pan-African youth community platform. Analyze this post and respond ONLY with valid JSON in this exact format: {"flagged": false, "reason": ""} or {"flagged": true, "reason": "brief reason"}. Flag content that contains: hate speech, racism, sexual content, violence, spam, scams, or harassment. Do NOT flag normal community discussions, scholarship info, career advice, or motivational content. Post to analyze: ' + text
        }]
      })
    });
    const data = await response.json();
    const reply = data.content?.[0]?.text || '{"flagged":false,"reason":""}';
    return JSON.parse(reply.replace(/```json|```/g, '').trim());
  } catch (e) {
    // If moderation itself fails, allow the post through rather than blocking real
    // members over an AI-worker outage - matches the original client-side behavior.
    console.error('[moderateContent] failed, allowing post through:', e.message);
    return { flagged: false, reason: '' };
  }
}

function stripHtml(str) { return String(str || '').replace(/<[^>]*>/g, '').trim(); }
function isValidUrl(url) { try { new URL(url); return true; } catch (e) { return false; } }
function getYouTubeId(url) {
  const m = String(url || '').match(/(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=))([\w-]{11})/);
  return m ? m[1] : '';
}

async function createPost(request, env, cors) {
  const { error, user } = await requireUser(request, env, cors);
  if (error) return error;
  const body = await request.json();
  const content = stripHtml(body.content).slice(0, 2000);
  if (!content) return json({ error: 'Write something first' }, 400, cors);
  const link = body.link && isValidUrl(body.link) ? body.link : '';

  const mod = await moderateContent(env, content);
  const now = Date.now();
  if (mod.flagged) {
    await env.DB.prepare(
      `INSERT INTO moderation_log (id,actor_id,action,target,content,reason,created_at) VALUES (?,?,?,?,?,?,?)`
    ).bind(newId(), user.id, 'post_blocked', 'posts', content, mod.reason || '', now).run();
    return json({ error: 'Post blocked: ' + (mod.reason || 'violates community guidelines') }, 422, cors);
  }

  const postId = newId();
  await env.DB.prepare(
    `INSERT INTO posts (id,author_id,content,category,link,youtube_id,image_url,department,created_at) VALUES (?,?,?,?,?,?,?,?,?)`
  ).bind(postId, user.id, content, body.category || 'General', link, getYouTubeId(link), body.imageUrl || '', body.department || null, now).run();
  await env.DB.prepare(`INSERT INTO points_history (id,user_id,action,description,points,created_at) VALUES (?,?,?,?,?,?)`)
    .bind(newId(), user.id, 'post_created', 'Posted in feed', 1, now).run();
  await env.DB.prepare(`INSERT INTO member_points (user_id, points) VALUES (?, 1) ON CONFLICT(user_id) DO UPDATE SET points = points + 1`)
    .bind(user.id).run();

  return json({ id: postId }, 201, cors);
}

async function deletePost(request, env, cors, postId) {
  const { error, user } = await requireUser(request, env, cors);
  if (error) return error;
  const post = await env.DB.prepare('SELECT author_id FROM posts WHERE id = ?').bind(postId).first();
  if (!post) return json({ error: 'Not found' }, 404, cors);
  if (post.author_id !== user.id && !user.is_admin) return json({ error: 'Not allowed' }, 403, cors);
  await env.DB.prepare('DELETE FROM posts WHERE id = ?').bind(postId).run();
  return json({ ok: true }, 200, cors);
}

async function toggleLike(request, env, cors, postId) {
  const { error, user } = await requireUser(request, env, cors);
  if (error) return error;
  const existing = await env.DB.prepare('SELECT 1 FROM post_likes WHERE post_id = ? AND user_id = ?').bind(postId, user.id).first();
  if (existing) {
    await env.DB.prepare('DELETE FROM post_likes WHERE post_id = ? AND user_id = ?').bind(postId, user.id).run();
  } else {
    await env.DB.prepare('INSERT INTO post_likes (post_id, user_id, created_at) VALUES (?, ?, ?)').bind(postId, user.id, Date.now()).run();
  }
  const { c } = await env.DB.prepare('SELECT COUNT(*) as c FROM post_likes WHERE post_id = ?').bind(postId).first();
  return json({ likeCount: c, likedByMe: !existing }, 200, cors);
}

async function getReplies(env, cors, postId) {
  const { results } = await env.DB.prepare(
    `SELECT r.*, u.name as author_name FROM post_replies r JOIN users u ON u.id = r.author_id
     WHERE r.post_id = ? ORDER BY r.created_at ASC`
  ).bind(postId).all();
  return json({ replies: results.map(r => ({ id: r.id, content: r.content, authorName: r.author_name, createdAt: r.created_at })) }, 200, cors);
}

async function createReply(request, env, cors, postId) {
  const { error, user } = await requireUser(request, env, cors);
  if (error) return error;
  const body = await request.json();
  const content = stripHtml(body.content).slice(0, 500);
  if (!content) return json({ error: 'Empty reply' }, 400, cors);
  await env.DB.prepare(
    `INSERT INTO post_replies (id,post_id,author_id,content,created_at) VALUES (?,?,?,?,?)`
  ).bind(newId(), postId, user.id, content, Date.now()).run();
  return json({ ok: true }, 201, cors);
}

// ---- notifications ----
// Firestore rules for this collection were `allow create, read: if isLoggedIn()` with
// no further restriction - any logged-in member can post or read any notification,
// broadcast or targeted at someone else. Matching that exactly rather than tightening
// it as a side effect of migrating.

function notifRow(row, isRead) {
  return {
    id: row.id, userId: row.user_id, title: row.title, message: row.message,
    url: row.url, type: row.type, postedBy: row.posted_by, department: row.department,
    createdAt: row.created_at, isRead: !!isRead
  };
}

async function createNotification(request, env, cors) {
  const { error, user } = await requireUser(request, env, cors);
  if (error) return error;
  const body = await request.json();
  if (!body.title || !body.message) return json({ error: 'Title and message required' }, 400, cors);
  const id = newId();
  await env.DB.prepare(
    `INSERT INTO notifications (id,user_id,title,message,url,type,posted_by,department,created_at) VALUES (?,?,?,?,?,?,?,?,?)`
  ).bind(id, body.userId || null, body.title, body.message, body.url || null, body.type || null,
    body.postedBy || user.name, body.department || null, Date.now()).run();
  return json({ id }, 201, cors);
}

async function getNotifications(request, env, cors, url) {
  const { error, user } = await requireUser(request, env, cors);
  if (error) return error;
  const scope = url.searchParams.get('scope') || 'recent';
  const limitParam = Math.min(parseInt(url.searchParams.get('limit') || '30', 10) || 30, 50);

  let query, binds;
  if (scope === 'broadcast') {
    query = `SELECT * FROM notifications WHERE user_id IS NULL ORDER BY created_at DESC LIMIT ?`;
    binds = [limitParam];
  } else if (scope === 'personal') {
    query = `SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT ?`;
    binds = [user.id, limitParam];
  } else {
    query = `SELECT * FROM notifications ORDER BY created_at DESC LIMIT ?`;
    binds = [limitParam];
  }
  const { results } = await env.DB.prepare(query).bind(...binds).all();
  if (!results.length) return json({ notifications: [] }, 200, cors);

  const ids = results.map(r => r.id);
  const placeholders = ids.map(() => '?').join(',');
  const reads = await env.DB.prepare(
    `SELECT notification_id FROM notification_reads WHERE user_id = ? AND notification_id IN (${placeholders})`
  ).bind(user.id, ...ids).all();
  const readSet = new Set(reads.results.map(r => r.notification_id));

  return json({ notifications: results.map(r => notifRow(r, readSet.has(r.id))) }, 200, cors);
}

async function markNotificationRead(request, env, cors, id) {
  const { error, user } = await requireUser(request, env, cors);
  if (error) return error;
  await env.DB.prepare(
    `INSERT INTO notification_reads (notification_id, user_id, read_at) VALUES (?,?,?) ON CONFLICT(notification_id, user_id) DO NOTHING`
  ).bind(id, user.id, Date.now()).run();
  return json({ ok: true }, 200, cors);
}

async function deleteNotificationHandler(request, env, cors, id) {
  const { error, user } = await requireUser(request, env, cors);
  if (error) return error;
  if (!user.is_admin) return json({ error: 'Admin only' }, 403, cors);
  await env.DB.prepare('DELETE FROM notifications WHERE id = ?').bind(id).run();
  return json({ ok: true }, 200, cors);
}

// ---- writes ----

async function submitJoin(request, env, cors) {
  const formObj = await request.json();
  // join.html actually submits first_name/last_name as separate fields, not a combined
  // name/full-name - this was silently rejecting every real submission (400, surfaced
  // to the applicant as a generic "Error - Try Again").
  const name = formObj.name || formObj['full-name']
    || [formObj.first_name, formObj.last_name].filter(Boolean).join(' ').trim() || '';
  const email = formObj.email || '';
  if (!name || !email || !isValidEmail(email)) return json({ error: 'Name and a valid email are required' }, 400, cors);

  const now = Date.now();
  await env.DB.prepare(
    'INSERT INTO join_requests (id,name,email,data_json,source,status,created_at) VALUES (?,?,?,?,?,?,?)'
  ).bind(newId(), name, email, JSON.stringify(formObj), 'join.html', 'pending', now).run();

  // Best-effort mirror into Firestore's joinRequests collection - admin.html's existing
  // approval queue reads that, not the D1 table above, and wasn't rebuilt for D1 yet.
  // Awaited (not fire-and-forget): an un-awaited fetch can get killed mid-flight once
  // the response is returned, since Workers don't keep running after that without
  // ctx.waitUntil() - confirmed missing live, the mirrored doc never actually landed.
  try {
    await env.OPS_WORKER.fetch('https://yan-ops-worker.youngafricansn.workers.dev/api/internal/mirror-join-request', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(formObj)
    });
  } catch (e) { console.error('Join request mirror failed:', e.message); }

  await sendEmail(env, {
    to: email, name,
    subject: 'Application Received — Young Africans Network',
    message: 'Thank you for applying to join the Young Africans Network! We have received your application and our team will review it within 48 hours. We are excited about your interest in being part of our pan-African community.\n\nWarm regards,\nYAN Administration Office\nyoungafricansnetwork.org'
  });

  return json({ ok: true }, 201, cors);
}

async function submitContact(request, env, cors) {
  const formObj = await request.json();
  // contact.html submits firstName/lastName separately, not a combined name - same class
  // of bug as join.html, silently rejecting every real submission.
  const name = formObj.name
    || [formObj.firstName, formObj.lastName].filter(Boolean).join(' ').trim() || '';
  const email = formObj.email || '';
  if (!name || !email || !isValidEmail(email)) return json({ error: 'Name and a valid email are required' }, 400, cors);

  const now = Date.now();
  await env.DB.prepare(
    'INSERT INTO contact_submissions (id,name,email,data_json,source,status,created_at) VALUES (?,?,?,?,?,?,?)'
  ).bind(newId(), name, email, JSON.stringify(formObj), 'contact.html', 'unread', now).run();

  await sendEmail(env, {
    to: email, name,
    subject: 'Message Received — Young Africans Network',
    message: 'Thank you for reaching out to the Young Africans Network! We have received your message and our team will get back to you within 48 hours.\n\nWarm regards,\nYAN Administration Office\nyoungafricansnetwork.org'
  });

  return json({ ok: true }, 201, cors);
}

// Replaces the floating WhatsApp button's wa.me redirect - visitors weren't being taken
// to WhatsApp at all wanted, they just wanted their message to reach YAN. No WhatsApp
// Business API involved (that needs an account/verification only the org can set up) -
// this just emails every admin with the message and the visitor's own number to call/
// message back on, same delivery mechanism already used for join/contact submissions.
async function submitQuickMessage(request, env, cors) {
  const body = await request.json();
  const phone = (body.phone || '').trim();
  const message = (body.message || '').trim();
  const name = (body.name || '').trim();
  if (!phone || !message) return json({ error: 'Phone number and message are required' }, 400, cors);

  const now = Date.now();
  await env.DB.prepare(
    'INSERT INTO contact_submissions (id,name,email,data_json,source,status,created_at) VALUES (?,?,?,?,?,?,?)'
  ).bind(newId(), name || 'WhatsApp widget', '', JSON.stringify({ phone, message, name }), 'whatsapp-widget', 'unread', now).run();

  const { results: admins } = await env.DB.prepare('SELECT email, name FROM users WHERE is_admin = 1').all();
  await Promise.all(admins.map(a => sendEmail(env, {
    to: a.email, name: a.name,
    subject: 'New WhatsApp widget message' + (name ? ' from ' + name : ''),
    message: `${name ? name + ' (' + phone + ')' : phone} sent a message via the site's WhatsApp button:\n\n"${message}"\n\nReply to them on WhatsApp: https://wa.me/${phone.replace(/[^0-9]/g, '')}`
  })));

  return json({ ok: true }, 201, cors);
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
      if (path === '/api/events' && request.method === 'GET') return await getEvents(env, cors);
      if (path === '/api/gallery' && request.method === 'GET') return await getGallery(env, cors);
      if (path === '/api/team' && request.method === 'GET') return await getTeam(env, cors);
      if (path === '/api/stories' && request.method === 'GET') return await getStories(env, cors);
      if (path === '/api/join' && request.method === 'POST') return await submitJoin(request, env, cors);
      if (path === '/api/contact' && request.method === 'POST') return await submitContact(request, env, cors);
      if (path === '/api/quick-message' && request.method === 'POST') return await submitQuickMessage(request, env, cors);

      if (path === '/api/notifications' && request.method === 'GET') return await getNotifications(request, env, cors, url);
      if (path === '/api/notifications' && request.method === 'POST') return await createNotification(request, env, cors);
      const notifMatch = path.match(/^\/api\/notifications\/([^/]+)(\/read)?$/);
      if (notifMatch) {
        const [, id, sub] = notifMatch;
        if (sub === '/read' && request.method === 'POST') return await markNotificationRead(request, env, cors, id);
        if (!sub && request.method === 'DELETE') return await deleteNotificationHandler(request, env, cors, id);
      }

      if (path === '/api/posts' && request.method === 'GET') return await getPosts(request, env, cors, url);
      if (path === '/api/posts' && request.method === 'POST') return await createPost(request, env, cors);

      const postMatch = path.match(/^\/api\/posts\/([^/]+)(\/(like|replies))?$/);
      if (postMatch) {
        const [, postId, , sub] = postMatch;
        if (!sub && request.method === 'DELETE') return await deletePost(request, env, cors, postId);
        if (sub === 'like' && request.method === 'POST') return await toggleLike(request, env, cors, postId);
        if (sub === 'replies' && request.method === 'GET') return await getReplies(env, cors, postId);
        if (sub === 'replies' && request.method === 'POST') return await createReply(request, env, cors, postId);
      }

      return json({ error: 'Not found' }, 404, cors);
    } catch (e) {
      console.error(e);
      return json({ error: e.message || 'Internal error' }, 500, cors);
    }
  }
};
