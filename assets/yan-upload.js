// Shared upload helper. Include with <script src="/assets/yan-upload.js"></script>.
// Images go to Cloudinary (already used everywhere else on the site, fine for photo-sized
// files). Video goes to R2 via the ops-worker instead: the Cloudinary preset in use here
// has a hard 10MB cap (confirmed directly - Cloudinary itself rejects anything larger with
// "File size too large"), and real files here (Google Meet recordings, edited video) are
// routinely far bigger than that. R2 has no such preset-level cap - the file streams
// straight through the Worker to the bucket without ever being buffered in memory, so the
// only real ceiling is Cloudflare's own platform request-size limit, not anything imposed
// here. Verified end-to-end (upload -> public URL -> fetched back, byte-for-byte).

(function () {
  const CLOUDINARY_CLOUD = 'deigiiyq5';
  const CLOUDINARY_PRESET = 'yan_Profiles';
  const UPLOAD_ENDPOINT = 'https://yan-ops-worker.youngafricansn.workers.dev/api/upload';

  async function uploadImage(file) {
    const fd = new FormData();
    fd.append('file', file);
    fd.append('upload_preset', CLOUDINARY_PRESET);
    const res = await fetch(`https://api.cloudinary.com/v1_1/${CLOUDINARY_CLOUD}/image/upload`, { method: 'POST', body: fd });
    const data = await res.json();
    if (!data.secure_url) throw new Error(data.error?.message || 'Upload failed');
    return data.secure_url;
  }

  async function uploadToR2(file) {
    const token = localStorage.getItem('yan_session_token');
    if (!token) throw new Error('Please sign in again before uploading');
    const res = await fetch(UPLOAD_ENDPOINT + '?filename=' + encodeURIComponent(file.name), {
      method: 'POST',
      headers: { 'Authorization': 'Bearer ' + token, 'Content-Type': file.type || 'application/octet-stream' },
      body: file
    });
    const data = await res.json();
    if (!res.ok || !data.url) throw new Error(data.error || 'Upload failed');
    return data.url;
  }

  window.YanUpload = {
    async uploadFile(file) {
      return file.type.startsWith('image/') ? uploadImage(file) : uploadToR2(file);
    }
  };
})();
