// Shared upload helper. Include with <script src="/assets/yan-upload.js"></script>.
// Images go to Cloudinary (already used everywhere else on the site, fine for photo-sized
// files - Cloudinary's preset here caps at 10MB, confirmed directly).
//
// Everything else (video, routinely multi-GB / hour-long recordings) goes to R2. Small
// files use a single streamed PUT through the Worker. Anything above SIMPLE_UPLOAD_MAX
// uses R2 multipart upload instead: the file is sliced into small chunks client-side and
// each chunk is its own HTTP request, so no single request ever has to carry a multi-GB
// body - only R2's own multipart ceiling applies (5MiB minimum / 5GiB maximum per part,
// 10,000 parts), not Cloudflare's platform request-size limit.
//
// Requests use XMLHttpRequest, not fetch: fetch gives no upload progress at all until a
// request finishes, so on a slow connection (real concern here - members are routinely on
// constrained mobile data) a single 10MB chunk can look completely frozen at "0%" for
// minutes even though it's genuinely uploading. XHR's upload.onprogress reports real
// byte-level progress as it happens, and every request has a timeout + automatic retry so
// a stalled connection fails and recovers instead of hanging silently forever.

(function () {
  const CLOUDINARY_CLOUD = 'deigiiyq5';
  const CLOUDINARY_PRESET = 'yan_Profiles';
  const OPS_BASE = 'https://yan-ops-worker.youngafricansn.workers.dev';
  const SIMPLE_UPLOAD_MAX = 15 * 1024 * 1024; // below this, one plain request beats multipart overhead
  const CHUNK_SIZE = 10 * 1024 * 1024;         // R2 requires >=5MiB per part (except the last)
  const MAX_CONCURRENT_PARTS = 3;
  const REQUEST_TIMEOUT_MS = 120000;           // per attempt - generous for a slow mobile chunk upload
  const MAX_RETRIES = 3;

  function authHeaders() {
    const token = localStorage.getItem('yan_session_token');
    if (!token) throw new Error('Please sign in again before uploading');
    return { 'Authorization': 'Bearer ' + token };
  }

  function xhrRequest(method, url, { headers = {}, body, onProgress, timeout = REQUEST_TIMEOUT_MS } = {}) {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      xhr.open(method, url);
      Object.entries(headers).forEach(([k, v]) => xhr.setRequestHeader(k, v));
      xhr.timeout = timeout;
      if (onProgress) {
        xhr.upload.onprogress = (e) => { if (e.lengthComputable) onProgress(e.loaded); };
      }
      xhr.onload = () => {
        let data = {};
        try { data = JSON.parse(xhr.responseText); } catch (e) {}
        if (xhr.status >= 200 && xhr.status < 300) resolve(data);
        else reject(new Error(data.error || ('Request failed (' + xhr.status + ')')));
      };
      xhr.onerror = () => reject(new Error('Network error - check your connection and try again'));
      xhr.ontimeout = () => reject(new Error('Upload stalled and timed out'));
      xhr.send(body);
    });
  }

  async function withRetry(fn, maxRetries = MAX_RETRIES) {
    let attempt = 0;
    while (true) {
      try { return await fn(); }
      catch (e) {
        attempt++;
        if (attempt > maxRetries) throw e;
        await new Promise(r => setTimeout(r, 1000 * attempt)); // simple backoff
      }
    }
  }

  async function uploadImage(file) {
    const fd = new FormData();
    fd.append('file', file);
    fd.append('upload_preset', CLOUDINARY_PRESET);
    const res = await fetch(`https://api.cloudinary.com/v1_1/${CLOUDINARY_CLOUD}/image/upload`, { method: 'POST', body: fd });
    const data = await res.json();
    if (!data.secure_url) throw new Error(data.error?.message || 'Upload failed');
    return data.secure_url;
  }

  async function uploadSimple(file, onProgress, filename) {
    const headers = authHeaders();
    headers['Content-Type'] = file.type || 'application/octet-stream';
    const url = OPS_BASE + '/api/upload?filename=' + encodeURIComponent(filename || file.name);
    const data = await withRetry(() => xhrRequest('POST', url, {
      headers, body: file,
      onProgress: (loaded) => { if (onProgress) onProgress(Math.min(99, Math.floor((loaded / file.size) * 100))); }
    }));
    if (!data.url) throw new Error('Upload failed');
    if (onProgress) onProgress(100);
    return data.url;
  }

  async function uploadMultipart(file, onProgress, filename) {
    const headers = authHeaders();
    const initUrl = OPS_BASE + '/api/upload/init?filename=' + encodeURIComponent(filename || file.name) + '&contentType=' + encodeURIComponent(file.type || 'application/octet-stream');
    const init = await withRetry(() => xhrRequest('POST', initUrl, { headers, timeout: 30000 }));
    if (!init.uploadId) throw new Error('Could not start upload');
    const { key, uploadId } = init;

    const totalParts = Math.ceil(file.size / CHUNK_SIZE);
    const uploadedBytes = new Array(totalParts).fill(0);
    const parts = new Array(totalParts);
    const reportProgress = () => {
      if (!onProgress) return;
      const done = uploadedBytes.reduce((a, b) => a + b, 0);
      onProgress(Math.min(99, Math.floor((done / file.size) * 100)));
    };

    let nextPart = 0;
    async function worker() {
      while (nextPart < totalParts) {
        const partNumber = ++nextPart; // R2 part numbers are 1-indexed
        const idx = partNumber - 1;
        const start = idx * CHUNK_SIZE;
        const chunk = file.slice(start, Math.min(start + CHUNK_SIZE, file.size));
        const url = OPS_BASE + '/api/upload/part?key=' + encodeURIComponent(key) + '&uploadId=' + encodeURIComponent(uploadId) + '&partNumber=' + partNumber;
        const data = await withRetry(() => xhrRequest('PUT', url, {
          headers, body: chunk,
          onProgress: (loaded) => { uploadedBytes[idx] = loaded; reportProgress(); }
        }));
        if (!data.etag) throw new Error('Part ' + partNumber + ' failed to upload');
        parts[idx] = { partNumber, etag: data.etag };
        uploadedBytes[idx] = chunk.size;
        reportProgress();
      }
    }

    try {
      await Promise.all(Array.from({ length: Math.min(MAX_CONCURRENT_PARTS, totalParts) }, worker));
    } catch (e) {
      xhrRequest('POST', OPS_BASE + '/api/upload/abort', {
        headers: { ...headers, 'Content-Type': 'application/json' },
        body: JSON.stringify({ key, uploadId })
      }).catch(() => {});
      throw e;
    }

    const completeData = await withRetry(() => xhrRequest('POST', OPS_BASE + '/api/upload/complete', {
      headers: { ...headers, 'Content-Type': 'application/json' },
      body: JSON.stringify({ key, uploadId, parts }),
      timeout: 30000
    }));
    if (!completeData.url) throw new Error('Could not finalize upload');
    if (onProgress) onProgress(100);
    return completeData.url;
  }

  window.YanUpload = {
    // filename is optional - lets the caller offer a rename before upload instead of
    // keeping whatever name the OS/recorder gave the file (e.g. a Google Meet recording's
    // auto-generated name).
    async uploadFile(file, onProgress, filename) {
      if (file.type.startsWith('image/')) return uploadImage(file);
      return file.size > SIMPLE_UPLOAD_MAX ? uploadMultipart(file, onProgress, filename) : uploadSimple(file, onProgress, filename);
    }
  };
})();
