const admin = require('firebase-admin');
const serviceAccount = require('./serviceAccount.json');
admin.initializeApp({ credential: admin.credential.cert(serviceAccount) });
const db = admin.firestore();

async function run() {
  const usersSnap = await db.collection('users').get();
  const certsSnap = await db.collection('certificates').get();
  const members = usersSnap.size;
  const countries = new Set(usersSnap.docs.map(d => d.data().country).filter(Boolean)).size;
  const certs = certsSnap.docs.filter(d => d.data().status === 'approved').length;
  await db.collection('config').doc('publicStats').set({
    members, countries, certs,
    updatedAt: admin.firestore.FieldValue.serverTimestamp()
  });
  console.log({ members, countries, certs });
}
run().then(() => process.exit(0)).catch(e => { console.error(e); process.exit(1); });
