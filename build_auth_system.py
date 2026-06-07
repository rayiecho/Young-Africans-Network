with open('yan-studio.html', 'r') as f:
    content = f.read()

# 1. Replace password login with Firebase Auth login screen
old_login = '''<!-- LOGIN -->
<div id="login-screen">
  <div class="login-box">
    <div class="login-logo">
      <img src="https://youngafricansnetwork.org/images/logo.jpeg" alt="YAN" onerror="this.style.display='none'">
    </div>
    <div class="login-title">YAN <span>Studio</span></div>
    <div class="login-sub">// AI VIDEO GENERATION SYSTEM</div>
    <input type="password" id="pwd-input" class="login-input" placeholder="Enter password" onkeydown="if(event.key==='Enter')checkPassword()">
    <button class="login-btn" onclick="checkPassword()">Access Studio →</button>
    <div class="login-error" id="login-error">⚠ Incorrect password. Try again.</div>
  </div>
</div>'''

new_login = '''<!-- LOGIN -->
<div id="login-screen">
  <div class="login-box">
    <div class="login-logo">
      <img src="https://youngafricansnetwork.org/images/logo.jpeg" alt="YAN" onerror="this.style.display='none'">
    </div>
    <div class="login-title">YAN <span>Studio</span></div>
    <div class="login-sub">// AI VIDEO GENERATION SYSTEM — BETA</div>
    
    <!-- AUTH TABS -->
    <div style="display:flex;margin-bottom:1.5rem;border:1px solid var(--border);border-radius:8px;overflow:hidden;">
      <button id="auth-tab-login" onclick="showAuthTab('login')" style="flex:1;padding:0.7rem;background:var(--gold);color:var(--navy);border:none;font-family:var(--font-display);font-weight:700;cursor:pointer;font-size:0.85rem;">Sign In</button>
      <button id="auth-tab-signup" onclick="showAuthTab('signup')" style="flex:1;padding:0.7rem;background:transparent;color:var(--muted);border:none;font-family:var(--font-display);font-weight:700;cursor:pointer;font-size:0.85rem;">Sign Up</button>
    </div>

    <!-- LOGIN FORM -->
    <div id="auth-login-form">
      <input type="email" id="login-email" class="login-input" placeholder="Email address" style="letter-spacing:0;margin-bottom:0.75rem;">
      <input type="password" id="login-password" class="login-input" placeholder="Password" style="letter-spacing:0;" onkeydown="if(event.key==='Enter')signIn()">
      <button class="login-btn" onclick="signIn()">Sign In →</button>
      <div style="margin-top:0.75rem;">
        <button onclick="signInGoogle()" style="width:100%;background:var(--navy3);border:1px solid var(--border);color:var(--white);padding:0.75rem;border-radius:10px;font-family:var(--font-display);font-size:0.88rem;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:0.5rem;">
          <svg width="18" height="18" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
          Continue with Google
        </button>
      </div>
    </div>

    <!-- SIGNUP FORM -->
    <div id="auth-signup-form" style="display:none;">
      <input type="text" id="signup-name" class="login-input" placeholder="Full name" style="letter-spacing:0;margin-bottom:0.75rem;">
      <input type="email" id="signup-email" class="login-input" placeholder="Email address" style="letter-spacing:0;margin-bottom:0.75rem;">
      <input type="password" id="signup-password" class="login-input" placeholder="Password (min 6 chars)" style="letter-spacing:0;" onkeydown="if(event.key==='Enter')signUp()">
      <button class="login-btn" onclick="signUp()" style="margin-top:0.75rem;">Create Account →</button>
      <div style="margin-top:0.75rem;">
        <button onclick="signInGoogle()" style="width:100%;background:var(--navy3);border:1px solid var(--border);color:var(--white);padding:0.75rem;border-radius:10px;font-family:var(--font-display);font-size:0.88rem;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:0.5rem;">
          <svg width="18" height="18" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
          Continue with Google
        </button>
      </div>
    </div>

    <div class="login-error" id="login-error">⚠ Error. Please try again.</div>
    <div style="font-size:0.72rem;color:var(--muted);margin-top:1rem;font-family:var(--font-mono);">Beta v1.0 — Free during testing period</div>
  </div>
</div>'''

