// Reads the Firebase Auth export (cf-backend/migration/firebase-users-export.json,
// produced by `firebase auth:export ... --format=json`) plus each user's Firestore
// profile doc, and generates a D1-ready SQL file that imports them preserving the
// original Firebase UID as the D1 primary key (so the custom-token bridge in
// firebase-bridge.js signs into the SAME account community.html already knows).
//
// Run from repo root: NODE_PATH=functions/node_modules node cf-backend/migration/import-users-to-d1.js
// Then apply with: npx wrangler d1 execute yan-db --remote --file=cf-backend/migration/import-users.sql
//   (from inside cf-backend/) - review the generated file before applying.

const fs = require('fs');
const path = require('path');
const admin = require('firebase-admin');
const sa = require(path.join(__dirname, '../../serviceAccount.json'));

admin.initializeApp({ credential: admin.credential.cert(sa) });
const db = admin.firestore();

function sqlStr(v) {
  if (v === null || v === undefined) return 'NULL';
  return `'${String(v).replace(/'/g, "''")}'`;
}
function sqlInt(v) {
  if (v === null || v === undefined) return 'NULL';
  return String(v);
}
function tsToMs(ts) {
  if (!ts) return null;
  if (ts._seconds !== undefined) return ts._seconds * 1000 + Math.floor((ts._nanoseconds || 0) / 1e6);
  return null;
}

async function main() {
  const exportPath = path.join(__dirname, 'firebase-users-export.json');
  const { users: authUsers } = JSON.parse(fs.readFileSync(exportPath, 'utf8'));
  console.log(`Loaded ${authUsers.length} auth users from export.`);

  const profiles = {};
  const snap = await db.collection('users').get();
  snap.forEach(d => { profiles[d.id] = d.data(); });
  console.log(`Loaded ${Object.keys(profiles).length} Firestore user profiles.`);

  const statements = [];
  let matched = 0, skippedNoProfile = 0;

  for (const au of authUsers) {
    const uid = au.localId;
    const profile = profiles[uid];
    if (!profile) { skippedNoProfile++; continue; }
    matched++;

    const passwordHash = au.passwordHash && au.salt ? `fbscrypt$${au.salt}$${au.passwordHash}` : null;
    const now = Date.now();
    const joinedAt = tsToMs(profile.joinedAt) || now;
    const createdAt = tsToMs(profile.createdAt) || joinedAt;

    statements.push(
      `INSERT INTO users (id,name,email,password_hash,photo_url,role,department,country,whatsapp,dob,bio,` +
      `is_admin,is_dept_head,is_exec,email_verified,profile_complete,referred_by,joined_at,created_at,updated_at) VALUES (` +
      [
        sqlStr(uid), sqlStr(profile.name || 'YAN Member'), sqlStr((au.email || profile.email || '').toLowerCase()),
        sqlStr(passwordHash), sqlStr(profile.photoUrl || null), sqlStr(profile.role || 'Member'),
        sqlStr(profile.department || null), sqlStr(profile.country || null), sqlStr(profile.whatsapp || null),
        sqlStr(profile.dob || null), sqlStr(profile.bio || ''), profile.isAdmin ? 1 : 0, profile.isDeptHead ? 1 : 0,
        profile.isExec ? 1 : 0, au.emailVerified ? 1 : 0, profile.profileComplete ? 1 : 0, sqlStr(profile.referredBy || ''),
        sqlInt(joinedAt), sqlInt(createdAt), sqlInt(now)
      ].join(',') + ');'
    );

    if (au.providerUserInfo && au.providerUserInfo.some(p => p.providerId === 'google.com')) {
      statements.push(
        `INSERT INTO auth_providers (id,user_id,provider,provider_uid,created_at) VALUES (` +
        [sqlStr(crypto.randomUUID()), sqlStr(uid), sqlStr('google.com'),
          sqlStr(au.providerUserInfo.find(p => p.providerId === 'google.com').rawId || ''), sqlInt(now)].join(',') + ');'
      );
    }
    if (passwordHash) {
      statements.push(
        `INSERT INTO auth_providers (id,user_id,provider,created_at) VALUES (` +
        [sqlStr(crypto.randomUUID()), sqlStr(uid), sqlStr('password'), sqlInt(now)].join(',') + ');'
      );
    }
    statements.push(`INSERT INTO member_points (user_id, points) VALUES (${sqlStr(uid)}, 0);`);
  }

  const outPath = path.join(__dirname, 'import-users.sql');
  fs.writeFileSync(outPath, statements.join('\n') + '\n');
  console.log(`Matched ${matched} users (${skippedNoProfile} auth-only accounts skipped - no Firestore profile).`);
  console.log(`Wrote ${statements.length} statements to ${outPath}`);
}

main().catch(e => { console.error(e); process.exit(1); });
