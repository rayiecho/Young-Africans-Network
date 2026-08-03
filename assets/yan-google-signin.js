// Client-side Google Sign-In using Google Identity Services (GSI), replacing Firebase Auth's
// signInWithPopup/GoogleAuthProvider. Requires a real Google OAuth 2.0 Client ID with
// youngafricansnetwork.org (and young-africans-network.web.app for testing) added under
// "Authorized JavaScript origins" in Google Cloud Console -> APIs & Services -> Credentials.
// Set it below AND as the GOOGLE_CLIENT_ID var in cf-backend/auth-worker/wrangler.toml -
// both sides must reference the same client ID or token verification will fail.

(function () {
  const GOOGLE_CLIENT_ID = 'REPLACE_WITH_GOOGLE_OAUTH_CLIENT_ID';
  let gsiLoaded = false;

  function loadGsiScript() {
    if (gsiLoaded) return Promise.resolve();
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = 'https://accounts.google.com/gsi/client';
      script.onload = () => { gsiLoaded = true; resolve(); };
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  // Returns a Promise resolving to the raw Google ID token (JWT) for use with YanAPI.googleSignIn().
  function requestGoogleIdToken() {
    return loadGsiScript().then(() => new Promise((resolve, reject) => {
      window.google.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: (response) => {
          if (response && response.credential) resolve(response.credential);
          else reject(new Error('Google sign-in was cancelled'));
        }
      });
      window.google.accounts.id.prompt((notification) => {
        if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
          // One-tap prompt was blocked/dismissed - fall back to the popup button flow.
          renderFallbackButton(resolve, reject);
        }
      });
    }));
  }

  function renderFallbackButton(resolve, reject) {
    const container = document.createElement('div');
    container.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.4);z-index:99999;display:flex;align-items:center;justify-content:center;';
    const box = document.createElement('div');
    box.style.cssText = 'background:#fff;padding:2rem;border-radius:16px;text-align:center;';
    box.innerHTML = '<p style="margin-bottom:1rem;font-family:sans-serif;color:#1B2A6B;">Sign in with Google</p>';
    const btnHolder = document.createElement('div');
    box.appendChild(btnHolder);
    const cancelBtn = document.createElement('button');
    cancelBtn.textContent = 'Cancel';
    cancelBtn.style.cssText = 'margin-top:1rem;background:none;border:none;color:#888;cursor:pointer;font-family:sans-serif;';
    cancelBtn.onclick = () => { container.remove(); reject(new Error('Google sign-in was cancelled')); };
    box.appendChild(cancelBtn);
    container.appendChild(box);
    document.body.appendChild(container);

    window.google.accounts.id.renderButton(btnHolder, { theme: 'outline', size: 'large', text: 'continue_with' });
    window.google.accounts.id.initialize({
      client_id: GOOGLE_CLIENT_ID,
      callback: (response) => {
        container.remove();
        if (response && response.credential) resolve(response.credential);
        else reject(new Error('Google sign-in was cancelled'));
      }
    });
  }

  window.YanGoogleSignIn = { requestGoogleIdToken };
})();
