// Session Coordination (dept_sessions/session_guests/session_roles/session_attendance)
// and the Volunteer Room (volunteer_tasks) - both new features, built native on D1/Workers
// rather than Firestore since they didn't exist before and would need migrating later anyway.

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

// ---- Firestore bridge: the existing feedback.html "which months can you volunteer"
// answers (sessionFeedback.volunteerMonths) are the real, already-in-use monthly
// volunteer list - not something to duplicate with a brand new D1 table. Queried
// live via Firestore's REST API rather than migrated, since feedback.html itself
// still writes there unchanged.
function pemToArrayBuffer(pem) {
  const b64 = pem.replace(/-----BEGIN PRIVATE KEY-----/, '').replace(/-----END PRIVATE KEY-----/, '').replace(/\s+/g, '');
  const bin = atob(b64);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return bytes.buffer;
}
function base64UrlEncode(bytesOrString) {
  const bytes = typeof bytesOrString === 'string' ? new TextEncoder().encode(bytesOrString) : bytesOrString;
  let bin = '';
  for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
  return btoa(bin).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

let cachedFirestoreToken = null;
let cachedFirestoreTokenExpiry = 0;

async function getFirestoreAccessToken(env) {
  if (cachedFirestoreToken && Date.now() < cachedFirestoreTokenExpiry - 60_000) return cachedFirestoreToken;
  const sa = JSON.parse(env.FIREBASE_SERVICE_ACCOUNT);
  const now = Math.floor(Date.now() / 1000);
  const header = { alg: 'RS256', typ: 'JWT' };
  const payload = {
    iss: sa.client_email, scope: 'https://www.googleapis.com/auth/datastore',
    aud: 'https://oauth2.googleapis.com/token', iat: now, exp: now + 3600
  };
  const assertion = `${base64UrlEncode(JSON.stringify(header))}.${base64UrlEncode(JSON.stringify(payload))}`;
  const key = await crypto.subtle.importKey('pkcs8', pemToArrayBuffer(sa.private_key), { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' }, false, ['sign']);
  const signature = await crypto.subtle.sign('RSASSA-PKCS1-v1_5', key, new TextEncoder().encode(assertion));
  const jwt = `${assertion}.${base64UrlEncode(new Uint8Array(signature))}`;
  const res = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=${encodeURIComponent(jwt)}`
  });
  const data = await res.json();
  if (!res.ok) throw new Error('Firestore token exchange failed: ' + JSON.stringify(data));
  cachedFirestoreToken = data.access_token;
  cachedFirestoreTokenExpiry = Date.now() + data.expires_in * 1000;
  return cachedFirestoreToken;
}

async function getFirestoreVolunteersForMonth(env, monthAbbrev) {
  const accessToken = await getFirestoreAccessToken(env);
  const res = await fetch(
    `https://firestore.googleapis.com/v1/projects/young-africans-network/databases/(default)/documents:runQuery`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + accessToken },
      body: JSON.stringify({
        structuredQuery: {
          from: [{ collectionId: 'sessionFeedback' }],
          where: { fieldFilter: { field: { fieldPath: 'volunteerMonths' }, op: 'ARRAY_CONTAINS', value: { stringValue: monthAbbrev } } }
        }
      })
    }
  );
  if (!res.ok) throw new Error('Firestore query failed: ' + (await res.text()));
  const rows = await res.json();
  const seen = new Set();
  const people = [];
  for (const row of rows) {
    const fields = row.document?.fields;
    if (!fields) continue;
    const email = fields.email?.stringValue || '';
    if (!email || seen.has(email)) continue;
    seen.add(email);
    people.push({
      name: fields.name?.stringValue || 'Anonymous',
      email, role: fields.role?.stringValue || '', country: fields.country?.stringValue || ''
    });
  }
  return people;
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

// "Pop-up": a notifications row with a distinct type the client (community.html)
// shows as a prominent in-app alert the moment it's seen, instead of just badge count -
// see the pollForPopups() polling loop client-side. Email is the second, independent
// channel so it also reaches someone not actively in the app right now.
async function notifyUser(env, userId, { title, message, emailSubject }) {
  await env.DB.prepare(
    `INSERT INTO notifications (id,user_id,title,message,type,posted_by,created_at) VALUES (?,?,?,?,?,?,?)`
  ).bind(newId(), userId, title, message, 'popup_task', 'YAN System', Date.now()).run();
  const user = await env.DB.prepare('SELECT email FROM users WHERE id = ?').bind(userId).first();
  if (user?.email) await sendEmail(env, { to: user.email, subject: emailSubject || title, message });
}

async function notifyAdmins(env, { title, message, emailSubject }) {
  const admins = await env.DB.prepare('SELECT id, email FROM users WHERE is_admin = 1').all();
  const now = Date.now();
  await Promise.all(admins.results.map(a => env.DB.prepare(
    `INSERT INTO notifications (id,user_id,title,message,type,posted_by,created_at) VALUES (?,?,?,?,?,?,?)`
  ).bind(newId(), a.id, title, message, 'popup_task', 'YAN System', now).run()));
  await Promise.all(admins.results.filter(a => a.email).map(a =>
    sendEmail(env, { to: a.email, subject: emailSubject || title, message })
  ));
}

async function sha256Hex(input) {
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(input));
  return [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join('');
}
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
async function requireAdminOrHead(request, env, cors) {
  const { error, user } = await requireUser(request, env, cors);
  if (error) return { error };
  if (!user.is_admin && !user.is_dept_head) return { error: json({ error: 'Admin or department head only' }, 403, cors) };
  return { user };
}

async function requireAdmin(request, env, cors) {
  const { error, user } = await requireUser(request, env, cors);
  if (error) return { error };
  if (!user.is_admin) return { error: json({ error: 'Admin only' }, 403, cors) };
  return { user };
}

// ---- sessions: shaping ----

async function hydrateSession(env, row) {
  const [guests, roles, attendanceCount] = await Promise.all([
    env.DB.prepare('SELECT * FROM session_guests WHERE session_id = ?').bind(row.id).all(),
    env.DB.prepare(
      `SELECT sr.*, u.name as filled_by_name FROM session_roles sr
       LEFT JOIN users u ON u.id = sr.filled_by WHERE sr.session_id = ?`
    ).bind(row.id).all(),
    env.DB.prepare('SELECT COUNT(*) as c FROM session_attendance WHERE session_id = ?').bind(row.id).first()
  ]);
  return {
    id: row.id, sessionDate: row.session_date, department: row.department, topic: row.topic,
    meetLink: row.meet_link, assignedHeadId: row.assigned_head_id, assignedHeadName: row.head_name,
    status: row.status, prepComplete: !!row.prep_complete, needsAssistance: !!row.needs_assistance,
    assistanceNote: row.assistance_note, createdAt: row.created_at,
    guests: guests.results.map(g => ({ id: g.id, name: g.name, contact: g.contact, confirmed: !!g.confirmed })),
    roles: roles.results.map(r => ({ id: r.id, roleName: r.role_name, filledBy: r.filled_by, filledByName: r.filled_by_name, notes: r.notes })),
    attendanceCount: attendanceCount.c
  };
}

async function createSessionHandler(request, env, cors) {
  const { error, user } = await requireAdmin(request, env, cors);
  if (error) return error;
  const body = await request.json();
  const { sessionDate, department, topic, meetLink } = body;
  if (!sessionDate || !department || !topic) return json({ error: 'Date, department and topic are required' }, 400, cors);

  let assignedHeadId = body.assignedHeadId || null;
  if (!assignedHeadId) {
    const head = await env.DB.prepare('SELECT id FROM users WHERE department = ? AND is_dept_head = 1 LIMIT 1').bind(department).first();
    assignedHeadId = head?.id || null;
  }

  const id = newId();
  const now = Date.now();
  await env.DB.prepare(
    `INSERT INTO dept_sessions (id,session_date,department,topic,meet_link,assigned_head_id,status,created_by,created_at,updated_at)
     VALUES (?,?,?,?,?,?, 'awaiting_confirmation', ?,?,?)`
  ).bind(id, sessionDate, department, topic, meetLink || null, assignedHeadId, user.id, now, now).run();

  if (assignedHeadId) {
    await notifyUser(env, assignedHeadId, {
      title: 'Your department is leading a session',
      message: `${department} is leading the ${sessionDate} session: "${topic}". Please confirm and prepare.`,
      emailSubject: 'YAN: your department is leading a session on ' + sessionDate
    });
  }

  return json({ id }, 201, cors);
}

async function listSessions(request, env, cors, url) {
  const department = url.searchParams.get('department');
  const headId = url.searchParams.get('headId');
  let query = `SELECT s.*, u.name as head_name FROM dept_sessions s LEFT JOIN users u ON u.id = s.assigned_head_id`;
  const conditions = [];
  const binds = [];
  if (department) { conditions.push('s.department = ?'); binds.push(department); }
  if (headId) { conditions.push('s.assigned_head_id = ?'); binds.push(headId); }
  if (conditions.length) query += ' WHERE ' + conditions.join(' AND ');
  query += ' ORDER BY s.session_date ASC';
  const { results } = await env.DB.prepare(query).bind(...binds).all();
  const sessions = await Promise.all(results.map(r => hydrateSession(env, r)));
  return json({ sessions }, 200, cors);
}

async function getSessionDetail(env, cors, id) {
  const row = await env.DB.prepare(
    `SELECT s.*, u.name as head_name FROM dept_sessions s LEFT JOIN users u ON u.id = s.assigned_head_id WHERE s.id = ?`
  ).bind(id).first();
  if (!row) return json({ error: 'Not found' }, 404, cors);
  return json({ session: await hydrateSession(env, row) }, 200, cors);
}

async function requireSessionAccess(request, env, cors, sessionId) {
  const { error, user } = await requireUser(request, env, cors);
  if (error) return { error };
  const session = await env.DB.prepare('SELECT * FROM dept_sessions WHERE id = ?').bind(sessionId).first();
  if (!session) return { error: json({ error: 'Not found' }, 404, cors) };
  const allowed = user.is_admin || session.assigned_head_id === user.id;
  if (!allowed) return { error: json({ error: 'Only the assigned head or an admin can do this' }, 403, cors) };
  return { user, session };
}

async function confirmSession(request, env, cors, id) {
  const { error, session } = await requireSessionAccess(request, env, cors, id);
  if (error) return error;
  const status = session.needs_assistance ? 'needs_help' : 'confirmed';
  await env.DB.prepare('UPDATE dept_sessions SET status = ?, updated_at = ? WHERE id = ?').bind(status, Date.now(), id).run();
  return json({ ok: true }, 200, cors);
}

async function markPrepComplete(request, env, cors, id) {
  const { error } = await requireSessionAccess(request, env, cors, id);
  if (error) return error;
  await env.DB.prepare('UPDATE dept_sessions SET prep_complete = 1, updated_at = ? WHERE id = ?').bind(Date.now(), id).run();
  return json({ ok: true }, 200, cors);
}

async function flagNeedsHelp(request, env, cors, id) {
  const { error, user, session } = await requireSessionAccess(request, env, cors, id);
  if (error) return error;
  const body = await request.json();
  const note = (body.note || '').trim();
  const taskType = ['poster','video_edit','slides','other'].includes(body.taskType) ? body.taskType : 'other';
  const now = Date.now();
  await env.DB.prepare(
    `UPDATE dept_sessions SET needs_assistance = 1, assistance_note = ?, status = 'needs_help', updated_at = ? WHERE id = ?`
  ).bind(note, now, id).run();

  // Bridge: a head flagging they need help automatically drops a task on the
  // Volunteer Room board instead of becoming another thing admin has to relay by hand.
  const taskId = newId();
  await env.DB.prepare(
    `INSERT INTO volunteer_tasks (id,task_type,title,brief,related_session_id,status,created_by,created_at,updated_at)
     VALUES (?,?,?,?,?, 'open', ?,?,?)`
  ).bind(taskId, taskType, `Help needed: ${session.topic}`, note, id, user.id, now, now).run();

  await notifyAdmins(env, {
    title: 'New volunteer help request',
    message: `${user.name} (${session.department}) needs help with "${session.topic}": ${note}`,
    emailSubject: 'New Volunteer Room task: ' + session.topic
  });

  const monthNow = MONTH_ABBREVS[new Date().getMonth()];
  const available = await getOrderedVolunteerAvailability(env, monthNow);
  await Promise.all(available.slice(0, 3).map(v => v.userId
    ? notifyUser(env, v.userId, {
        title: 'New Volunteer Room task: ' + session.topic,
        message: `A new ${taskType.replace('_',' ')} task is open: "Help needed: ${session.topic}". First come, first served.`,
        emailSubject: 'YAN Volunteer Room: Help needed for ' + session.topic
      })
    : sendEmail(env, { to: v.email, subject: 'YAN Volunteer Room: Help needed for ' + session.topic,
        message: `A new ${taskType.replace('_',' ')} task is open: "Help needed: ${session.topic}". First come, first served.` })
  ));

  return json({ ok: true, volunteerTaskId: taskId }, 200, cors);
}

async function addGuest(request, env, cors, id) {
  const { error } = await requireSessionAccess(request, env, cors, id);
  if (error) return error;
  const body = await request.json();
  if (!body.name) return json({ error: 'Guest name required' }, 400, cors);
  const guestId = newId();
  await env.DB.prepare('INSERT INTO session_guests (id,session_id,name,contact,confirmed) VALUES (?,?,?,?,0)')
    .bind(guestId, id, body.name, body.contact || null).run();
  return json({ id: guestId }, 201, cors);
}

async function confirmGuest(request, env, cors, id, guestId) {
  const { error } = await requireSessionAccess(request, env, cors, id);
  if (error) return error;
  await env.DB.prepare('UPDATE session_guests SET confirmed = 1 WHERE id = ? AND session_id = ?').bind(guestId, id).run();
  // If every session was flagged as needing_help purely for lack of guests, catching
  // this here would be nice, but that's a judgment call for the head, not automatic.
  return json({ ok: true }, 200, cors);
}

async function addRole(request, env, cors, id) {
  const { error } = await requireSessionAccess(request, env, cors, id);
  if (error) return error;
  const body = await request.json();
  if (!body.roleName) return json({ error: 'Role name required' }, 400, cors);
  const roleId = newId();
  await env.DB.prepare('INSERT INTO session_roles (id,session_id,role_name) VALUES (?,?,?)')
    .bind(roleId, id, body.roleName).run();
  return json({ id: roleId }, 201, cors);
}

async function claimRole(request, env, cors, id, roleId) {
  const { error, user } = await requireUser(request, env, cors);
  if (error) return error;
  const role = await env.DB.prepare('SELECT * FROM session_roles WHERE id = ? AND session_id = ?').bind(roleId, id).first();
  if (!role) return json({ error: 'Not found' }, 404, cors);
  if (role.filled_by && role.filled_by !== user.id) return json({ error: 'Already claimed' }, 409, cors);
  const nowFilled = role.filled_by === user.id ? null : user.id; // clicking again releases it
  await env.DB.prepare('UPDATE session_roles SET filled_by = ? WHERE id = ?').bind(nowFilled, roleId).run();
  return json({ filledBy: nowFilled }, 200, cors);
}

async function checkIn(request, env, cors, id) {
  const { error, user } = await requireUser(request, env, cors);
  if (error) return error;
  await env.DB.prepare(
    `INSERT INTO session_attendance (session_id,user_id,checked_in_at,marked_by) VALUES (?,?,?,'self')
     ON CONFLICT(session_id,user_id) DO NOTHING`
  ).bind(id, user.id, Date.now()).run();
  return json({ ok: true }, 200, cors);
}

async function getAttendance(request, env, cors, id) {
  const { error } = await requireSessionAccess(request, env, cors, id);
  if (error) return error;
  const { results } = await env.DB.prepare(
    `SELECT a.checked_in_at, a.marked_by, u.id as user_id, u.name FROM session_attendance a
     JOIN users u ON u.id = a.user_id WHERE a.session_id = ? ORDER BY a.checked_in_at ASC`
  ).bind(id).all();
  return json({ attendance: results.map(r => ({ userId: r.user_id, name: r.name, checkedInAt: r.checked_in_at, markedBy: r.marked_by })) }, 200, cors);
}

async function deleteSession(request, env, cors, id) {
  const { error, user } = await requireUser(request, env, cors);
  if (error) return error;
  if (!user.is_admin) return json({ error: 'Admin only' }, 403, cors);
  await env.DB.prepare('DELETE FROM dept_sessions WHERE id = ?').bind(id).run();
  return json({ ok: true }, 200, cors);
}

// ---- volunteer room ----

function taskRow(row) {
  return {
    id: row.id, taskType: row.task_type, title: row.title, brief: row.brief,
    relatedSessionId: row.related_session_id, rawFileUrl: row.raw_file_url,
    status: row.status, claimedBy: row.claimed_by, claimedByName: row.claimed_by_name,
    submittedFileUrl: row.submitted_file_url, reviewNote: row.review_note,
    dueDate: row.due_date, pointsAwarded: row.points_awarded, createdAt: row.created_at
  };
}

async function createTask(request, env, cors) {
  const { error, user } = await requireAdmin(request, env, cors);
  if (error) return error;
  const body = await request.json();
  if (!body.title || !body.taskType) return json({ error: 'Title and task type are required' }, 400, cors);
  const id = newId();
  const now = Date.now();
  await env.DB.prepare(
    `INSERT INTO volunteer_tasks (id,task_type,title,brief,related_session_id,raw_file_url,due_date,status,created_by,created_at,updated_at)
     VALUES (?,?,?,?,?,?,?, 'open', ?,?,?)`
  ).bind(id, body.taskType, body.title, body.brief || null, body.relatedSessionId || null,
    body.rawFileUrl || null, body.dueDate || null, user.id, now, now).run();

  // Notify whoever's first in the rotation queue - not everyone, so it stays useful
  // whether there are 3 volunteers or 30 (avoids a stampede/spam on every task).
  const monthNow = MONTH_ABBREVS[new Date().getMonth()];
  const available = await getOrderedVolunteerAvailability(env, monthNow);
  await Promise.all(available.slice(0, 3).map(v => v.userId
    ? notifyUser(env, v.userId, {
        title: 'New Volunteer Room task: ' + body.title,
        message: `A new ${body.taskType.replace('_',' ')} task is open: "${body.title}". First come, first served.`,
        emailSubject: 'YAN Volunteer Room: ' + body.title
      })
    : sendEmail(env, { to: v.email, subject: 'YAN Volunteer Room: ' + body.title,
        message: `A new ${body.taskType.replace('_',' ')} task is open: "${body.title}". First come, first served.` })
  ));

  return json({ id }, 201, cors);
}

async function listTasks(request, env, cors, url) {
  const status = url.searchParams.get('status');
  const mine = url.searchParams.get('mine');
  let user = null;
  if (mine) {
    const r = await requireUser(request, env, cors);
    if (r.error) return r.error;
    user = r.user;
  }
  let query = `SELECT t.*, u.name as claimed_by_name FROM volunteer_tasks t LEFT JOIN users u ON u.id = t.claimed_by`;
  const conditions = [];
  const binds = [];
  if (status) { conditions.push('t.status = ?'); binds.push(status); }
  if (mine && user) { conditions.push('t.claimed_by = ?'); binds.push(user.id); }
  if (conditions.length) query += ' WHERE ' + conditions.join(' AND ');
  query += ' ORDER BY t.created_at DESC';
  const { results } = await env.DB.prepare(query).bind(...binds).all();
  return json({ tasks: results.map(taskRow) }, 200, cors);
}

async function claimTask(request, env, cors, id) {
  const { error, user } = await requireUser(request, env, cors);
  if (error) return error;
  const task = await env.DB.prepare('SELECT * FROM volunteer_tasks WHERE id = ?').bind(id).first();
  if (!task) return json({ error: 'Not found' }, 404, cors);
  if (task.status !== 'open') return json({ error: 'Already claimed' }, 409, cors);
  const now = Date.now();
  await env.DB.batch([
    env.DB.prepare(`UPDATE volunteer_tasks SET status = 'claimed', claimed_by = ?, updated_at = ? WHERE id = ?`)
      .bind(user.id, now, id),
    // Fair rotation: claiming moves you to the back of the line for next time.
    env.DB.prepare(`INSERT INTO volunteer_queue (user_id, last_claimed_at) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET last_claimed_at = ?`)
      .bind(user.id, now, now)
  ]);
  return json({ ok: true }, 200, cors);
}

// Whoever has gone longest without claiming anything (or has never claimed) is first
// in line. Not everyone is in this queue - only members who've claimed a task before,
// so this is a rotation among people who've actually shown up before, not a broadcast
// to all 160+ members. New members who claim their first task join the queue then.
async function getVolunteerQueue(env) {
  const { results } = await env.DB.prepare(
    `SELECT u.id, u.name, u.photo_url, q.last_claimed_at FROM volunteer_queue q
     JOIN users u ON u.id = q.user_id ORDER BY q.last_claimed_at ASC`
  ).all();
  return results.map(r => ({ userId: r.id, name: r.name, photoUrl: r.photo_url, lastClaimedAt: r.last_claimed_at }));
}

// Kept as the client-facing "queue" endpoint for compatibility, but now backed by the
// real feedback.html monthly availability list (see getOrderedVolunteerAvailability),
// not the old D1-only claim history - that was the actual bug: a brand new queue that
// ignored the volunteer list you already had.
async function getVolunteerQueueHandler(request, env, cors, url) {
  const { error } = await requireUser(request, env, cors);
  if (error) return error;
  const month = url.searchParams.get('month') || MONTH_ABBREVS[new Date().getMonth()];
  return json({ month, queue: await getOrderedVolunteerAvailability(env, month) }, 200, cors);
}

async function emailVolunteerQueue(request, env, cors) {
  const { error } = await requireAdmin(request, env, cors);
  if (error) return error;
  const body = await request.json();
  if (!body.subject || !body.message) return json({ error: 'Subject and message required' }, 400, cors);
  const month = body.month || MONTH_ABBREVS[new Date().getMonth()];
  const people = await getOrderedVolunteerAvailability(env, month);
  await Promise.all(people.map(p => sendEmail(env, { to: p.email, subject: body.subject, message: body.message })));
  return json({ ok: true, sentTo: people.length }, 200, cors);
}

async function getHeadsHandler(request, env, cors) {
  const { error } = await requireUser(request, env, cors);
  if (error) return error;
  const { results } = await env.DB.prepare(
    `SELECT id, name, email, department FROM users WHERE is_dept_head = 1 ORDER BY department ASC`
  ).all();
  return json({ heads: results.map(h => ({ userId: h.id, name: h.name, email: h.email, department: h.department })) }, 200, cors);
}

const MONTH_ABBREVS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

// The real volunteer pool for a month = feedback.html's existing "which months can you
// volunteer" answers (Firestore). The rotation order on top of that pool = D1's
// last_claimed_at (never-claimed, or longest since claiming, first) - people not yet
// matched to a D1 account sort first too (nothing to move them down yet).
async function getOrderedVolunteerAvailability(env, month) {
  const people = await getFirestoreVolunteersForMonth(env, month);
  if (!people.length) return [];
  const emails = people.map(p => p.email.toLowerCase());
  const placeholders = emails.map(() => '?').join(',');
  const { results } = await env.DB.prepare(`SELECT id, email FROM users WHERE email IN (${placeholders})`).bind(...emails).all();
  const emailToUserId = Object.fromEntries(results.map(r => [r.email.toLowerCase(), r.id]));
  const userIds = results.map(r => r.id);
  let lastClaimedByUser = {};
  if (userIds.length) {
    const qp = userIds.map(() => '?').join(',');
    const q = await env.DB.prepare(`SELECT user_id, last_claimed_at FROM volunteer_queue WHERE user_id IN (${qp})`).bind(...userIds).all();
    lastClaimedByUser = Object.fromEntries(q.results.map(r => [r.user_id, r.last_claimed_at]));
  }
  const merged = people.map(p => {
    const userId = emailToUserId[p.email.toLowerCase()] || null;
    return { ...p, userId, lastClaimedAt: userId ? (lastClaimedByUser[userId] || 0) : 0 };
  });
  merged.sort((a, b) => a.lastClaimedAt - b.lastClaimedAt);
  return merged;
}


async function submitTask(request, env, cors, id) {
  const { error, user } = await requireUser(request, env, cors);
  if (error) return error;
  const task = await env.DB.prepare('SELECT * FROM volunteer_tasks WHERE id = ?').bind(id).first();
  if (!task) return json({ error: 'Not found' }, 404, cors);
  if (task.claimed_by !== user.id) return json({ error: 'Only the person who claimed this can submit it' }, 403, cors);
  const body = await request.json();
  if (!body.submittedFileUrl) return json({ error: 'submittedFileUrl required' }, 400, cors);
  await env.DB.prepare(`UPDATE volunteer_tasks SET status = 'submitted', submitted_file_url = ?, updated_at = ? WHERE id = ?`)
    .bind(body.submittedFileUrl, Date.now(), id).run();
  return json({ ok: true }, 200, cors);
}

async function reviewTask(request, env, cors, id) {
  const { error } = await requireAdminOrHead(request, env, cors);
  if (error) return error;
  const task = await env.DB.prepare('SELECT * FROM volunteer_tasks WHERE id = ?').bind(id).first();
  if (!task) return json({ error: 'Not found' }, 404, cors);
  const body = await request.json();
  const now = Date.now();
  if (body.approved) {
    const points = 15;
    await env.DB.batch([
      env.DB.prepare(`UPDATE volunteer_tasks SET status = 'approved', review_note = ?, points_awarded = ?, updated_at = ? WHERE id = ?`)
        .bind(body.note || '', points, now, id),
      env.DB.prepare(`INSERT INTO points_history (id,user_id,action,description,points,created_at) VALUES (?,?,?,?,?,?)`)
        .bind(newId(), task.claimed_by, 'volunteer_task_approved', 'Completed: ' + task.title, points, now),
      env.DB.prepare(`INSERT INTO member_points (user_id, points) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET points = points + ?`)
        .bind(task.claimed_by, points, points)
    ]);
  } else {
    await env.DB.prepare(`UPDATE volunteer_tasks SET status = 'changes_requested', review_note = ?, updated_at = ? WHERE id = ?`)
      .bind(body.note || '', now, id).run();
  }
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

      if (path === '/api/sessions' && request.method === 'POST') return await createSessionHandler(request, env, cors);
      if (path === '/api/sessions' && request.method === 'GET') return await listSessions(request, env, cors, url);

      const sessionMatch = path.match(/^\/api\/sessions\/([^/]+)(\/(.+))?$/);
      if (sessionMatch) {
        const [, id, , sub] = sessionMatch;
        if (!sub && request.method === 'GET') return await getSessionDetail(env, cors, id);
        if (!sub && request.method === 'DELETE') return await deleteSession(request, env, cors, id);
        if (sub === 'confirm' && request.method === 'POST') return await confirmSession(request, env, cors, id);
        if (sub === 'prep-complete' && request.method === 'POST') return await markPrepComplete(request, env, cors, id);
        if (sub === 'needs-help' && request.method === 'POST') return await flagNeedsHelp(request, env, cors, id);
        if (sub === 'guests' && request.method === 'POST') return await addGuest(request, env, cors, id);
        if (sub === 'checkin' && request.method === 'POST') return await checkIn(request, env, cors, id);
        if (sub === 'attendance' && request.method === 'GET') return await getAttendance(request, env, cors, id);
        if (sub === 'roles' && request.method === 'POST') return await addRole(request, env, cors, id);

        const guestConfirmMatch = sub && sub.match(/^guests\/([^/]+)\/confirm$/);
        if (guestConfirmMatch && request.method === 'POST') return await confirmGuest(request, env, cors, id, guestConfirmMatch[1]);

        const roleClaimMatch = sub && sub.match(/^roles\/([^/]+)\/claim$/);
        if (roleClaimMatch && request.method === 'POST') return await claimRole(request, env, cors, id, roleClaimMatch[1]);
      }

      if (path === '/api/volunteer-tasks' && request.method === 'POST') return await createTask(request, env, cors);
      if (path === '/api/volunteer-tasks' && request.method === 'GET') return await listTasks(request, env, cors, url);

      const taskMatch = path.match(/^\/api\/volunteer-tasks\/([^/]+)(\/(claim|submit|review))?$/);
      if (taskMatch) {
        const [, id, , sub] = taskMatch;
        if (sub === 'claim' && request.method === 'POST') return await claimTask(request, env, cors, id);
        if (sub === 'submit' && request.method === 'POST') return await submitTask(request, env, cors, id);
        if (sub === 'review' && request.method === 'POST') return await reviewTask(request, env, cors, id);
      }

      if (path === '/api/volunteer-queue' && request.method === 'GET') return await getVolunteerQueueHandler(request, env, cors, url);
      if (path === '/api/volunteer-queue/email' && request.method === 'POST') return await emailVolunteerQueue(request, env, cors);
      if (path === '/api/heads' && request.method === 'GET') return await getHeadsHandler(request, env, cors);

      return json({ error: 'Not found' }, 404, cors);
    } catch (e) {
      console.error(e);
      return json({ error: e.message || 'Internal error' }, 500, cors);
    }
  },

  // Daily cron: reminds an assigned head at 5/3/1 days before their session if they
  // still haven't confirmed, without spamming - each tier only fires once.
  async scheduled(event, env, ctx) {
    const now = Date.now();
    const { results } = await env.DB.prepare(
      `SELECT * FROM dept_sessions WHERE status = 'awaiting_confirmation' AND assigned_head_id IS NOT NULL`
    ).all();
    for (const s of results) {
      const daysUntil = Math.round((new Date(s.session_date + 'T00:00:00').getTime() - now) / 86400000);
      let tier = null;
      if (daysUntil === 5 && !s.reminder_5_sent) tier = 5;
      else if (daysUntil === 3 && !s.reminder_3_sent) tier = 3;
      else if (daysUntil === 1 && !s.reminder_1_sent) tier = 1;
      if (!tier) continue;
      await notifyUser(env, s.assigned_head_id, {
        title: `Reminder: ${s.topic} is in ${tier} day${tier === 1 ? '' : 's'}`,
        message: `Your department is leading "${s.topic}" on ${s.session_date} and it isn't confirmed yet. Please confirm and prepare.`,
        emailSubject: `YAN reminder: confirm your session (${tier} day${tier === 1 ? '' : 's'} left)`
      });
      await env.DB.prepare(`UPDATE dept_sessions SET reminder_${tier}_sent = 1 WHERE id = ?`).bind(s.id).run();
    }
  }
};
