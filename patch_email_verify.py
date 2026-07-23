with open('community.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes_made = []

# 1. Remove the three functions: sendLoginCode, verifyLoginCode, resendLoginCode
old_functions = """async function sendLoginCode(uid, email) {
  try {
    const midDocId = uid.substring(0,8).toUpperCase();
    const midSnap = await getDoc(doc(db, 'memberIds', midDocId));
    const code = midSnap.exists() ? midSnap.data().memberId : ('YAN-' + midDocId);
    await fetch('https://yan-email-worker.youngafricansn.workers.dev', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        to_email: email,
        name: 'Member',
        subject: 'Your YAN Sign-In Verification Code',
        message: 'Your verification code is: **' + code + '**\\n\\nEnter this code on the sign-in screen to continue.\\n\\nIf you did not try to sign in, you can safely ignore this email.',
        type: 'general'
      })
    });
  } catch(e) {
    console.error('[YAN Auth] Failed to send login code:', e);
    showToast('Could not send verification code. Try "Resend Code".', 'error');
  }
}

async function verifyLoginCode() {
  const input = document.getElementById('login-code-input');
  const btn = document.getElementById('verify-code-btn');
  const code = (input.value || '').trim().toUpperCase();
  if (!code) return showToast('Enter the code from your email', 'error');
  if (!auth.currentUser) return showToast('Session expired, please sign in again', 'error');
  btn.disabled = true; btn.textContent = 'Verifying...';
  try {
    const uid = auth.currentUser.uid;
    const midDocId = uid.substring(0,8).toUpperCase();
    const snap = await getDoc(doc(db, 'memberIds', midDocId));
    const actualCode = snap.exists() ? (snap.data().memberId || '').toUpperCase() : null;
    if (actualCode && code === actualCode) {
      sessionStorage.setItem('yan_login_verified_' + uid, 'true');
      showToast('Verified! Welcome back.');
      location.reload();
    } else {
      showToast('Incorrect code. Please check your email and try again.', 'error');
    }
  } catch(e) {
    console.error('[YAN Auth] Code verification error:', e);
    showToast('Verification failed. Try again.', 'error');
  } finally {
    btn.disabled = false; btn.textContent = 'Verify & Continue';
  }
}

function resendLoginCode() {
  if (auth.currentUser) {
    sendLoginCode(auth.currentUser.uid, auth.currentUser.email);
    showToast('Code resent — check your email.');
  }
}

onAuthStateChanged"""

new_functions = "onAuthStateChanged"

if old_functions in content:
    content = content.replace(old_functions, new_functions, 1)
    changes_made.append("Removed sendLoginCode/verifyLoginCode/resendLoginCode functions")
else:
    changes_made.append("FAILED: functions block not found")

# 2. Remove the per-session gate inside onAuthStateChanged
old_gate = """    // Require a fresh login-code verification every browser session
    if (!sessionStorage.getItem('yan_login_verified_' + user.uid)) {
      console.log('[YAN Auth] Login not verified this session - showing code screen');
      showScreen('screen-login-verify');
      sendLoginCode(user.uid, user.email);
      return;
    }
    // Try cached data"""

new_gate = "    // Try cached data"

if old_gate in content:
    content = content.replace(old_gate, new_gate, 1)
    changes_made.append("Removed per-session login-code gate")
else:
    changes_made.append("FAILED: gate block not found")

# 3. Remove the window exports for the deleted functions
old_export = "window.verifyLoginCode=verifyLoginCode; window.resendLoginCode=resendLoginCode;"
if old_export in content:
    content = content.replace(old_export, "", 1)
    changes_made.append("Removed window exports")
else:
    changes_made.append("FAILED: export line not found")

# 4. Remove the HTML screen for entering the login code
old_screen = """<!-- LOGIN VERIFY CODE -->
<div id="screen-login-verify" class="screen">
  <div class="auth-card" style="text-align:center;max-width:480px;">
    <img src="images/logo.jpeg" alt="YAN" style="width:70px;height:70px;border-radius:50%;border:2px solid var(--gold);margin:0 auto 1.5rem;display:block;">
    <h2 style="font-family:Playfair Display,serif;font-size:1.4rem;font-weight:900;color:var(--navy);margin-bottom:0.75rem;">Verify Your Sign-In</h2>
    <p style="color:var(--gray);font-size:0.88rem;line-height:1.7;margin-bottom:1.5rem;">We've sent a verification code to your email. Enter it below to continue.</p>
    <div class="form-group"><input type="text" id="login-code-input" placeholder="e.g. YAN-XXXXXXXX" style="text-align:center;text-transform:uppercase;"></div>
    <button onclick="verifyLoginCode()" class="btn-primary" id="verify-code-btn" style="width:100%;margin:1rem 0;">Verify & Continue</button>
    <button onclick="resendLoginCode()" class="btn-outline" style="width:100%;margin-bottom:1rem;">Resend Code</button>
    <button onclick="doSignOut()" style="background:none;border:none;color:var(--gray);font-size:0.82rem;cursor:pointer;font-family:Poppins,sans-serif;">Sign out and use a different account</button>
  </div>
</div>

"""
if old_screen in content:
    content = content.replace(old_screen, "", 1)
    changes_made.append("Removed screen-login-verify HTML block")
else:
    changes_made.append("FAILED: screen HTML block not found")

with open('community.html', 'w', encoding='utf-8') as f:
    f.write(content)

for c in changes_made:
    print(c)
