/* Evil Encryption Academy — shared helpers.
   Real cryptography via the Web Crypto API. Keys are fixed and printed; nothing here is secret. */

/* ---------------- crypto helpers ---------------- */
const hex   = b => [...new Uint8Array(b)].map(x => x.toString(16).padStart(2,'0')).join('');
const bytes = s => new TextEncoder().encode(s);
const text  = b => new TextDecoder().decode(b);

async function aesKey(raw){
  return crypto.subtle.importKey('raw', raw, {name:'AES-CBC'}, false, ['encrypt','decrypt']);
}
async function demoKeyBytes(seed='evil-encryption-academy'){
  return new Uint8Array(await crypto.subtle.digest('SHA-256', bytes(seed)));
}
async function aesCBC(data, keyRaw, ivRaw){
  const k = await aesKey(keyRaw);
  return new Uint8Array(await crypto.subtle.encrypt(
    {name:'AES-CBC', iv: ivRaw || new Uint8Array(16)}, k, data));
}
/* Web Crypto deliberately omits ECB. Encrypting each 16-byte block under a zero IV is
   mathematically identical, so the demo shows the real failure rather than a mock-up. */
async function aesECB(data, keyRaw){
  const k = await aesKey(keyRaw), zero = new Uint8Array(16);
  const out = new Uint8Array(data.length);
  for(let i=0;i<data.length;i+=16){
    const enc = new Uint8Array(await crypto.subtle.encrypt(
      {name:'AES-CBC', iv:zero}, k, data.slice(i,i+16)));
    out.set(enc.slice(0,16), i);
  }
  return out;
}
function shannon(u8){
  if(!u8.length) return 0;
  const c = new Array(256).fill(0);
  for(const b of u8) c[b]++;
  let h = 0;
  for(const n of c){ if(n){ const p = n/u8.length; h -= p*Math.log2(p); } }
  return h;
}
function distinctBlocks(u8, size=16){
  const s = new Set();
  for(let i=0;i+size<=u8.length;i+=size) s.add(hex(u8.slice(i,i+size)));
  return s.size;
}
function hexdump(u8, limit=64){
  let o='';
  for(let i=0;i<Math.min(u8.length,limit);i+=16){
    const c=[...u8.slice(i,i+16)];
    o+=c.map(b=>b.toString(16).padStart(2,'0')).join(' ').padEnd(47)+'  |'+
       c.map(b=>b>=32&&b<127?String.fromCharCode(b):'.').join('')+'|\n';
  }
  return o.trimEnd();
}
function histogram(u8, buckets=32, height=5){
  const c=new Array(buckets).fill(0), span=256/buckets;
  for(const b of u8) c[Math.floor(b/span)]++;
  const peak=Math.max(...c)||1; const rows=[];
  for(let l=height;l>0;l--) rows.push('|'+c.map(v=>(v/peak*height>=l?'█':' ')).join('')+'|');
  rows.push('+'+'-'.repeat(buckets)+'+');
  return rows.join('\n');
}
/* Announce a simulation result to assistive tech without cluttering the visual layout. */
function describe(id, msg){
  const el = document.getElementById(id);
  if(el) el.textContent = msg;
}
function busy(el, on){ if(el) el.classList.toggle('busy', !!on); }

/* ---------------- theme ---------------- */
const THEME_KEY = 'eea-theme';
function applyTheme(t){
  if(t === 'system'){ document.documentElement.removeAttribute('data-theme'); }
  else { document.documentElement.setAttribute('data-theme', t); }
  const b = document.querySelector('.theme-btn');
  if(b){
    const label = t === 'system' ? 'System' : (t === 'dark' ? 'Dark' : 'Light');
    b.textContent = label + ' theme';
    b.setAttribute('aria-label', 'Colour theme: ' + label + '. Activate to change.');
  }
  document.dispatchEvent(new CustomEvent('themechange'));
}
function currentTheme(){
  try { return localStorage.getItem(THEME_KEY) || 'system'; } catch(e){ return 'system'; }
}
function isDark(){
  const t = currentTheme();
  if(t === 'dark') return true;
  if(t === 'light') return false;
  return window.matchMedia('(prefers-color-scheme: dark)').matches;
}

