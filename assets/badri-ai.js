/* =====================================================================
   BADRI'S AI — floating chat widget
   ---------------------------------------------------------------------
   Streams answers from the Cloud Run endpoint set in this script tag's
   data-endpoint attribute (see server/README.md). On localhost it talks
   to the local server on :8080. With no endpoint it renders nothing.
   Model output is never inserted as HTML: see renderRich().
   ===================================================================== */
(function () {
  'use strict';

  var script = document.currentScript;
  var isLocal = /^(localhost|127\.0\.0\.1)$/.test(location.hostname);
  var ENDPOINT = isLocal ? 'http://localhost:8080' : ((script && script.dataset.endpoint) || '').trim();
  if (!ENDPOINT || !window.fetch || !window.TextDecoderStream) return;

  var EMAIL = 'badriathindran@gmail.com';
  var MAX_HISTORY = 16;
  var MAX_CHARS = 1000;
  var WAKE_LIMIT_MS = 60000;   // keep retrying a failed connection this long (Cloud Run cold start)
  var RETRY_DELAY_MS = 3000;
  var WAKE_AFTER_MS = 5 * 60 * 1000;   // skip the wake-up ping if we reached the service this recently
  var CUT_OFF = 'The answer was cut off. Please try again.';
  var WAKING = 'Waking up — the first answer can take up to a minute…';
  var GREETING = "Hi, I'm Badri's AI 👋 Ask me about my experience, projects, skills, or education.";
  var SUGGESTIONS = [
    'What are you working on now?',
    'Tell me about PolicyPal',
    "What's your GenAI experience?",
    'How can I contact you?'
  ];
  var ALLOWED_PROTOCOLS = ['https:', 'mailto:', 'tel:'];
  // **bold** | [text](url) | https://url | email | +phone
  var TOKEN = /\*\*([^*\n]+)\*\*|\[([^\]\n]+)\]\(([^)\s]+)\)|(https:\/\/[^\s<>()]*[^\s<>().,;:!?'"])|([\w.+-]+@[\w-]+(?:\.[\w-]+)+)|(\+\d[\d ().-]{7,}\d)/g;
  var mobile = window.matchMedia('(max-width:560px)');
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  var ICONS = {
    star: '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2l2.6 6.3L21 9l-4.8 4.3L17.6 21 12 17.3 6.4 21l1.4-7.7L3 9l6.4-.7z"/></svg>',
    close: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>',
    send: '<svg class="bai-icon-send" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    stop: '<svg class="bai-icon-stop" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="6" y="6" width="12" height="12" rx="2"/></svg>'
  };

  var history = [];        // [{ role, content }] sent to the server
  var controller = null;   // AbortController while a reply streams
  var frame = 0, pending = null;
  var lastContact = 0;     // when we last reached (or tried to reach) the service
  var ui = buildUI();

  // A cold start takes ~40 s, so wake the service when a visitor arrives, returns to the tab
  // or opens the chat. No timers: an idle or hidden tab never keeps the service awake.
  wake();
  document.addEventListener('visibilitychange', function () {
    if (!document.hidden) wake();
  });

  /* =================================================================
     1) DOM
     ================================================================= */
  function h(tag, attrs, children) {
    var node = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === 'html') node.innerHTML = attrs[k];          // static icons only, never model output
      else if (k === 'text') node.textContent = attrs[k];
      else node.setAttribute(k, attrs[k]);
    });
    (children || []).forEach(function (c) { node.appendChild(c); });
    return node;
  }

  function buildUI() {
    var launcher = h('button', { type: 'button', 'class': 'bai-launcher', 'aria-expanded': 'false',
      'aria-controls': 'bai-panel', 'aria-label': "Chat with Badri's AI", html: ICONS.star });
    var close = h('button', { type: 'button', 'class': 'bai-close', 'aria-label': 'Close chat', html: ICONS.close });
    var log = h('div', { 'class': 'bai-log', role: 'log', 'aria-live': 'off', 'aria-label': 'Conversation' });
    var chips = h('div', { 'class': 'bai-chips' }, SUGGESTIONS.map(function (q) {
      return h('button', { type: 'button', 'class': 'bai-chip', text: q });
    }));
    var input = h('textarea', { id: 'bai-input', 'class': 'bai-input', rows: '1', maxlength: String(MAX_CHARS),
      placeholder: 'Ask about my work…', 'data-interactive': '' });
    var send = h('button', { type: 'submit', 'class': 'bai-send', 'aria-label': 'Send', html: ICONS.send + ICONS.stop });
    var form = h('form', { 'class': 'bai-form' }, [
      h('label', { 'class': 'bai-sr', 'for': 'bai-input', text: "Ask Badri's AI a question" }), input, send
    ]);
    var status = h('div', { 'class': 'bai-sr', 'aria-live': 'polite' });
    var panel = h('section', { id: 'bai-panel', 'class': 'bai-panel', role: 'dialog', 'aria-modal': 'false',
      'aria-labelledby': 'bai-title', tabindex: '-1', hidden: '' }, [
      h('header', { 'class': 'bai-head' }, [
        h('span', { 'class': 'bai-head__dot', 'aria-hidden': 'true' }),
        h('div', { 'class': 'bai-head__text' }, [
          h('h2', { id: 'bai-title', text: "Badri's AI" }),
          h('p', { text: 'AI version of Badri · may make mistakes · email for anything important' })
        ]),
        close
      ]),
      log, chips, form, status
    ]);

    document.body.appendChild(launcher);
    document.body.appendChild(panel);
    addMessage('assistant', GREETING, log);

    launcher.addEventListener('click', function () { panel.hidden ? open() : closePanel(); });
    close.addEventListener('click', closePanel);
    chips.addEventListener('click', function (e) {
      if (e.target.classList.contains('bai-chip')) ask(e.target.textContent);
    });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (controller) controller.abort();
      else ask(input.value);
    });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) { e.preventDefault(); form.requestSubmit(); }
    });
    input.addEventListener('input', autoGrow);
    panel.addEventListener('keydown', onPanelKeydown);

    return { launcher: launcher, panel: panel, log: log, chips: chips, input: input, send: send, status: status };
  }

  /* =================================================================
     2) OPEN / CLOSE / KEYBOARD
     ================================================================= */
  function open() {
    var modal = mobile.matches;
    ui.panel.hidden = false;
    ui.panel.setAttribute('aria-modal', modal ? 'true' : 'false');
    ui.launcher.setAttribute('aria-expanded', 'true');
    document.documentElement.classList.toggle('bai-locked', modal);
    if (modal) fitViewport();
    (ui.input.disabled ? ui.panel : ui.input).focus();
    wake();
  }

  function wake() {
    if (Date.now() - lastContact < WAKE_AFTER_MS) return;
    lastContact = Date.now();
    fetch(ENDPOINT, { method: 'GET' }).catch(function () {});
  }

  function closePanel() {
    ui.panel.hidden = true;
    ui.launcher.setAttribute('aria-expanded', 'false');
    document.documentElement.classList.remove('bai-locked');
    ui.launcher.focus();
  }

  function onPanelKeydown(e) {
    if (e.key === 'Escape') { e.preventDefault(); closePanel(); return; }
    if (e.key !== 'Tab' || ui.panel.getAttribute('aria-modal') !== 'true') return;
    // mobile sheet is modal: keep focus inside it
    var focusable = ui.panel.querySelectorAll('button:not([disabled]), textarea:not([disabled]), a[href]');
    var first = focusable[0], last = focusable[focusable.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  }

  // keep the mobile sheet above the on-screen keyboard
  function fitViewport() {
    if (window.visualViewport) ui.panel.style.setProperty('--bai-vh', window.visualViewport.height + 'px');
  }
  if (window.visualViewport) window.visualViewport.addEventListener('resize', fitViewport);

  function autoGrow() {
    ui.input.style.height = 'auto';
    ui.input.style.height = ui.input.scrollHeight + 'px';
  }

  /* =================================================================
     3) CONVERSATION
     ================================================================= */
  function ask(text) {
    text = text.trim();
    if (!text || controller) return;

    ui.chips.hidden = true;
    ui.input.value = '';
    autoGrow();
    history.push({ role: 'user', content: text });
    addMessage('user', text);

    var bubble = addMessage('assistant', '');
    var answer = '';
    bubble.setAttribute('aria-busy', 'true');
    announce("Badri's AI is replying…");
    setBusy(true);

    streamChat(history.slice(-MAX_HISTORY), controller.signal, function (delta) {
      answer += delta;
      scheduleRender(bubble, answer);
    }, function () {
      renderNow(bubble, '', WAKING);
    }).then(function (finish) {
      history.push({ role: 'assistant', content: answer });
      renderNow(bubble, answer, finish === 'length' ? '(answer trimmed for length)' : '');
      announce(bubble.textContent);
    }).catch(function (err) {
      if (err.name === 'AbortError') {
        renderNow(bubble, answer, '(stopped)');
        announce('Stopped.');
      } else {
        renderNow(bubble, err.message || connectionError());
        bubble.classList.add('bai-msg--error');
        announce(bubble.textContent);
      }
    }).then(function () {
      bubble.removeAttribute('aria-busy');
      setBusy(false);
    });
  }

  // The input is disabled while a reply is busy, so park keyboard focus on the panel (typing
  // and Space do nothing there; Escape still closes it) and hand it back to the input after.
  function setBusy(busy) {
    var active = document.activeElement;
    var refocus = busy ? (ui.panel.contains(active) || active === document.body)  // body: a clicked chip was hidden
                       : (active === ui.panel || active === ui.send);
    controller = busy ? new AbortController() : null;
    ui.input.disabled = busy;
    ui.send.classList.toggle('is-busy', busy);
    ui.send.setAttribute('aria-label', busy ? 'Stop' : 'Send');
    if (refocus) (busy ? ui.panel : ui.input).focus();
  }

  function announce(text) { ui.status.textContent = text; }

  function connectionError() {
    return "I'm having trouble connecting — you can email me at " + EMAIL + '.';
  }

  /* =================================================================
     4) STREAMING  (POST → server-sent events via fetch)
     ================================================================= */
  function streamChat(messages, signal, onDelta, onWaking) {
    return connect(messages, signal, Date.now() + WAKE_LIMIT_MS, onWaking).then(function (res) {
      if (res.ok) return readEvents(res.body, onDelta);
      return res.json().catch(function () { return null; }).then(function (body) {
        var message = (body && body.error && body.error.message) || connectionError();
        var retry = res.headers.get('Retry-After');
        if (res.status === 429 && retry) message += ' Please try again in ' + retry + ' s.';
        throw new Error(message);
      });
    });
  }

  // A cold start makes Cloud Run reject requests without CORS headers, so fetch fails
  // outright; retry until the instance is up. Our own errors arrive as responses instead.
  function connect(messages, signal, deadline, onWaking) {
    lastContact = Date.now();
    return fetch(ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: messages }),
      signal: signal
    }).catch(function (err) {
      if (err.name === 'AbortError') throw err;
      if (Date.now() + RETRY_DELAY_MS > deadline) throw new Error(connectionError());
      if (onWaking) { onWaking(); onWaking = null; }
      return wait(RETRY_DELAY_MS, signal).then(function () {
        return connect(messages, signal, deadline, null);
      });
    });
  }

  function wait(ms, signal) {
    return new Promise(function (resolve, reject) {
      var timer = setTimeout(resolve, ms);
      signal.addEventListener('abort', function () {
        clearTimeout(timer);
        reject(new DOMException('Aborted', 'AbortError'));
      }, { once: true });
    });
  }

  function readEvents(body, onDelta) {
    var reader = body.pipeThrough(new TextDecoderStream()).getReader();
    var buffer = '';
    function pump() {
      return reader.read().catch(function (err) {
        throw err.name === 'AbortError' ? err : new Error(CUT_OFF);  // e.g. "network error"
      }).then(function (chunk) {
        if (chunk.done) throw new Error(CUT_OFF);
        buffer += chunk.value;
        var end;
        while ((end = buffer.indexOf('\n\n')) !== -1) {
          var ev = parseFrame(buffer.slice(0, end));
          buffer = buffer.slice(end + 2);
          if (!ev) continue;
          if (ev.event === 'delta') onDelta(ev.data.t || '');
          else if (ev.event === 'done') { reader.cancel(); return ev.data.finish; }
          else if (ev.event === 'error') throw new Error(ev.data.message || connectionError());
        }
        return pump();
      });
    }
    return pump();
  }

  function parseFrame(frameText) {
    var event = 'message', data = null;
    frameText.split('\n').forEach(function (line) {
      if (line.indexOf('event: ') === 0) event = line.slice(7);
      else if (line.indexOf('data: ') === 0) data = line.slice(6);
    });
    if (data === null) return null;  // ": ok" comment / keep-alive
    try { return { event: event, data: JSON.parse(data) }; } catch (e) { return null; }
  }

  /* =================================================================
     5) RENDERING  (text nodes only; links limited to https/mailto/tel)
     ================================================================= */
  function addMessage(role, text, log) {
    log = log || ui.log;
    var bubble = h('div', { 'class': 'bai-msg bai-msg--' + role });
    renderRich(bubble, text);
    var stick = nearBottom(log);
    log.appendChild(bubble);
    if (stick || role === 'user') scrollToBottom(log, !reduceMotion.matches);
    return bubble;
  }

  function scheduleRender(bubble, text) {
    pending = { bubble: bubble, text: text };
    if (frame) return;
    frame = requestAnimationFrame(function () {
      frame = 0;
      var stick = nearBottom(ui.log);
      renderRich(pending.bubble, pending.text);
      if (stick) scrollToBottom(ui.log, false);
    });
  }

  function renderNow(bubble, text, note) {
    if (frame) { cancelAnimationFrame(frame); frame = 0; }
    var stick = nearBottom(ui.log);
    renderRich(bubble, text);
    if (note) bubble.appendChild(h('span', { 'class': 'bai-msg__note', text: (/\S$/.test(text) ? ' ' : '') + note }));
    if (stick) scrollToBottom(ui.log, false);
  }

  function renderRich(node, text) {
    node.textContent = '';
    var last = 0, m;
    TOKEN.lastIndex = 0;
    while ((m = TOKEN.exec(text))) {
      if (m.index > last) node.appendChild(document.createTextNode(text.slice(last, m.index)));
      node.appendChild(tokenNode(m));
      last = TOKEN.lastIndex;
    }
    if (last < text.length) node.appendChild(document.createTextNode(text.slice(last)));
  }

  function tokenNode(m) {
    if (m[1]) return h('strong', { text: m[1] });
    if (m[2]) return link(m[2], m[3]);
    if (m[4]) return link(m[4], m[4]);
    if (m[5]) return link(m[5], 'mailto:' + m[5]);
    return link(m[6], 'tel:' + m[6].replace(/[^\d+]/g, ''));
  }

  function link(label, url) {
    var href = safeHref(url);
    if (!href) return document.createTextNode(label);
    if (href.indexOf('https:') !== 0) return h('a', { href: href, text: label });  // mailto:/tel: open their app
    return h('a', { href: href, target: '_blank', rel: 'noopener noreferrer', text: label });
  }

  function safeHref(url) {
    try {
      var parsed = new URL(url);
      return ALLOWED_PROTOCOLS.indexOf(parsed.protocol) !== -1 ? parsed.href : null;
    } catch (e) { return null; }
  }

  function nearBottom(log) {
    return log.scrollHeight - log.scrollTop - log.clientHeight < 80;
  }

  function scrollToBottom(log, smooth) {
    log.scrollTo({ top: log.scrollHeight, behavior: smooth ? 'smooth' : 'auto' });
  }
})();
