// Public content + form-submission API: read-only endpoints for events/gallery/team/stories
// (previously direct Firestore reads from events.html/gallery.html/team.html/Journey_Stories.html)
// and write endpoints for join.html/contact.html's forms.

function corsHeaders(origin, allowedOrigins) {
  const allowed = allowedOrigins.includes(origin) ? origin : allowedOrigins[0];
  return {
    'Access-Control-Allow-Origin': allowed,
    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Vary': 'Origin'
  };
}

function json(data, status, headers) {
  return new Response(JSON.stringify(data), { status, headers: { 'Content-Type': 'application/json', ...headers } });
}

function newId() { return crypto.randomUUID(); }
function isValidEmail(email) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email); }

async function sendEmail(env, { to, subject, message }) {
  try {
    await fetch(env.EMAIL_WORKER_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ to, subject, message })
    });
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

// ---- writes ----

async function submitJoin(request, env, cors) {
  const formObj = await request.json();
  const name = formObj.name || formObj['full-name'] || '';
  const email = formObj.email || '';
  if (!name || !email || !isValidEmail(email)) return json({ error: 'Name and a valid email are required' }, 400, cors);

  const now = Date.now();
  await env.DB.prepare(
    'INSERT INTO join_requests (id,name,email,data_json,source,status,created_at) VALUES (?,?,?,?,?,?,?)'
  ).bind(newId(), name, email, JSON.stringify(formObj), 'join.html', 'pending', now).run();

  await sendEmail(env, {
    to: email,
    subject: 'Application Received — Young Africans Network',
    message: 'Thank you for applying to join the Young Africans Network! We have received your application and our team will review it within 48 hours. We are excited about your interest in being part of our pan-African community.\n\nWarm regards,\nYAN Administration Office\nyoungafricansnetwork.org'
  });

  return json({ ok: true }, 201, cors);
}

async function submitContact(request, env, cors) {
  const formObj = await request.json();
  const name = formObj.name || '';
  const email = formObj.email || '';
  if (!name || !email || !isValidEmail(email)) return json({ error: 'Name and a valid email are required' }, 400, cors);

  const now = Date.now();
  await env.DB.prepare(
    'INSERT INTO contact_submissions (id,name,email,data_json,source,status,created_at) VALUES (?,?,?,?,?,?,?)'
  ).bind(newId(), name, email, JSON.stringify(formObj), 'contact.html', 'unread', now).run();

  await sendEmail(env, {
    to: email,
    subject: 'Message Received — Young Africans Network',
    message: 'Thank you for reaching out to the Young Africans Network! We have received your message and our team will get back to you within 48 hours.\n\nWarm regards,\nYAN Administration Office\nyoungafricansnetwork.org'
  });

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

      return json({ error: 'Not found' }, 404, cors);
    } catch (e) {
      console.error(e);
      return json({ error: e.message || 'Internal error' }, 500, cors);
    }
  }
};
