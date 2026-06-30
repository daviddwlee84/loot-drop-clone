(function () {
  'use strict';

  var DISCLAIMER_TEXT =
    'This entry is an AI-assisted summary and analysis derived from publicly available sources only ' +
    '(news, founder statements, funding data, etc.). It represents patterns, opinions, and interpretations ' +
    'for educational purposes\u2014not verified facts, accusations, or professional advice. AI can contain errors ' +
    'or \u2018hallucinations\u2019; all content is human-reviewed but provided \u2018as is\u2019 with no warranties of accuracy, ' +
    'completeness, or reliability. We disclaim all liability for reliance on or use of this information.';

  var CONTACT_INTRO =
    'If you are a representative of this company and believe any information is inaccurate or wish to request a correction, please submit the form below.';

  var style = document.createElement('style');
  style.textContent = [
    '.dc-btn{display:inline-block;background:#000;color:#fff;border:2px solid #000;' +
      'padding:5px 14px;font-family:"Space Grotesk",sans-serif;font-size:10px;font-weight:700;letter-spacing:1.5px;' +
      'cursor:pointer;text-transform:uppercase;box-shadow:3px 3px 0 #000;transition:transform .15s,box-shadow .15s;}',
    '.dc-btn:hover{transform:translate(-1px,-1px);box-shadow:4px 4px 0 #000;}',

    '.dc-overlay{display:none;position:fixed;inset:0;z-index:10000;background:rgba(0,0,0,.55);' +
      'align-items:center;justify-content:center;padding:20px;}',
    '.dc-overlay.active{display:flex;}',

    '.dc-modal{background:#fff;border:4px solid #000;box-shadow:8px 8px 0 #000;max-width:560px;width:100%;' +
      'max-height:90vh;overflow-y:auto;font-family:"Space Grotesk",sans-serif;position:relative;}',

    '.dc-modal-header{background:#000;color:#fff;padding:14px 20px;display:flex;align-items:center;justify-content:space-between;}',
    '.dc-modal-header h3{margin:0;font-size:14px;letter-spacing:2px;text-transform:uppercase;}',
    '.dc-close{background:none;border:none;color:#fff;font-size:22px;cursor:pointer;padding:0 4px;line-height:1;}',

    '.dc-body{padding:20px 24px 24px;}',
    '.dc-body p{margin:0 0 16px;font-size:13px;line-height:1.7;color:#333;}',
    '.dc-body p:last-child{margin-bottom:0;}',

    '.dc-divider{border:none;border-top:2px dashed #ddd;margin:20px 0;}',

    '.dc-form{display:flex;flex-direction:column;gap:10px;}',
    '.dc-form label{font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#000;}',
    '.dc-form input,.dc-form textarea{border:3px solid #000;padding:10px 12px;font-family:"Space Grotesk",sans-serif;' +
      'font-size:13px;outline:none;transition:border-color .2s;}',
    '.dc-form input:focus,.dc-form textarea:focus{border-color:#F4C430;}',
    '.dc-form textarea{resize:vertical;min-height:80px;}',
    '.dc-submit{background:#000;color:#fff;border:none;padding:12px 20px;font-family:"Space Grotesk",sans-serif;' +
      'font-size:12px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;cursor:pointer;' +
      'box-shadow:4px 4px 0 #000;transition:transform .15s,box-shadow .15s,background .15s;}',
    '.dc-submit:hover{transform:translate(-2px,-2px);box-shadow:6px 6px 0 #000;}',
    '.dc-submit:disabled{opacity:.5;cursor:not-allowed;transform:none;box-shadow:4px 4px 0 #000;}',
    '.dc-success{background:#065F46;color:#fff;padding:12px 16px;font-size:13px;font-weight:600;text-align:center;border:2px solid #000;}',
    '.dc-error{background:#B91C1C;color:#fff;padding:12px 16px;font-size:13px;font-weight:600;text-align:center;border:2px solid #000;}'
  ].join('\n');
  document.head.appendChild(style);

  var overlay = document.createElement('div');
  overlay.className = 'dc-overlay';
  overlay.innerHTML =
    '<div class="dc-modal">' +
      '<div class="dc-modal-header">' +
        '<h3>Disclaimer</h3>' +
        '<button class="dc-close" type="button">&times;</button>' +
      '</div>' +
      '<div class="dc-body">' +
        '<p>' + DISCLAIMER_TEXT + '</p>' +
        '<hr class="dc-divider">' +
        '<p>' + CONTACT_INTRO + '</p>' +
        '<form class="dc-form" id="dc-contact-form">' +
          '<label for="dc-name">Your Name / Company</label>' +
          '<input type="text" id="dc-name" name="name" required placeholder="e.g. Jane Doe, Acme Corp">' +
          '<label for="dc-email">Email Address</label>' +
          '<input type="email" id="dc-email" name="email" required placeholder="you@company.com">' +
          '<label for="dc-page">Page URL (auto-filled)</label>' +
          '<input type="text" id="dc-page" name="page_url" readonly>' +
          '<label for="dc-message">Message</label>' +
          '<textarea id="dc-message" name="message" required placeholder="Describe the inaccuracy or correction request\u2026"></textarea>' +
          '<button type="submit" class="dc-submit">Submit Request</button>' +
          '<div id="dc-form-status"></div>' +
        '</form>' +
      '</div>' +
    '</div>';
  document.body.appendChild(overlay);

  function openModal() {
    document.getElementById('dc-page').value = window.location.href;
    overlay.classList.add('active');
  }

  document.querySelectorAll('.dc-btn').forEach(function (el) {
    el.addEventListener('click', openModal);
  });

  overlay.querySelector('.dc-close').addEventListener('click', function () {
    overlay.classList.remove('active');
  });
  overlay.addEventListener('click', function (e) {
    if (e.target === overlay) overlay.classList.remove('active');
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') overlay.classList.remove('active');
  });

  var form = document.getElementById('dc-contact-form');
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var submitBtn = form.querySelector('.dc-submit');
    var status = document.getElementById('dc-form-status');
    status.innerHTML = '';
    submitBtn.disabled = true;
    submitBtn.textContent = 'Sending\u2026';

    var payload = {
      name: document.getElementById('dc-name').value.trim(),
      email: document.getElementById('dc-email').value.trim(),
      page_url: document.getElementById('dc-page').value,
      message: document.getElementById('dc-message').value.trim()
    };

    fetch('/api/contact', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(function (res) {
        if (!res.ok) throw new Error('Server error');
        return res.json();
      })
      .then(function () {
        status.innerHTML = '<div class="dc-success">Thank you! Your request has been submitted.</div>';
        form.reset();
        document.getElementById('dc-page').value = window.location.href;
      })
      .catch(function () {
        status.innerHTML = '<div class="dc-error">Something went wrong. Please try again.</div>';
      })
      .finally(function () {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit Request';
      });
  });
})();
