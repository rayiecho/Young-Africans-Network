with open('community.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_block = """  const printWin = window.open('', '_blank', 'width=1400,height=850');
  printWin.document.write('<!DOCTYPE html><html><head><meta charset="UTF-8">'
    + '<div class="no-print" style="background:#f0ece4;padding:10px;font-family:Montserrat,sans-serif;font-size:11px;color:#666;text-align:center;margin-bottom:8px;">'
    + '&#9432; <strong style="color:#E63329;">PDF:</strong> Set <strong>Orientation = Landscape</strong>, Paper = A4, Margins = None'
    + ' &nbsp;|&nbsp; <button onclick="window.print()" style="background:#1B2A6B;color:#fff;border:none;padding:4px 16px;border-radius:4px;cursor:pointer;font-weight:700;font-family:Montserrat,sans-serif;">&#128424; Save as PDF</button>'
    + ' &nbsp;|&nbsp; <button onclick="saveCertAsImage(this)" style="background:#27AE60;color:#fff;border:none;padding:4px 16px;border-radius:4px;cursor:pointer;font-weight:700;font-family:Montserrat,sans-serif;">&#128248; Save as Image</button>'
    + '</div>'
    + body
    + '<scr' + 'ipt>'
    + 'function saveCertAsImage(btn){'
    + '  btn.textContent = "Generating..."; btn.disabled = true;'
    + '  var cert = document.querySelector(".cert");'
    + '  var wrap = document.querySelector(".cert").parentElement;'
    + '  window.opener.saveCertFromPopup(wrap, btn);'
    + '}'
    + 'setTimeout(function(){ window.print(); },1500);'
    + '<\\/script><\\/bo' + 'dy><\\/html>');
  printWin.document.close();
}"""

new_block = """  showToast('Generating your certificate...');
  const holder = document.createElement('div');
  holder.id = 'yan-cert-render-holder';
  holder.style.cssText = 'position:fixed;top:0;left:-99999px;width:297mm;height:210mm;z-index:-1;';
  holder.innerHTML = '<style>' + css + '</style>' + body;
  document.body.appendChild(holder);

  const imgs = Array.from(holder.querySelectorAll('img'));
  await Promise.all(imgs.map(img => img.complete ? Promise.resolve() : new Promise(resolve => {
    img.addEventListener('load', resolve, {once:true});
    img.addEventListener('error', resolve, {once:true});
  })));
  await new Promise(resolve => setTimeout(resolve, 300));

  const certEl = holder.querySelector('.cert');
  html2canvas(certEl, {
    scale: 2,
    useCORS: true,
    backgroundColor: '#fff',
    width: certEl.scrollWidth,
    height: certEl.scrollHeight
  }).then(function(canvas) {
    document.body.removeChild(holder);
    const imgData = canvas.toDataURL('image/png');
    const pdf = new jspdf.jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' });
    pdf.addImage(imgData, 'PNG', 0, 0, 297, 210);
    pdf.save('YAN-Certificate-' + memberName.replace(/ /g, '_') + '.pdf');
    showToast('Certificate downloaded!');
  }).catch(function(e) {
    if (document.body.contains(holder)) document.body.removeChild(holder);
    showToast('Certificate generation failed: ' + e.message, 'error');
  });
}"""

if old_block not in content:
    print("OLD BLOCK NOT FOUND - abort")
else:
    content = content.replace(old_block, new_block, 1)
    # add crossorigin to the QR image to reduce canvas-tainting risk
    content = content.replace(
        "'<img src=\"https://api.qrserver.com/v1/create-qr-code/?size=80x80&data=' + encodeURIComponent(verifyUrl) + '\" style=\"width:75px;height:75px;display:block;\" alt=\"QR Code\"/>'",
        "'<img src=\"https://api.qrserver.com/v1/create-qr-code/?size=80x80&data=' + encodeURIComponent(verifyUrl) + '\" crossorigin=\"anonymous\" style=\"width:75px;height:75px;display:block;\" alt=\"QR Code\"/>'"
    )
    # add jsPDF script tag next to the existing html2canvas script tag
    old_script = '<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>'
    new_script = old_script + '\\n<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>'
    if old_script in content:
        content = content.replace(old_script, new_script, 1)
        script_status = "jsPDF script tag added"
    else:
        script_status = "WARNING: html2canvas script tag not found, jsPDF NOT added - add manually"
    with open('community.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("PATCHED: downloadCertificate rewritten. " + script_status)
