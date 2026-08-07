// Replaces the floating WhatsApp button's wa.me redirect. Visitors no longer leave the
// site - they type their message and phone number in place, and it's emailed straight to
// every admin (same delivery mechanism as join/contact form submissions), who can then
// reply on real WhatsApp using the number provided. Include with
// <script src="/assets/yan-whatsapp-widget.js"></script> - injects its own modal markup,
// no HTML changes needed beyond swapping the button's onclick.

(function () {
  const ENDPOINT = 'https://yan-content-worker.youngafricansn.workers.dev/api/quick-message';

  function injectModal() {
    if (document.getElementById('qm-overlay')) return;
    const overlay = document.createElement('div');
    overlay.id = 'qm-overlay';
    overlay.style.cssText = 'display:none;position:fixed;inset:0;background:rgba(13,27,75,0.55);z-index:999999;align-items:center;justify-content:center;padding:1rem;';
    overlay.innerHTML = `<div style="background:#fff;border-radius:20px;padding:1.75rem;max-width:400px;width:100%;box-shadow:0 20px 60px rgba(0,0,0,0.3);font-family:Poppins,sans-serif;">
      <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:1rem;">
        <div style="width:36px;height:36px;border-radius:50%;background:#25D366;display:flex;align-items:center;justify-content:center;flex-shrink:0;">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="#fff"><path d="M17.6 6.32A7.85 7.85 0 0 0 12.05 4a7.94 7.94 0 0 0-6.9 11.9L4 20l4.2-1.1a7.93 7.93 0 0 0 3.8 1h0a7.94 7.94 0 0 0 5.6-13.58zm-5.55 12.2h0a6.6 6.6 0 0 1-3.37-.92l-.24-.14-2.5.66.67-2.44-.16-.25a6.6 6.6 0 1 1 12.24-3.5 6.56 6.56 0 0 1-6.64 6.6zm3.6-4.94c-.2-.1-1.17-.58-1.35-.64s-.32-.1-.45.1-.5.63-.62.76-.23.15-.43.05a5.4 5.4 0 0 1-1.6-.98 6 6 0 0 1-1.1-1.37c-.12-.2 0-.3.09-.4.09-.1.2-.24.3-.36.1-.12.13-.2.2-.34.06-.13.03-.25 0-.35s-.45-1.1-.62-1.5c-.16-.4-.33-.33-.45-.34h-.38a.73.73 0 0 0-.53.25 2.2 2.2 0 0 0-.7 1.65 3.85 3.85 0 0 0 .82 2.03 8.8 8.8 0 0 0 3.36 3c.47.2.84.32 1.12.41.47.15.9.13 1.24.08.38-.06 1.17-.48 1.33-.94.17-.46.17-.85.12-.94-.05-.09-.18-.14-.38-.24z"/></svg>
        </div>
        <h3 style="font-family:'Playfair Display',serif;font-size:1.05rem;color:#1B2A6B;margin:0;">Message YAN</h3>
      </div>
      <p style="font-size:0.8rem;color:#6B7280;margin-bottom:1rem;">Send us a message and your number - we'll get back to you on WhatsApp.</p>
      <div style="margin-bottom:0.85rem;"><label style="font-size:0.78rem;font-weight:700;color:#1B2A6B;display:block;margin-bottom:0.35rem;">Your name (optional)</label>
        <input type="text" id="qm-name" style="width:100%;padding:0.65rem 0.85rem;border:1.5px solid rgba(27,42,107,0.15);border-radius:10px;font-family:Poppins,sans-serif;font-size:0.85rem;box-sizing:border-box;"></div>
      <div style="margin-bottom:0.85rem;"><label style="font-size:0.78rem;font-weight:700;color:#1B2A6B;display:block;margin-bottom:0.35rem;">Your WhatsApp number</label>
        <input type="tel" id="qm-phone" placeholder="+254 700 000 000" style="width:100%;padding:0.65rem 0.85rem;border:1.5px solid rgba(27,42,107,0.15);border-radius:10px;font-family:Poppins,sans-serif;font-size:0.85rem;box-sizing:border-box;"></div>
      <div style="margin-bottom:1.25rem;"><label style="font-size:0.78rem;font-weight:700;color:#1B2A6B;display:block;margin-bottom:0.35rem;">Message</label>
        <textarea id="qm-message" rows="4" placeholder="Hi YAN, I need some help..." style="width:100%;padding:0.65rem 0.85rem;border:1.5px solid rgba(27,42,107,0.15);border-radius:10px;font-family:Poppins,sans-serif;font-size:0.85rem;box-sizing:border-box;resize:vertical;"></textarea></div>
      <div id="qm-status" style="font-size:0.78rem;color:#6B7280;margin-bottom:0.75rem;"></div>
      <div style="display:flex;gap:0.6rem;justify-content:flex-end;">
        <button onclick="YanWhatsAppWidget.close()" style="background:#F8F9FF;color:#1B2A6B;border:none;padding:0.65rem 1.4rem;border-radius:50px;font-family:Poppins,sans-serif;font-weight:700;cursor:pointer;">Cancel</button>
        <button id="qm-submit" onclick="YanWhatsAppWidget.submit()" style="background:#25D366;color:#fff;border:none;padding:0.65rem 1.4rem;border-radius:50px;font-family:Poppins,sans-serif;font-weight:700;cursor:pointer;">Send</button>
      </div>
    </div>`;
    document.body.appendChild(overlay);
  }

  function open() {
    injectModal();
    document.getElementById('qm-name').value = '';
    document.getElementById('qm-phone').value = '';
    document.getElementById('qm-message').value = '';
    document.getElementById('qm-status').textContent = '';
    document.getElementById('qm-overlay').style.display = 'flex';
  }

  function close() {
    const overlay = document.getElementById('qm-overlay');
    if (overlay) overlay.style.display = 'none';
  }

  async function submit() {
    const name = document.getElementById('qm-name').value.trim();
    const phone = document.getElementById('qm-phone').value.trim();
    const message = document.getElementById('qm-message').value.trim();
    const status = document.getElementById('qm-status');
    if (!phone || !message) { status.textContent = 'Please enter your number and a message.'; status.style.color = '#E63329'; return; }
    const btn = document.getElementById('qm-submit');
    btn.disabled = true;
    status.style.color = '#6B7280';
    status.textContent = 'Sending...';
    try {
      const res = await fetch(ENDPOINT, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, phone, message })
      });
      if (!res.ok) throw new Error((await res.json().catch(() => ({}))).error || 'Could not send');
      status.style.color = '#27AE60';
      status.textContent = "Sent! We'll message you on WhatsApp soon.";
      setTimeout(close, 2200);
    } catch (e) {
      status.style.color = '#E63329';
      status.textContent = e.message;
    } finally {
      btn.disabled = false;
    }
  }

  window.YanWhatsAppWidget = { open, close, submit };
})();