/* ---------------- progress ---------------- */
const PROG_KEY = 'eea-progress';
const PAGES = ['01','02','03','04','05','06','07','08','09','10','11'];
function readProgress(){
  try { return JSON.parse(localStorage.getItem(PROG_KEY) || '[]'); } catch(e){ return []; }
}
function writeProgress(list){
  try { localStorage.setItem(PROG_KEY, JSON.stringify(list)); } catch(e){}
}
function markDone(pid, done){
  let p = readProgress();
  p = done ? [...new Set([...p, pid])] : p.filter(x => x !== pid);
  writeProgress(p);
  paintProgress();
}
function paintProgress(){
  const done = readProgress().filter(p => PAGES.includes(p));
  const pct = Math.round(done.length / PAGES.length * 100);
  const fill = document.querySelector('.prog-fill');
  const txt  = document.querySelector('.prog-count');
  const bar  = document.querySelector('.prog-bar');
  if(fill) fill.style.width = pct + '%';
  if(txt)  txt.textContent = done.length + ' of ' + PAGES.length + ' read';
  if(bar){
    bar.setAttribute('role','progressbar');
    bar.setAttribute('aria-valuenow', String(pct));
    bar.setAttribute('aria-valuemin','0');
    bar.setAttribute('aria-valuemax','100');
    bar.setAttribute('aria-label','Course progress: ' + done.length + ' of ' + PAGES.length + ' modules read');
  }
  document.querySelectorAll('.side nav a[data-p]').forEach(a => {
    const d = done.includes(a.dataset.p);
    a.classList.toggle('done', d);
    const i = a.querySelector('i');
    if(i && PAGES.includes(a.dataset.p)) i.textContent = d ? '✓' : a.dataset.p;
  });
  const db = document.querySelector('.done-bar');
  if(db){
    const pid = db.dataset.p, d = done.includes(pid);
    db.classList.toggle('is-done', d);
    db.querySelector('p').textContent = d
      ? 'Marked as read. It will stay ticked when you come back.'
      : 'Finished this module?';
    const b = db.querySelector('button');
    b.textContent = d ? 'Mark unread' : 'Mark as read';
    b.setAttribute('aria-pressed', String(d));
  }
}

/* ---------------- wiring ---------------- */
document.addEventListener('DOMContentLoaded', () => {
  applyTheme(currentTheme());

  const mb = document.querySelector('.menu-btn'), sd = document.querySelector('.side');
  if(mb && sd){
    mb.setAttribute('aria-expanded','false');
    mb.addEventListener('click', () => {
      const open = sd.classList.toggle('open');
      mb.setAttribute('aria-expanded', String(open));
    });
  }

  const tb = document.querySelector('.theme-btn');
  if(tb) tb.addEventListener('click', () => {
    const order = ['system','light','dark'];
    const next = order[(order.indexOf(currentTheme()) + 1) % order.length];
    try { localStorage.setItem(THEME_KEY, next); } catch(e){}
    applyTheme(next);
  });

  const db = document.querySelector('.done-bar');
  if(db) db.querySelector('button').addEventListener('click', () => {
    markDone(db.dataset.p, !readProgress().includes(db.dataset.p));
  });

  const rb = document.querySelector('.prog-reset');
  if(rb) rb.addEventListener('click', () => { writeProgress([]); paintProgress(); });

  /* copy buttons on every output block */
  document.querySelectorAll('.out').forEach(o => {
    const b = document.createElement('button');
    b.className = 'copy'; b.type = 'button'; b.textContent = 'Copy';
    b.setAttribute('aria-label','Copy this output to the clipboard');
    b.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(o.textContent.replace(/^Copy/, '').trim());
        b.textContent = 'Copied'; setTimeout(() => b.textContent = 'Copy', 1400);
      } catch(e){ b.textContent = 'Failed'; setTimeout(() => b.textContent = 'Copy', 1400); }
    });
    o.appendChild(b);
  });

  /* arrow-key paging, but never while typing */
  document.addEventListener('keydown', e => {
    if(e.metaKey || e.ctrlKey || e.altKey) return;
    const t = e.target.tagName;
    if(t === 'INPUT' || t === 'TEXTAREA' || t === 'SELECT' || e.target.isContentEditable) return;
    const sel = e.key === 'ArrowLeft' ? '.pager a:not(.nxt)'
              : e.key === 'ArrowRight' ? '.pager a.nxt' : null;
    if(!sel) return;
    const link = document.querySelector(sel);
    if(link) { e.preventDefault(); window.location.href = link.getAttribute('href'); }
  });

  paintProgress();
});