content = content.replace(old_login, new_login, 1)

# 2. Add Firebase + Auth imports in head
old_head = '<link href="https://fonts.googleapis.com'
new_head = '''<script type="module">
  import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js';
  import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword, signInWithPopup, GoogleAuthProvider, onAuthStateChanged, signOut, updateProfile } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js';
  import { getFirestore, doc, setDoc, getDoc, updateDoc, increment, collection, addDoc, serverTimestamp, query, orderBy, limit, getDocs } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js';

  const firebaseConfig = {
    apiKey: "AIzaSyCs321YuksiFN3gUql_d880w48pf9Jq0Pk",
    authDomain: "young-africans-network.firebaseapp.com",
    projectId: "young-africans-network",
    storageBucket: "young-africans-network.appspot.com",
    messagingSenderId: "224204618916",
    appId: "1:224204618916:web:yan-studio"
  };

  const app = initializeApp(firebaseConfig);
  const auth = getAuth(app);
  const db = getFirestore(app);
  const googleProvider = new GoogleAuthProvider();

  // BETA LIMIT: 10 videos per user during testing
  const BETA_LIMIT = 10;
  const ADMIN_EMAILS = ['youngafricansn@gmail.com', 'reganayiecho@gmail.com'];

  let currentUser = null;
  let userProfile = null;

  // Auth state
  onAuthStateChanged(auth, async (user) => {
    if (user) {
      currentUser = user;
      await loadUserProfile(user);
      document.getElementById('login-screen').style.display = 'none';
      document.getElementById('app').style.display = 'block';
      updateUserUI();
      if (ADMIN_EMAILS.includes(user.email)) showAdminTab();
    } else {
      currentUser = null;
      document.getElementById('login-screen').style.display = 'flex';
      document.getElementById('app').style.display = 'none';
    }
  });

  async function loadUserProfile(user) {
    const ref = doc(db, 'studio_users', user.uid);
    const snap = await getDoc(ref);
    if (!snap.exists()) {
      await setDoc(ref, {
        name: user.displayName || user.email.split('@')[0],
        email: user.email,
        videosGenerated: 0,
        joinedAt: serverTimestamp(),
        plan: 'beta'
      });
      userProfile = { videosGenerated: 0, plan: 'beta' };
    } else {
      userProfile = snap.data();
    }
  }

  function updateUserUI() {
    if (!currentUser) return;
    const name = currentUser.displayName || currentUser.email.split('@')[0];
    document.getElementById('user-name-display').textContent = name;
    const remaining = BETA_LIMIT - (userProfile?.videosGenerated || 0);
    document.getElementById('user-videos-remaining').textContent = `${remaining} videos left`;
  }

  async function trackVideoGeneration(title, duration) {
    if (!currentUser) return;
    const ref = doc(db, 'studio_users', currentUser.uid);
    await updateDoc(ref, {
      videosGenerated: increment(1),
      lastVideoAt: serverTimestamp()
    });
    await addDoc(collection(db, 'studio_videos'), {
      userId: currentUser.uid,
      userEmail: currentUser.email,
      title: title,
      duration: duration,
      createdAt: serverTimestamp()
    });
    userProfile.videosGenerated = (userProfile.videosGenerated || 0) + 1;
    updateUserUI();
  }

  async function checkVideoLimit() {
    if (!currentUser) return false;
    if (ADMIN_EMAILS.includes(currentUser.email)) return true;
    const used = userProfile?.videosGenerated || 0;
    if (used >= BETA_LIMIT) {
      alert(`You have reached the beta limit of ${BETA_LIMIT} videos. Thank you for testing YAN Studio! Full access coming soon.`);
      return false;
    }
    return true;
  }

  async function submitFeedback(rating, message) {
    if (!currentUser) return;
    await addDoc(collection(db, 'studio_feedback'), {
      userId: currentUser.uid,
      userEmail: currentUser.email,
      rating: rating,
      message: message,
      createdAt: serverTimestamp()
    });
  }

  // Auth functions
  window.signIn = async function() {
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    try {
      await signInWithEmailAndPassword(auth, email, password);
    } catch(e) {
      document.getElementById('login-error').style.display = 'block';
      document.getElementById('login-error').textContent = '⚠ ' + e.message.replace('Firebase: ', '');
    }
  };

  window.signUp = async function() {
    const name = document.getElementById('signup-name').value;
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;
    if (!name || !email || !password) { alert('Please fill all fields'); return; }
    try {
      const cred = await createUserWithEmailAndPassword(auth, email, password);
      await updateProfile(cred.user, { displayName: name });
    } catch(e) {
      document.getElementById('login-error').style.display = 'block';
      document.getElementById('login-error').textContent = '⚠ ' + e.message.replace('Firebase: ', '');
    }
  };

  window.signInGoogle = async function() {
    try {
      await signInWithPopup(auth, googleProvider);
    } catch(e) {
      document.getElementById('login-error').style.display = 'block';
      document.getElementById('login-error').textContent = '⚠ ' + e.message;
    }
  };

  window.logout = async function() {
    await signOut(auth);
  };

  window.showAuthTab = function(tab) {
    document.getElementById('auth-login-form').style.display = tab === 'login' ? 'block' : 'none';
    document.getElementById('auth-signup-form').style.display = tab === 'signup' ? 'block' : 'none';
    document.getElementById('auth-tab-login').style.background = tab === 'login' ? 'var(--gold)' : 'transparent';
    document.getElementById('auth-tab-login').style.color = tab === 'login' ? 'var(--navy)' : 'var(--muted)';
    document.getElementById('auth-tab-signup').style.background = tab === 'signup' ? 'var(--gold)' : 'transparent';
    document.getElementById('auth-tab-signup').style.color = tab === 'signup' ? 'var(--navy)' : 'var(--muted)';
  };

  window.trackVideoGeneration = trackVideoGeneration;
  window.checkVideoLimit = checkVideoLimit;
  window.submitFeedback = submitFeedback;

  // Admin dashboard
  window.showAdminTab = function() {
    const tabs = document.getElementById('main-tabs');
    if (tabs && !document.getElementById('tab-admin')) {
      const btn = document.createElement('button');
      btn.className = 'main-tab';
      btn.id = 'tab-admin';
      btn.onclick = () => loadAdminDashboard();
      btn.textContent = '⚙️ Admin';
      tabs.appendChild(btn);
    }
  };

  window.loadAdminDashboard = async function() {
    // Switch to admin section
    ['create','enhance','library'].forEach(t => {
      const s = document.getElementById('section-'+t);
      const b = document.getElementById('tab-'+t);
      if(s) s.classList.remove('active');
      if(b) b.classList.remove('active');
    });
    document.getElementById('tab-admin').classList.add('active');

    // Load stats
    const usersSnap = await getDocs(query(collection(db, 'studio_users'), orderBy('videosGenerated', 'desc'), limit(50)));
    const videosSnap = await getDocs(query(collection(db, 'studio_videos'), orderBy('createdAt', 'desc'), limit(20)));
    const feedbackSnap = await getDocs(query(collection(db, 'studio_feedback'), orderBy('createdAt', 'desc'), limit(20)));

    let adminHTML = `
      <div class="card">
        <div class="card-title"><div class="card-title-icon">⚙️</div>Admin Dashboard</div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-bottom:2rem;">
          <div style="background:var(--navy3);border-radius:12px;padding:1.5rem;text-align:center;">
            <div style="font-size:2rem;font-weight:800;color:var(--gold);">${usersSnap.size}</div>
            <div style="font-size:0.78rem;color:var(--muted);font-family:var(--font-mono);">TOTAL USERS</div>
          </div>
          <div style="background:var(--navy3);border-radius:12px;padding:1.5rem;text-align:center;">
            <div style="font-size:2rem;font-weight:800;color:var(--gold);">${videosSnap.size}</div>
            <div style="font-size:0.78rem;color:var(--muted);font-family:var(--font-mono);">VIDEOS MADE</div>
          </div>
          <div style="background:var(--navy3);border-radius:12px;padding:1.5rem;text-align:center;">
            <div style="font-size:2rem;font-weight:800;color:var(--gold);">${feedbackSnap.size}</div>
            <div style="font-size:0.78rem;color:var(--muted);font-family:var(--font-mono);">FEEDBACKS</div>
          </div>
        </div>

        <div style="font-size:0.88rem;font-weight:700;margin-bottom:1rem;color:var(--gold);font-family:var(--font-mono);">TOP USERS</div>
        ${usersSnap.docs.map(d => {
          const u = d.data();
          return `<div style="display:flex;justify-content:space-between;padding:0.75rem;background:var(--navy3);border-radius:8px;margin-bottom:0.5rem;font-size:0.82rem;">
            <span>${u.name || u.email}</span>
            <span style="color:var(--gold);font-family:var(--font-mono);">${u.videosGenerated || 0} videos</span>
          </div>`;
        }).join('')}

        <div style="font-size:0.88rem;font-weight:700;margin:1.5rem 0 1rem;color:var(--gold);font-family:var(--font-mono);">RECENT FEEDBACK</div>
        ${feedbackSnap.docs.map(d => {
          const f = d.data();
          return `<div style="padding:0.75rem;background:var(--navy3);border-radius:8px;margin-bottom:0.5rem;font-size:0.82rem;">
            <div style="color:var(--gold);margin-bottom:0.25rem;">${'⭐'.repeat(f.rating || 0)} — ${f.userEmail}</div>
            <div style="color:var(--muted);">${f.message || ''}</div>
          </div>`;
        }).join('')}
      </div>`;

    let adminSection = document.getElementById('section-admin');
    if (!adminSection) {
      adminSection = document.createElement('div');
      adminSection.className = 'main-section active';
      adminSection.id = 'section-admin';
      document.querySelector('.main').appendChild(adminSection);
    } else {
      adminSection.className = 'main-section active';
    }
    adminSection.innerHTML = adminHTML;
  };

  // Feedback modal
  window.openFeedback = function() {
    document.getElementById('feedback-modal').style.display = 'flex';
  };

  window.closeFeedback = function() {
    document.getElementById('feedback-modal').style.display = 'none';
  };

  window.sendFeedback = async function() {
    const rating = document.querySelector('.star-btn.selected')?.dataset.rating || 0;
    const message = document.getElementById('feedback-message').value;
    if (!message) { alert('Please write something'); return; }
    await submitFeedback(parseInt(rating), message);
    closeFeedback();
    alert('Thank you for your feedback! 🙏');
    document.getElementById('feedback-message').value = '';
    document.querySelectorAll('.star-btn').forEach(b => b.classList.remove('selected'));
  };

</script>
<link href="https://fonts.googleapis.com'''

