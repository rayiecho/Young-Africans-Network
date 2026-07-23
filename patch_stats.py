with open('index.html') as f:
    content = f.read()

old = """async function loadLiveStats() {
  try {
    const [usersSnap, certsSnap] = await Promise.all([
      getDocs(collection(db, 'users')),
      getDocs(collection(db, 'certificates'))
    ]);
    const members = usersSnap.size;
    const countries = new Set(usersSnap.docs.map(d => d.data().country).filter(Boolean)).size;
    const certs = certsSnap.docs.filter(d => d.data().status == 'approved').length;"""

new = """async function loadLiveStats() {
  try {
    const statsSnap = await getDoc(doc(db, 'config', 'publicStats'));
    if (statsSnap.exists() == false) { console.log('Stats load error: publicStats doc missing'); return; }
    const data = statsSnap.data();
    const members = data.members;
    const countries = data.countries;
    const certs = data.certs;"""

if old not in content:
    print('FUNCTION BODY NOT FOUND — abort, paste this back to Claude')
else:
    content = content.replace(old, new)
    with open('index.html', 'w') as f:
        f.write(content)
    print('Function body patched')
