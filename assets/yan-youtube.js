// One-click "Publish to YouTube" for admin review flows. Reuses the exact OAuth client
// already used for Google Sign-In and yan-studio.html's own YouTube upload feature (same
// client ID, same implicit-grant popup pattern) rather than building a second one - the
// only difference is the redirect lands on the dedicated oauth-callback.html, which relays
// the token back via postMessage instead of yan-studio.html's self-polling approach, so
// this works from any page without that page needing to be a registered redirect URI itself.
// Requires https://youngafricansnetwork.org/oauth-callback.html to be an Authorized
// redirect URI on that OAuth client in Google Cloud Console.

(function () {
  const YT_CLIENT_ID = '224204618916-014ts9p8mj2vs9b0rtnq1b2o8gaetehk.apps.googleusercontent.com';
  const YT_SCOPES = 'https://www.googleapis.com/auth/youtube.upload';
  let cachedToken = null;

  function requestYouTubeToken() {
    if (cachedToken) return Promise.resolve(cachedToken);
    return new Promise((resolve, reject) => {
      const redirectUri = window.location.origin + '/oauth-callback.html';
      const authUrl = 'https://accounts.google.com/o/oauth2/v2/auth?' +
        'client_id=' + YT_CLIENT_ID +
        '&redirect_uri=' + encodeURIComponent(redirectUri) +
        '&response_type=token' +
        '&scope=' + encodeURIComponent(YT_SCOPES) +
        '&include_granted_scopes=true';
      const popup = window.open(authUrl, 'yan-youtube-auth', 'width=500,height=650,scrollbars=yes');
      if (!popup) { reject(new Error('Popup blocked - please allow popups for this site')); return; }

      function onMessage(event) {
        if (event.origin !== window.location.origin || !event.data || event.data.source !== 'yan-oauth-callback') return;
        window.removeEventListener('message', onMessage);
        clearInterval(closeCheck);
        if (event.data.error) { reject(new Error(event.data.error)); return; }
        cachedToken = event.data.accessToken;
        resolve(cachedToken);
      }
      window.addEventListener('message', onMessage);

      const closeCheck = setInterval(() => {
        if (popup.closed) {
          clearInterval(closeCheck);
          window.removeEventListener('message', onMessage);
          reject(new Error('Sign-in window was closed'));
        }
      }, 500);
    });
  }

  async function publishVideoToYouTube(videoUrl, { title, description }, onStatus) {
    onStatus && onStatus('Connecting to YouTube...');
    const token = await requestYouTubeToken();

    onStatus && onStatus('Downloading video...');
    const videoRes = await fetch(videoUrl);
    if (!videoRes.ok) throw new Error('Could not fetch the video file');
    const videoBlob = await videoRes.blob();

    onStatus && onStatus('Uploading to YouTube (this can take a while for large files)...');
    const metadata = {
      snippet: { title: title || 'YAN Video', description: description || '', tags: ['YAN', 'YoungAfricansNetwork', 'Africa'], categoryId: '27' },
      status: { privacyStatus: 'public' }
    };
    const boundary = '-------314159265358979323846';
    const delimiter = '\r\n--' + boundary + '\r\n';
    const closeDelimiter = '\r\n--' + boundary + '--';
    const body = new Blob([
      delimiter, 'Content-Type: application/json\r\n\r\n', JSON.stringify(metadata),
      delimiter, 'Content-Type: ' + (videoBlob.type || 'video/mp4') + '\r\n\r\n', videoBlob,
      closeDelimiter
    ]);

    const res = await fetch('https://www.googleapis.com/upload/youtube/v3/videos?uploadType=multipart&part=snippet,status', {
      method: 'POST',
      headers: { 'Authorization': 'Bearer ' + token, 'Content-Type': 'multipart/related; boundary="' + boundary + '"' },
      body
    });
    const data = await res.json();
    if (!data.id) throw new Error(data.error?.message || 'YouTube upload failed');
    return 'https://www.youtube.com/watch?v=' + data.id;
  }

  window.YanYouTube = { publishVideoToYouTube };
})();
