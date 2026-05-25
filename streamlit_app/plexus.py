PLEXUS_HTML = """
<script>
(function() {

  const parentWin = window.parent;
  const parentDoc = parentWin.document;

  if (parentWin.__plexusInitialized) return;
  parentWin.__plexusInitialized = true;

  let canvas = parentDoc.getElementById('plexus-canvas');
  if (!canvas) {
    canvas = parentDoc.createElement('canvas');
    canvas.id = 'plexus-canvas';
    canvas.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100dvh;z-index:-1;pointer-events:none;';
    parentDoc.body.appendChild(canvas);
  }
  const ctx = canvas.getContext('2d');

  // Offscreen canvas for the static nebula background
  const bgCanvas = parentDoc.createElement('canvas');
  const bgCtx = bgCanvas.getContext('2d');

  let W, H, nodes;
  let mouse = { x: -9999, y: -9999 };
  let clicked = false;

  function paintNebula() {
    bgCanvas.width = W;
    bgCanvas.height = H;
    const c = bgCtx;

    // Deep navy base
    const base = c.createLinearGradient(0, 0, W * 0.3, H);
    base.addColorStop(0,   '#0a0826');
    base.addColorStop(0.5, '#161347');
    base.addColorStop(1,   '#0d0a30');
    c.fillStyle = base;
    c.fillRect(0, 0, W, H);

    c.globalCompositeOperation = 'screen';

    // Purple glow, upper-right
    let g = c.createRadialGradient(W*0.72, H*0.25, 0, W*0.72, H*0.25, Math.max(W,H)*0.7);
    g.addColorStop(0,   'rgba(90, 50, 130, 0.55)');
    g.addColorStop(0.3, 'rgba(70, 40, 110, 0.35)');
    g.addColorStop(1,   'rgba(0,0,0,0)');
    c.fillStyle = g; c.fillRect(0, 0, W, H);

    // Amber glow, bottom-left
    g = c.createRadialGradient(W*0.18, H*0.85, 0, W*0.18, H*0.85, Math.max(W,H)*0.55);
    g.addColorStop(0,   'rgba(180, 110, 60, 0.45)');
    g.addColorStop(0.3, 'rgba(130, 80, 50, 0.25)');
    g.addColorStop(1,   'rgba(0,0,0,0)');
    c.fillStyle = g; c.fillRect(0, 0, W, H);

    // Amber hint, right
    g = c.createRadialGradient(W*1.05, H*0.55, 0, W*1.05, H*0.55, Math.max(W,H)*0.4);
    g.addColorStop(0, 'rgba(160, 100, 70, 0.35)');
    g.addColorStop(1, 'rgba(0,0,0,0)');
    c.fillStyle = g; c.fillRect(0, 0, W, H);

    // Cyan mist wave
    const wavePoints = [
      { x: 0.05, y: 0.55, r: 0.28, a: 0.28 },
      { x: 0.25, y: 0.62, r: 0.32, a: 0.32 },
      { x: 0.45, y: 0.58, r: 0.30, a: 0.30 },
      { x: 0.65, y: 0.65, r: 0.35, a: 0.35 },
      { x: 0.85, y: 0.60, r: 0.30, a: 0.28 },
      { x: 1.0,  y: 0.70, r: 0.30, a: 0.25 },
    ];
    for (const p of wavePoints) {
      g = c.createRadialGradient(W*p.x, H*p.y, 0, W*p.x, H*p.y, Math.max(W,H)*p.r);
      g.addColorStop(0,   `rgba(120, 160, 200, ${p.a})`);
      g.addColorStop(0.5, `rgba(80, 120, 170, ${p.a * 0.4})`);
      g.addColorStop(1,   'rgba(0,0,0,0)');
      c.fillStyle = g; c.fillRect(0, 0, W, H);
    }

    // Nebula noise — soft blurry circles
    for (let i = 0; i < 200; i++) {
      const x = Math.random() * W;
      const y = Math.random() * H;
      const r = 80 + Math.random() * 200;
      const hue = Math.random() < 0.5
        ? `rgba(100, 120, 180, ${0.02 + Math.random() * 0.04})`
        : `rgba(140, 110, 160, ${0.02 + Math.random() * 0.04})`;
      g = c.createRadialGradient(x, y, 0, x, y, r);
      g.addColorStop(0, hue);
      g.addColorStop(1, 'rgba(0,0,0,0)');
      c.fillStyle = g; c.fillRect(x - r, y - r, r * 2, r * 2);
    }

    // Golden dust particles
    c.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 120; i++) {
      const x = Math.random() * W;
      const y = Math.random() * H;
      const r = Math.random() * 1.2 + 0.2;
      const warm = Math.random() < 0.4;
      const a = 0.3 + Math.random() * 0.5;
      c.beginPath();
      c.arc(x, y, r, 0, Math.PI * 2);
      c.fillStyle = warm
        ? `rgba(220, 170, 110, ${a})`
        : `rgba(220, 220, 240, ${a * 0.7})`;
      c.fill();
    }

    // Vignette
    c.globalCompositeOperation = 'source-over';
    g = c.createRadialGradient(W/2, H/2, Math.min(W,H)*0.3, W/2, H/2, Math.max(W,H)*0.8);
    g.addColorStop(0, 'rgba(0,0,0,0)');
    g.addColorStop(1, 'rgba(0,0,20,0.5)');
    c.fillStyle = g; c.fillRect(0, 0, W, H);
  }

  function resize() {
    W = canvas.width = parentWin.innerWidth;
    H = canvas.height = parentWin.innerHeight;
    paintNebula();
  }

  function initNodes() {
    let count = 160;
    if (W < 480) {
      count = 50;
    } else if (W < 1024) {
      count = 100;
    }
    
    nodes = [];
    for (let i = 0; i < count; i++) {
      nodes.push({
        x: Math.random() * W,
        y: Math.random() * H,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        r: Math.random() * 2.0 + 0.8,
        expanded: false
      });
    }
    nodes.push({ x: W/2, y: H/2, vx: 0, vy: 0, r: 3, isPointer: true });
  }


  let last = 0;

  function draw(ts) {
      if (ts - last < 33) {
        parentWin.requestAnimationFrame(draw);
        return;
      }
      last = ts;
    // Paint pre-rendered nebula as background
    ctx.drawImage(bgCanvas, 0, 0);

    const ptr = nodes[nodes.length - 1];

    for (let i = 0; i < nodes.length - 1; i++) {
      const n = nodes[i];
      n.x += n.vx;
      n.y += n.vy;
      if (n.x < 0 || n.x > W) n.vx *= -1;
      if (n.y < 0 || n.y > H) n.vy *= -1;
    }

    ptr.x += (mouse.x - ptr.x) * 0.08;
    ptr.y += (mouse.y - ptr.y) * 0.08;

    const maxDist = 160;
    const maxDist2 = maxDist * maxDist;
    const clickRadius = 85;

    for (let i = 0; i < nodes.length - 1; i++) {
      for (let j = i + 1; j < nodes.length - 1; j += 2) {
        const a = nodes[i], b = nodes[j];
        const dx = a.x - b.x, dy = a.y - b.y;
        const dist2 = dx*dx + dy*dy;
        const dist = Math.sqrt(dist2);
        if (dist2 < maxDist2) {
          const alpha = (1 - dist / maxDist) * 0.7;
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.strokeStyle = `rgba(170,170,255,${alpha})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }

    const pointerReach = 140;
    for (let i = 0; i < nodes.length - 1; i++) {
      const n = nodes[i];
      const dx = n.x - ptr.x, dy = n.y - ptr.y;
      const dist2 = dx*dx + dy*dy;
      const dist = Math.sqrt(dist2);
      if (dist2 < pointerReach * pointerReach) {
        const alpha = (1 - dist / pointerReach) * 0.65;
        ctx.beginPath();
        ctx.moveTo(n.x, n.y);
        ctx.lineTo(ptr.x, ptr.y);
        ctx.strokeStyle = `rgba(220,210,255,${alpha})`;
        ctx.lineWidth = 0.8;
        ctx.stroke();
        n.expanded = clicked && dist < clickRadius;
      } else {
        n.expanded = false;
      }
    }

    for (let i = 0; i < nodes.length - 1; i++) {
      const n = nodes[i];
      const r = n.expanded ? n.r * 5.5 : n.r;
      ctx.beginPath();
      ctx.arc(n.x, n.y, r, 0, Math.PI * 2);
      ctx.fillStyle = n.expanded
        ? 'rgba(210,200,255,0.95)'
        : 'rgba(200,200,255,0.7)';
      ctx.fill();
    }

    ctx.beginPath();
    ctx.arc(ptr.x, ptr.y, 3.5, 0, Math.PI * 2);
    ctx.fillStyle = '#ffffff';
    ctx.fill();

    parentWin.requestAnimationFrame(draw);

  }

  parentWin.addEventListener('mousemove', e => { mouse.x = e.clientX; mouse.y = e.clientY; });
  parentWin.addEventListener('mousedown', () => { clicked = true; });
  parentWin.addEventListener('mouseup',   () => { clicked = false; });
  parentWin.addEventListener('resize', () => { resize(); initNodes(); });

  resize();
  initNodes();
  draw();
})();
</script>
"""
