(function () {
  var lb = document.getElementById('lightbox');
  if (!lb) return;
  var stage = lb.querySelector('.lightbox-stage');
  var img = document.getElementById('lightbox-img');
  var hint = lb.querySelector('.lightbox-hint');
  var closeBtn = lb.querySelector('.lightbox-close');

  var MIN = 1, MAX = 6;
  var scale = 1, tx = 0, ty = 0;
  var pointers = new Map();
  var pinch = null, pan = null, moved = false, lastTap = 0, hintTimer = 0;

  function apply() {
    img.style.transform = 'translate(' + tx + 'px,' + ty + 'px) scale(' + scale + ')';
    lb.classList.toggle('zoomed', scale > 1.01);
  }
  function clamp() {
    var r = stage.getBoundingClientRect();
    var w = img.offsetWidth * scale, h = img.offsetHeight * scale;
    var maxX = Math.max(0, (w - r.width) / 2 + 40);
    var maxY = Math.max(0, (h - r.height) / 2 + 40);
    tx = Math.min(maxX, Math.max(-maxX, tx));
    ty = Math.min(maxY, Math.max(-maxY, ty));
  }
  function zoomAt(cx, cy, factor) {
    var r = img.getBoundingClientRect();
    var ox = cx - (r.left + r.width / 2), oy = cy - (r.top + r.height / 2);
    var ns = Math.min(MAX, Math.max(MIN, scale * factor));
    var k = ns / scale;
    tx += ox * (1 - k); ty += oy * (1 - k); scale = ns;
    if (scale === 1) { tx = 0; ty = 0; }
    clamp(); apply();
  }
  function reset() { scale = 1; tx = 0; ty = 0; apply(); }

  function open(src, alt) {
    img.src = src; img.alt = alt || '';
    reset();
    lb.classList.add('show');
    document.body.style.overflow = 'hidden';
    hint.classList.add('show');
    clearTimeout(hintTimer);
    hintTimer = setTimeout(function () { hint.classList.remove('show'); }, 2200);
  }
  function close() {
    lb.classList.remove('show');
    document.body.style.overflow = '';
    img.removeAttribute('src');
  }

  document.querySelectorAll('.step-img, .ref-grid figure img').forEach(function (el) {
    el.addEventListener('click', function (e) {
      e.preventDefault();
      open(el.currentSrc || el.src, el.alt);
    });
  });
  closeBtn.addEventListener('click', function (e) { e.stopPropagation(); close(); });

  function dist(a, b) { var dx = a.x - b.x, dy = a.y - b.y; return Math.hypot(dx, dy); }
  function mid(a, b) { return { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 }; }

  stage.addEventListener('pointerdown', function (e) {
    stage.setPointerCapture(e.pointerId);
    pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
    moved = false;
    if (pointers.size === 2) {
      var p = Array.from(pointers.values());
      pinch = { d: dist(p[0], p[1]), c: mid(p[0], p[1]) };
      pan = null;
    } else if (pointers.size === 1) {
      pan = { x: e.clientX, y: e.clientY, tx: tx, ty: ty };
    }
  });
  stage.addEventListener('pointermove', function (e) {
    if (!pointers.has(e.pointerId)) return;
    pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (pointers.size === 2 && pinch) {
      var p = Array.from(pointers.values());
      var d = dist(p[0], p[1]), c = mid(p[0], p[1]);
      if (d > 0 && pinch.d > 0) zoomAt(c.x, c.y, d / pinch.d);
      tx += c.x - pinch.c.x; ty += c.y - pinch.c.y; clamp(); apply();
      pinch = { d: d, c: c };
      moved = true;
    } else if (pointers.size === 1 && pan && scale > 1) {
      var nx = pan.tx + (e.clientX - pan.x), ny = pan.ty + (e.clientY - pan.y);
      if (Math.abs(e.clientX - pan.x) > 3 || Math.abs(e.clientY - pan.y) > 3) moved = true;
      tx = nx; ty = ny; clamp(); apply();
    }
  });
  function up(e) {
    if (!pointers.has(e.pointerId)) return;
    pointers.delete(e.pointerId);
    if (pointers.size < 2) pinch = null;
    if (pointers.size === 1) {
      var p = Array.from(pointers.values())[0];
      pan = { x: p.x, y: p.y, tx: tx, ty: ty };
      return;
    }
    if (pointers.size === 0 && !moved && e.type === 'pointerup') {
      var now = Date.now();
      var onImg = e.target === img;
      if (now - lastTap < 320 && onImg) {
        lastTap = 0;
        if (scale > 1.01) reset(); else zoomAt(e.clientX, e.clientY, 2.5);
        return;
      }
      lastTap = now;
      if (!onImg) close();
    }
  }
  stage.addEventListener('pointerup', up);
  stage.addEventListener('pointercancel', up);
  stage.addEventListener('wheel', function (e) {
    e.preventDefault();
    zoomAt(e.clientX, e.clientY, e.deltaY < 0 ? 1.15 : 1 / 1.15);
  }, { passive: false });

  document.addEventListener('keydown', function (e) {
    if (!lb.classList.contains('show')) return;
    if (e.key === 'Escape') close();
    else if (e.key === '+' || e.key === '=') zoomAt(innerWidth / 2, innerHeight / 2, 1.25);
    else if (e.key === '-') zoomAt(innerWidth / 2, innerHeight / 2, 0.8);
    else if (e.key === '0') reset();
  });
})();