content = content.replace(old_head, new_head, 1)

# 3. Update header to show user info + feedback button
old_header_logout = '<button class="header-logout" onclick="logout()">Sign Out</button>'
new_header_logout = '''<div style="display:flex;align-items:center;gap:1rem;">
      <div style="text-align:right;">
        <div style="font-size:0.82rem;font-weight:600;" id="user-name-display">Loading...</div>
        <div style="font-size:0.7rem;color:var(--gold);font-family:var(--font-mono);" id="user-videos-remaining"></div>
      </div>
      <button onclick="openFeedback()" style="background:rgba(245,166,35,0.12);border:1px solid var(--border);color:var(--gold);padding:0.4rem 1rem;border-radius:8px;font-family:var(--font-display);font-size:0.78rem;cursor:pointer;">💬 Feedback</button>
      <button class="header-logout" onclick="logout()">Sign Out</button>
    </div>'''

content = content.replace(old_header_logout, new_header_logout, 1)

# 4. Add feedback modal + check limit before generating
old_app_end = '</div>\n\n<script>'
new_app_end = '''</div>

<!-- FEEDBACK MODAL -->
<div id="feedback-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.8);z-index:9999;align-items:center;justify-content:center;padding:2rem;">
  <div style="background:var(--navy2);border:1px solid var(--border);border-radius:20px;padding:2rem;width:100%;max-width:480px;">
    <div style="font-size:1.2rem;font-weight:800;margin-bottom:0.5rem;">Share Your Feedback</div>
    <div style="font-size:0.82rem;color:var(--muted);margin-bottom:1.5rem;font-family:var(--font-mono);">Help us improve YAN Studio during beta</div>
    <div style="display:flex;gap:0.5rem;margin-bottom:1.5rem;">
      ${[1,2,3,4,5].map(n => `<button class="star-btn" data-rating="${n}" onclick="document.querySelectorAll('.star-btn').forEach(b=>b.classList.remove('selected'));this.classList.add('selected');document.querySelectorAll('.star-btn').forEach((b,i)=>{if(i<${n})b.style.color='#F5A623';else b.style.color='var(--muted)'})" style="flex:1;background:var(--navy3);border:1px solid var(--border);color:var(--muted);padding:0.75rem;border-radius:8px;font-size:1.2rem;cursor:pointer;">⭐</button>`).join('')}
    </div>
    <textarea id="feedback-message" style="width:100%;background:var(--navy3);border:1px solid var(--border);color:var(--white);padding:0.85rem;border-radius:10px;font-family:var(--font-display);font-size:0.88rem;resize:vertical;min-height:100px;outline:none;margin-bottom:1rem;" placeholder="What's working well? What needs improvement?"></textarea>
    <div style="display:flex;gap:1rem;">
      <button onclick="sendFeedback()" style="flex:1;background:var(--gold);color:var(--navy);border:none;padding:0.85rem;border-radius:10px;font-weight:700;cursor:pointer;">Send Feedback</button>
      <button onclick="closeFeedback()" style="background:transparent;border:1px solid var(--border);color:var(--white);padding:0.85rem 1.5rem;border-radius:10px;cursor:pointer;">Cancel</button>
    </div>
  </div>
</div>

<script>'''

content = content.replace(old_app_end, new_app_end, 1)

# 5. Add limit check before script generation and track after
old_gen_start = "async function generateScript() {\n  if (currentMode === 'own') {\n    await structureOwnScript();\n    return;\n  }\n  const topic = document.getElementById('video-topic').value.trim();\n  if (!topic) { alert('Please enter a video topic first.'); return; }"

new_gen_start = """async function generateScript() {
  // Check beta limit
  if (window.checkVideoLimit && !(await window.checkVideoLimit())) return;

  if (currentMode === 'own') {
    await structureOwnScript();
    return;
  }
  const topic = document.getElementById('video-topic').value.trim();
  if (!topic) { alert('Please enter a video topic first.'); return; }"""

content = content.replace(old_gen_start, new_gen_start, 1)

# Track video after generation
old_track = "  addLog('success', '📚 Saved to Video Library!');"
new_track = """  addLog('success', '📚 Saved to Video Library!');
  if (window.trackVideoGeneration) window.trackVideoGeneration(scriptData.title, scriptData.duration);"""

content = content.replace(old_track, new_track, 1)

with open('yan-studio.html', 'w') as f:
    f.write(content)
print("✅ Full auth system built!")
