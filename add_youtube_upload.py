with open('yan-studio.html', 'r') as f:
    content = f.read()

# 1. Add YouTube upload button on download page
old_download_btns = '''          <button class="btn btn-outline" onclick="shareWhatsApp()" style="background:#25D366;border-color:#25D366;color:#fff;">💬 Share on WhatsApp</button>
          <button class="btn btn-outline" onclick="makeAnother()">+ Make Another Video</button>'''

new_download_btns = '''          <button class="btn btn-outline" onclick="shareWhatsApp()" style="background:#25D366;border-color:#25D366;color:#fff;">💬 Share on WhatsApp</button>
          <button class="btn btn-outline" onclick="uploadToYouTube()" style="background:#FF0000;border-color:#FF0000;color:#fff;">▶ Upload to YouTube</button>
          <button class="btn btn-outline" onclick="makeAnother()">+ Make Another Video</button>'''

content = content.replace(old_download_btns, new_download_btns, 1)

# 2. Add YouTube upload JS
old_make_another = 'function makeAnother() {'
new_make_another = '''// ── YOUTUBE UPLOAD ──
const YT_CLIENT_ID = '224204618916-014ts9p8mj2vs9b0rtnq1b2o8gaetehk.apps.googleusercontent.com';
const YT_SCOPES = 'https://www.googleapis.com/auth/youtube.upload';
let ytAccessToken = null;

function initYouTubeAuth() {
  return new Promise((resolve, reject) => {
    if (ytAccessToken) { resolve(ytAccessToken); return; }
    
    const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?` +
      `client_id=${YT_CLIENT_ID}` +
      `&redirect_uri=${encodeURIComponent(window.location.href.split('?')[0])}` +
      `&response_type=token` +
      `&scope=${encodeURIComponent(YT_SCOPES)}` +
      `&include_granted_scopes=true`;

    const popup = window.open(authUrl, 'youtube-auth', 'width=500,height=600,scrollbars=yes');
    
    const interval = setInterval(() => {
      try {
        if (popup.closed) {
          clearInterval(interval);
          reject(new Error('Auth popup closed'));
          return;
        }
        const hash = popup.location.hash;
        if (hash && hash.includes('access_token')) {
          clearInterval(interval);
          popup.close();
          const params = new URLSearchParams(hash.substring(1));
          ytAccessToken = params.get('access_token');
          resolve(ytAccessToken);
        }
      } catch(e) {}
    }, 500);
  });
}

async function uploadToYouTube() {
  if (!videoBlob) { alert('No video to upload.'); return; }
  
  const statusEl = document.getElementById('download-info');
  statusEl.textContent = 'Connecting to YouTube...';
  
  try {
    const token = await initYouTubeAuth();
    statusEl.textContent = '✓ Authenticated! Uploading video...';
    
    const metadata = {
      snippet: {
        title: scriptData.title || 'YAN Video',
        description: `Generated with YAN Studio — AI Video Generator\n\nYoung Africans Network\nhttps://youngafricansnetwork.org\n\n${(scriptData.hashtags || []).join(' ')}`,
        tags: ['YAN', 'YoungAfricansNetwork', 'Africa', 'Education'],
        categoryId: '27' // Education
      },
      status: {
        privacyStatus: 'public'
      }
    };

    // Multipart upload
    const boundary = '-------314159265358979323846';
    const delimiter = '\\r\\n--' + boundary + '\\r\\n';
    const closeDelimiter = '\\r\\n--' + boundary + '--';

    const metadataStr = JSON.stringify(metadata);
    const videoArrayBuffer = await videoBlob.arrayBuffer();

    const body = new Blob([
      delimiter,
      'Content-Type: application/json\\r\\n\\r\\n',
      metadataStr,
      delimiter,
      'Content-Type: video/webm\\r\\n\\r\\n',
      new Uint8Array(videoArrayBuffer),
      closeDelimiter
    ]);

    const response = await fetch(
      'https://www.googleapis.com/upload/youtube/v3/videos?uploadType=multipart&part=snippet,status',
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': `multipart/related; boundary="${boundary}"`,
        },
        body: body
      }
    );

    const data = await response.json();
    
    if (data.id) {
      const ytUrl = `https://www.youtube.com/watch?v=${data.id}`;
      statusEl.innerHTML = `✅ Uploaded! <a href="${ytUrl}" target="_blank" style="color:#F5A623;">Watch on YouTube →</a>`;
      addLog('success', `✓ YouTube upload complete: ${ytUrl}`);
    } else {
      throw new Error(data.error?.message || 'Upload failed');
    }
    
  } catch(e) {
    statusEl.textContent = '✗ Upload failed: ' + e.message;
    addLog('error', '✗ YouTube error: ' + e.message);
  }
}

function makeAnother() {'''

content = content.replace(old_make_another, new_make_another, 1)

with open('yan-studio.html', 'w') as f:
    f.write(content)
print("✅ YouTube upload added!")
