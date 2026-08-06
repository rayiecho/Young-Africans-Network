// Shared upload helper. Include with <script src="/assets/yan-upload.js"></script>.
// Images go to Cloudinary (already used everywhere else on the site, fine for photo-sized
// files - Cloudinary's preset here caps at 10MB, confirmed directly).
//
// Everything else (video, routinely multi-GB / hour-long recordings) goes to R2. Small
// files use a single streamed PUT through the Worker. Anything above SIMPLE_UPLOAD_MAX
// uses R2 multipart upload instead: the file is sliced into small chunks client-side and
// each chunk is its own HTTP request, so no single request ever has to carry a multi-GB
// body - only R2's own multipart ceiling applies (5GiB/part, 10,000 parts), not
// Cloudflare's platform request-size limit. Verified end-to-end (upload -> public URL ->
// fetched back, byte-for-byte).

(function () {
  const CLOUDINARY_CLOUD = 'deigiiyq5';
  const CLOUDINARY_PRESET = 'yan_Profiles';
  const OPS_BASE = 'https://yan-ops-worker.youngafricansn.workers.dev';
  const SIMPLE_UPLOAD_MAX = 15 * 1024 * 1024; // below this, one plain request beats multipart overhead
  const CHUNK_SIZE = 10 * 1024 * 1024;         // well above R2's 5MiB/part minimum
  const MAX_CONCURRENT_PARTS = 4;

  function authHeaders() {
    const token = localStorage.getItem('yan_session_token');
    if (!token) throw new Error('Please sign in again before uploading');
    return { 'Authorization': 'Bearer ' + token };
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
    const res = await fetch(OPS_BASE + '/api/upload?filename=' + encodeURIComponent(filename || file.name), {
      method: 'POST', headers, body: file
    });
    const data = await res.json();
    if (!res.ok || !data.url) throw new Error(data.error || 'Upload failed');
    if (onProgress) onProgress(100);
    return data.url;
  }

  async function uploadMultipart(file, onProgress, filename) {
    const headers = authHeaders();
    const initRes = await fetch(
      OPS_BASE + '/api/upload/init?filename=' + encodeURIComponent(filename || file.name) + '&contentType=' + encodeURIComponent(file.type || 'application/octet-stream'),
      { method: 'POST', headers }
    );
    const init = await initRes.json();
    if (!initRes.ok || !init.uploadId) throw new Error(init.error || 'Could not start upload');
    const { key, uploadId } = init;

    const totalParts = Math.ceil(file.size / CHUNK_SIZE);
    const parts = new Array(totalParts);
    const uploadedBytes = new Array(totalParts).fill(0);
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
        const res = await fetch(
          OPS_BASE + '/api/upload/part?key=' + encodeURIComponent(key) + '&uploadId=' + encodeURIComponent(uploadId) + '&partNumber=' + partNumber,
          { method: 'PUT', headers, body: chunk }
        );
        const data = await res.json();
        if (!res.ok || !data.etag) throw new Error(data.error || ('Part ' + partNumber + ' failed to upload'));
        parts[idx] = { partNumber, etag: data.etag };
        uploadedBytes[idx] = chunk.size;
        reportProgress();
      }
    }

    try {
      await Promise.all(Array.from({ length: Math.min(MAX_CONCURRENT_PARTS, totalParts) }, worker));
    } catch (e) {
      fetch(OPS_BASE + '/api/upload/abort', {
        method: 'POST', headers: { ...headers, 'Content-Type': 'application/json' },
        body: JSON.stringify({ key, uploadId })
      }).catch(() => {});
      throw e;
    }

    const completeRes = await fetch(OPS_BASE + '/api/upload/complete', {
      method: 'POST', headers: { ...headers, 'Content-Type': 'application/json' },
      body: JSON.stringify({ key, uploadId, parts })
    });
    const data = await completeRes.json();
    if (!completeRes.ok || !data.url) throw new Error(data.error || 'Could not finalize upload');
    if (onProgress) onProgress(100);
    return data.url;
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
