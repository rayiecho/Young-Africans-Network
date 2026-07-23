with open('admin.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes = []

# 1. Reset attempts to 0 whenever a fresh code is sent
old_setdoc = """    await setDoc(doc(db, 'adminVerification', uid), {
      code: code,
      expiresAt: Date.now() + 10 * 60 * 1000
    });"""
new_setdoc = """    await setDoc(doc(db, 'adminVerification', uid), {
      code: code,
      expiresAt: Date.now() + 10 * 60 * 1000,
      attempts: 0
    });"""
if old_setdoc in content:
    content = content.replace(old_setdoc, new_setdoc, 1)
    changes.append("Reset attempts to 0 on new code send")
else:
    changes.append("FAILED: setDoc block not found")

# 2. Replace verifyAdminCode with attempt-tracking version
old_verify = """window.verifyAdminCode = async function() {
  const input = document.getElementById('admin-verify-input');
  const btn = document.getElementById('admin-verify-btn');
  const code = (input.value || '').trim().toUpperCase();
  if (!code) return showToast('Enter the code from your email.', 'error');
  if (!auth.currentUser) return showToast('Session expired, please sign in again.', 'error');
  btn.disabled = true; btn.textContent = 'Verifying...';
  try {
    const uid = auth.currentUser.uid;
    const snap = await getDoc(doc(db, 'adminVerification', uid));
    if (!snap.exists()) { showToast('No code found. Click Resend.', 'error'); return; }
    const data = snap.data();
    if (Date.now() > data.expiresAt) { showToast('Code expired. Click Resend.', 'error'); return; }
    if (code !== (data.code || '').toUpperCase()) { showToast('Incorrect code.', 'error'); return; }
    sessionStorage.setItem('yan_admin_verified_' + uid, 'true');
    showToast('Verified! Welcome back.');
    location.reload();
  } catch(e) {
    console.error('Admin code verification error:', e);
    showToast('Verification failed. Try again.', 'error');
  } finally {
    btn.disabled = false; btn.textContent = 'Verify & Continue';
  }
};"""

new_verify = """window.verifyAdminCode = async function() {
  const input = document.getElementById('admin-verify-input');
  const btn = document.getElementById('admin-verify-btn');
  const code = (input.value || '').trim().toUpperCase();
  if (!code) return showToast('Enter the code from your email.', 'error');
  if (!auth.currentUser) return showToast('Session expired, please sign in again.', 'error');
  btn.disabled = true; btn.textContent = 'Verifying...';
  try {
    const uid = auth.currentUser.uid;
    const snap = await getDoc(doc(db, 'adminVerification', uid));
    if (!snap.exists()) { showToast('No code found. Click Resend.', 'error'); return; }
    const data = snap.data();
    if ((data.attempts || 0) >= 3) { window.showAdminLockout(); return; }
    if (Date.now() > data.expiresAt) { showToast('Code expired. Click Resend.', 'error'); return; }
    if (code !== (data.code || '').toUpperCase()) {
      const newAttempts = (data.attempts || 0) + 1;
      await updateDoc(doc(db, 'adminVerification', uid), { attempts: newAttempts });
      if (newAttempts >= 3) { window.showAdminLockout(); return; }
      showToast('Incorrect code. ' + (3 - newAttempts) + ' attempt(s) remaining.', 'error');
      return;
    }
    await updateDoc(doc(db, 'adminVerification', uid), { attempts: 0 });
    sessionStorage.setItem('yan_admin_verified_' + uid, 'true');
    showToast('Verified! Welcome back.');
    location.reload();
  } catch(e) {
    console.error('Admin code verification error:', e);
    showToast('Verification failed. Try again.', 'error');
  } finally {
    btn.disabled = false; btn.textContent = 'Verify & Continue';
  }
};
window.showAdminLockout = function() {
  const codeBlock = document.getElementById('admin-verify-code-block');
  const lockBlock = document.getElementById('admin-verify-lockout-block');
  if (codeBlock) codeBlock.style.display = 'none';
  if (lockBlock) lockBlock.style.display = 'block';
};"""

if old_verify in content:
    content = content.replace(old_verify, new_verify, 1)
    changes.append("Replaced verifyAdminCode with attempt-tracking + lockout version")
else:
    changes.append("FAILED: verifyAdminCode block not found")

# 3. Wrap the code-entry UI in a div, add a hidden lockout panel with contact options
old_html = """<div id="screen-admin-verify" style="display:none;">
  <div class="login-card">
    <img src="images/logo.jpeg" alt="YAN Logo">
    <h2>Verify Your Sign-In</h2>
    <p>Enter the verification code sent to your email.</p>
    <input type="text" id="admin-verify-input" placeholder="Enter code" onkeydown="if(event.key==='Enter')verifyAdminCode()" style="width:100%;padding:0.85rem 1rem;border:1.5px solid rgba(27,42,107,0.15);border-radius:12px;font-family:Poppins,sans-serif;font-size:0.88rem;outline:none;box-sizing:border-box;margin-bottom:1rem;text-align:center;text-transform:uppercase;">
    <button class="btn-login" id="admin-verify-btn" onclick="verifyAdminCode()">Verify &amp; Continue</button>
    <button class="btn-login" onclick="resendAdminVerificationCode()" style="background:transparent;border:1.5px solid rgba(27,42,107,0.15);color:var(--navy);margin-top:0.75rem;">Resend Code</button>
    <a href="#" onclick="doAdminLogout();return false;" class="login-back">Sign out and use a different account</a>
  </div>
</div>"""

new_html = """<div id="screen-admin-verify" style="display:none;">
  <div class="login-card">
    <img src="images/logo.jpeg" alt="YAN Logo">
    <h2>Verify Your Sign-In</h2>
    <div id="admin-verify-code-block">
      <p>Enter the verification code sent to your email.</p>
      <input type="text" id="admin-verify-input" placeholder="Enter code" onkeydown="if(event.key==='Enter')verifyAdminCode()" style="width:100%;padding:0.85rem 1rem;border:1.5px solid rgba(27,42,107,0.15);border-radius:12px;font-family:Poppins,sans-serif;font-size:0.88rem;outline:none;box-sizing:border-box;margin-bottom:1rem;text-align:center;text-transform:uppercase;">
      <button class="btn-login" id="admin-verify-btn" onclick="verifyAdminCode()">Verify &amp; Continue</button>
      <button class="btn-login" onclick="resendAdminVerificationCode()" style="background:transparent;border:1.5px solid rgba(27,42,107,0.15);color:var(--navy);margin-top:0.75rem;">Resend Code</button>
    </div>
    <div id="admin-verify-lockout-block" style="display:none;">
      <p style="color:#E63329;font-weight:700;margin-bottom:0.75rem;">Too many incorrect attempts</p>
      <p style="margin-bottom:1.25rem;">For your security, code entry has been locked for this sign-in. Please verify your identity directly with the tech team:</p>
      <a href="tel:+254791887609" class="btn-login" style="display:block;text-decoration:none;text-align:center;margin-bottom:0.75rem;">Call +254 791 887609</a>
      <a href="https://wa.me/254791887609" target="_blank" rel="noopener" class="btn-login" style="display:block;text-decoration:none;text-align:center;background:#25D366;border-color:#25D366;color:#fff;margin-bottom:0.75rem;">Message us on WhatsApp</a>
      <a href="mailto:tech@youngafricansnetwork.org" class="btn-login" style="display:block;text-decoration:none;text-align:center;background:transparent;border:1.5px solid rgba(27,42,107,0.15);color:var(--navy);margin-bottom:0.75rem;">Email tech@youngafricansnetwork.org</a>
    </div>
    <a href="#" onclick="doAdminLogout();return false;" class="login-back">Sign out and use a different account</a>
  </div>
</div>"""

if old_html in content:
    content = content.replace(old_html, new_html, 1)
    changes.append("Added lockout panel HTML with call/WhatsApp/email fallback")
else:
    changes.append("FAILED: HTML block not found")

with open('admin.html', 'w', encoding='utf-8') as f:
    f.write(content)

for c in changes:
    print(c)
