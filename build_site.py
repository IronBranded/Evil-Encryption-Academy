#!/usr/bin/env python3
"""Builds the Evil Encryption Academy site. Run: python3 build_site.py"""
import os

NAV = open("assets/_nav.html").read()

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__ — Evil Encryption Academy</title>
<meta name="description" content="__DESC__">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/academy.css">
</head>
<body>
<button class="menu-btn ghost">Menu</button>
<div class="shell">
<aside class="side">
__NAV__</aside>
<main>
<p class="crumb">__CRUMB__</p>
<h1>__H1__</h1>
<p class="lede">__LEDE__</p>
__BODY__
<div class="pager">__PREV____NEXT__</div>
</main>
</div>
<script src="assets/academy.js"></script>
<script>
(function(){var l=document.querySelector('.side a[data-p="__PID__"]');if(l)l.classList.add('on');})();
</script>
__SIM__
</body>
</html>"""


def build(fn, pid, crumb, h1, lede, body, sim="", prev=None, nxt=None, desc=None):
    p = f'<a href="{prev[0]}"><em>Previous</em>{prev[1]}</a>' if prev else "<span></span>"
    n = f'<a class="nxt" href="{nxt[0]}"><em>Next</em>{nxt[1]}</a>' if nxt else "<span></span>"
    html = (HEAD.replace("__NAV__", NAV).replace("__TITLE__", h1)
            .replace("__DESC__", (desc or lede)[:155].replace('"', "'"))
            .replace("__CRUMB__", crumb).replace("__H1__", h1).replace("__LEDE__", lede)
            .replace("__BODY__", body).replace("__PREV__", p).replace("__NEXT__", n)
            .replace("__PID__", pid).replace("__SIM__", sim))
    open(fn, "w", encoding="utf-8").write(html)
    return fn


# ===========================================================================
# INDEX
# ===========================================================================
build("index.html", "index", "Evil Encryption Academy",
 "Encryption, and how ransomware uses it",
 "Ransomware is an applied cryptography problem wearing a Windows costume. "
 "This site explains the encryption itself: the types, how each one works, how ransomware "
 "combines them, and how to tell the schemes apart. Every page has a working simulation.",
 """
<h2>Why encryption is the whole story</h2>
<p>Strip away the delivery, the extortion and the branding, and every ransomware family reduces
to a handful of cryptographic decisions: which cipher encrypts the data, which one protects the
key, how much of each file gets touched, and whether one key or many are used.</p>
<p>Those four decisions determine everything a defender can observe and everything a victim
experiences. Learn them and the families stop looking like a hundred different threats and start
looking like a small number of recurring designs.</p>

<h2>What you will be able to do</h2>
<ul>
  <li>Explain the difference between encoding, hashing and encryption, and why only one of them locks anything</li>
  <li>Describe how AES and ChaCha20 work, and why the mode of operation matters more than the cipher</li>
  <li>Explain why RSA and elliptic curves cannot encrypt a hard drive, and what they are actually for</li>
  <li>Describe the hybrid scheme every modern family uses, and why it is so effective</li>
  <li>Recognise full, header-only, intermittent and chunked encryption from the shape of the result</li>
  <li>Tell one scheme apart from another using only the encrypted output</li>
</ul>

<h2>The path</h2>
<table>
<tr><th>#</th><th>Topic</th><th>The idea</th></tr>
<tr><td>01</td><td><a href="01-what-encryption-is.html">What encryption is</a></td><td>Three things people confuse, and the operation underneath all of them</td></tr>
<tr><td>02</td><td><a href="02-symmetric.html">Symmetric encryption</a></td><td>One key, enormous speed, and the two cipher families</td></tr>
<tr><td>03</td><td><a href="03-modes.html">Modes of operation</a></td><td>Where a correct cipher still produces a broken result</td></tr>
<tr><td>04</td><td><a href="04-asymmetric.html">Asymmetric encryption</a></td><td>Two keys, tiny capacity, and why that is enough</td></tr>
<tr><td>05</td><td><a href="05-hybrid.html">The hybrid scheme</a></td><td>How the two families combine into the ransomware core</td></tr>
<tr><td>06</td><td><a href="06-coverage.html">How much gets encrypted</a></td><td>Full, header-only, intermittent, chunked</td></tr>
<tr><td>07</td><td><a href="07-key-models.html">Key models</a></td><td>One key for everything, or one key per file</td></tr>
<tr><td>08</td><td><a href="08-os-native.html">OS-native encryption</a></td><td>When the operating system does the encrypting</td></tr>
<tr><td>09</td><td><a href="09-telling-them-apart.html">Telling them apart</a></td><td>Identifying a scheme from its output alone</td></tr>
</table>

<div class="note">
<p><b>Concepts, not operations.</b> This site explains how encryption schemes work and how to
recognise them. It contains no encryption tooling, no malware, and no operational procedures.
The simulations run entirely in your browser using the standard Web Crypto API, and the keys
are printed on screen — nothing here is secret and nothing is irreversible.</p>
</div>

<h2>Start</h2>
<p style="margin-top:20px"><a href="01-what-encryption-is.html"><button>Begin with module 01</button></a></p>
""",
 nxt=("01-what-encryption-is.html", "What encryption is"))


# ===========================================================================
# 01 — WHAT ENCRYPTION IS
# ===========================================================================
build("01-what-encryption-is.html", "01", "Foundations · 01",
 "What encryption is",
 "Three operations get called encryption and only one of them is. Getting these apart is the "
 "single most useful thing on this site, because every later idea depends on it.",
 """
<h2>The three confusions</h2>
<table>
<tr><th></th><th>What it does</th><th>Reversible?</th><th>Needs a key?</th></tr>
<tr><td><strong>Encoding</strong></td><td>Changes representation for transport</td><td>Yes, by anyone</td><td>No</td></tr>
<tr><td><strong>Hashing</strong></td><td>Produces a fixed-size fingerprint</td><td><strong>Never</strong></td><td>No</td></tr>
<tr><td><strong>Encryption</strong></td><td>Makes data unreadable without a key</td><td>Yes, with the key</td><td><strong>Yes</strong></td></tr>
</table>

<p><strong>Base64 is not encryption.</strong> It has no key. Anyone can decode it. When you see
base64 in a ransom note or attached to an encrypted file, it is being used as <em>storage</em> —
a way to write binary data as text — not as protection.</p>

<p><strong>Hashing is not encryption.</strong> A hash cannot be reversed, even by whoever created
it. Hashes identify and verify; they never lock anything. A 4 GB video and a one-word text file
both produce the same 32-byte SHA-256 output, which tells you immediately that the original
cannot be inside it.</p>

<p><strong>Encryption is not damage.</strong> This one matters most when explaining an incident to
someone. An encrypted file is completely intact. Every byte of the original is recoverable with
the key. Nothing was deleted and nothing was corrupted — the data was transformed, and the
transformation runs backwards.</p>

<div class="sim">
  <div class="sim-head"><b>Simulation · the three transforms</b><span>Web Crypto, real AES-256</span></div>
  <div class="sim-body">
    <p>Type anything. Each transform runs on the same input, then each is asked to reverse.</p>
    <div class="row"><input type="text" id="s1-in" value="Transfer 48200.00 to account 4417"></div>
    <div class="row"><button id="s1-go">Transform</button><button class="ghost" id="s1-rev">Try to reverse each</button></div>
    <table style="margin-top:6px">
      <tr><th>Transform</th><th>Output</th></tr>
      <tr><td>Base64<br><span class="stat">encoding</span></td><td><div class="out" id="s1-b64" style="margin:0"></div></td></tr>
      <tr><td>SHA-256<br><span class="stat">hashing</span></td><td><div class="out" id="s1-sha" style="margin:0"></div></td></tr>
      <tr><td>AES-256-CBC<br><span class="stat">encryption</span></td><td><div class="out" id="s1-aes" style="margin:0"></div></td></tr>
    </table>
    <div class="out" id="s1-rout" style="margin-top:14px">Press "Try to reverse each" to see which survive the round trip.</div>
    <p class="stat" id="s1-key"></p>
  </div>
</div>

<h2>XOR: the operation underneath everything</h2>
<p>XOR compares two bits and returns 1 when they differ:</p>
<div class="out tight">0 XOR 0 = 0      1 XOR 0 = 1
0 XOR 1 = 1      1 XOR 1 = 0</div>
<p>The property that makes it the foundation of cryptography is that <strong>XOR is its own
inverse</strong>. Apply the same key twice and you are back where you started:</p>
<div class="out tight">data XOR key = ciphertext
ciphertext XOR key = data</div>

<p>Every cipher on this site ends in an XOR. AES and ChaCha20 differ in <em>how they generate the
thing you XOR with</em> — not in the combining step. Once XOR makes sense, the shape of every
cipher makes sense.</p>

<div class="sim">
  <div class="sim-head"><b>Simulation · XOR is its own inverse</b><span>watch it undo itself</span></div>
  <div class="sim-body">
    <div class="row"><input type="text" id="s2-in" value="CONFIDENTIAL"></div>
    <div class="row"><label>Key byte</label><input type="range" id="s2-k" min="1" max="255" value="90" style="flex:1">
      <span class="stat" id="s2-kv">0x5A</span></div>
    <div class="out tight" id="s2-out"></div>
    <p class="stat">A single repeating key byte is the weakest possible cipher — 255 guesses breaks it.
    Real ciphers generate a keystream as long as the message, which is the entire difference.</p>
  </div>
</div>

<div class="note">
<p><b>Why this matters for ransomware.</b> A file that has been base64-encoded looks scrambled but
is trivially readable. A file that has been hashed is gone entirely. A file that has been encrypted
is perfectly intact and unreadable. Only the third produces the situation ransomware depends on:
the data still exists, and access to it is controlled by whoever holds the key.</p>
</div>
""",
 sim="""<script>
const S1KEY = (async()=>await demoKeyBytes())();
async function s1run(){
  const v = document.getElementById('s1-in').value;
  const k = await S1KEY;
  document.getElementById('s1-b64').textContent = btoa(unescape(encodeURIComponent(v)));
  document.getElementById('s1-sha').textContent = hex(await crypto.subtle.digest('SHA-256', bytes(v)));
  const iv = new Uint8Array(16);
  const ct = await aesCBC(bytes(v), k, iv);
  document.getElementById('s1-aes').textContent = hex(ct);
  document.getElementById('s1-key').textContent = 'demo key (public, fixed): ' + hex(k).slice(0,32) + '…';
  document.getElementById('s1-rout').textContent = 'Press "Try to reverse each" to see which survive the round trip.';
}
async function s1rev(){
  const v = document.getElementById('s1-in').value, k = await S1KEY;
  const b64 = btoa(unescape(encodeURIComponent(v)));
  let o = '';
  o += 'Base64   → ' + decodeURIComponent(escape(atob(b64))) + '\\n';
  o += '           reversed with no key at all. This was never protection.\\n\\n';
  o += 'SHA-256  → cannot be reversed, by anyone, ever.\\n';
  o += '           The output is 32 bytes regardless of input size. The\\n';
  o += '           original is not in there to recover.\\n\\n';
  const iv = new Uint8Array(16);
  const ct = await aesCBC(bytes(v), k, iv);
  const kk = await aesKey(k);
  const pt = await crypto.subtle.decrypt({name:'AES-CBC', iv}, kk, ct);
  o += 'AES-256  → ' + text(pt) + '\\n';
  o += '           reversed exactly, because we hold the key. Without it,\\n';
  o += '           this line is unreachable. That gap is the whole of ransomware.';
  document.getElementById('s1-rout').textContent = o;
}
document.getElementById('s1-go').addEventListener('click', s1run);
document.getElementById('s1-rev').addEventListener('click', s1rev);
document.getElementById('s1-in').addEventListener('input', s1run);
s1run();

function s2run(){
  const v = document.getElementById('s2-in').value;
  const k = +document.getElementById('s2-k').value;
  document.getElementById('s2-kv').textContent = '0x' + k.toString(16).padStart(2,'0').toUpperCase();
  const a = bytes(v);
  const enc = a.map(b => b ^ k);
  const dec = enc.map(b => b ^ k);
  const show = u => [...u].map(b => (b>=32&&b<127)?String.fromCharCode(b):'·').join('');
  document.getElementById('s2-out').textContent =
    'plaintext   ' + show(a)   + '\\n' +
    'XOR key     ' + show(enc) + '   ← unreadable\\n' +
    'XOR again   ' + show(dec) + '   ← back to the start';
}
document.getElementById('s2-k').addEventListener('input', s2run);
document.getElementById('s2-in').addEventListener('input', s2run);
s2run();
</script>""",
 prev=("index.html", "Overview"), nxt=("02-symmetric.html", "Symmetric encryption"))

print("built: index, 01")


# ===========================================================================
# 02 — SYMMETRIC
# ===========================================================================
build("02-symmetric.html", "02", "Foundations · 02",
 "Symmetric encryption",
 "One key locks and unlocks. It is fast enough to encrypt a whole disk, which is exactly why "
 "every ransomware family uses it to do the actual work.",
 """
<h2>One key, both directions</h2>
<p>Symmetric encryption uses a single key for both operations. Like a padlock where the same key
opens and closes it. That simplicity is what makes it fast: a modern processor encrypts
somewhere between one and five gigabytes per second with AES.</p>
<p>The obvious problem is distribution. Whoever encrypts must hold the key, and if the key stays
with the data then anyone who has the data has the key. Ransomware solves this by borrowing from
<a href="04-asymmetric.html">asymmetric cryptography</a> — covered in module 05.</p>

<h2>Two families</h2>
<table>
<tr><th></th><th>Block ciphers</th><th>Stream ciphers</th></tr>
<tr><td>Example</td><td>AES</td><td>ChaCha20, XChaCha20</td></tr>
<tr><td>Works on</td><td>Fixed 16-byte blocks</td><td>A keystream XORed with the data</td></tr>
<tr><td>Output size</td><td>Padded up to a block multiple</td><td>Identical to the input</td></tr>
<tr><td>Speed comes from</td><td><strong>Hardware</strong> (AES-NI instructions)</td><td><strong>Software</strong>, no special hardware</td></tr>
<tr><td>Chosen when</td><td>Running on x86 with acceleration</td><td>Cross-platform, no hardware assumptions</td></tr>
</table>

<p>That last row explains a shift in the landscape. Families written in Rust and Go — which target
Windows, Linux and ESXi from one codebase — overwhelmingly pick ChaCha20 or its extended-nonce
variant XChaCha20, because it is fast everywhere without depending on CPU features.</p>

<h3>AES, briefly</h3>
<p>AES takes 16 bytes at a time. It expands your key into a set of round keys, then for 10, 12 or
14 rounds it substitutes bytes through a fixed lookup table, shifts rows, mixes columns, and XORs
in the round key. Every step is reversible. The number of rounds depends on key size: 10 for
AES-128, 14 for AES-256.</p>

<h3>ChaCha20, briefly</h3>
<p>ChaCha20 never touches your data until the very end. It builds a 64-byte internal state from a
fixed constant, the key, a counter and a nonce, then stirs that state through 20 rounds of
addition, XOR and rotation. The stirred state <em>is</em> the keystream, which gets XORed with the
plaintext. Because it only ever produces a keystream, output is exactly as long as input.</p>

<div class="sim">
  <div class="sim-head"><b>Simulation · what encryption does to data</b><span>real AES-256-CBC</span></div>
  <div class="sim-body">
    <p>The same content before and after. Watch the byte distribution flatten.</p>
    <div class="row"><textarea id="s3-in">INVOICE 2024-0417
Customer: Acme Industrial Ltd
Amount Due: 48,200.00 GBP
Status: UNPAID</textarea></div>
    <div class="grid2">
      <div>
        <p class="stat"><b>Before</b> — plaintext</p>
        <div class="out tight" id="s3-pt"></div>
        <p class="stat">byte frequency</p>
        <div class="out tight" id="s3-ph"></div>
        <p class="stat">entropy <b id="s3-pe"></b> / 8.000</p>
      </div>
      <div>
        <p class="stat"><b>After</b> — AES-256-CBC</p>
        <div class="out tight" id="s3-ct"></div>
        <p class="stat">byte frequency</p>
        <div class="out tight" id="s3-ch"></div>
        <p class="stat">entropy <b id="s3-ce"></b> / 8.000</p>
      </div>
    </div>
    <p class="stat" id="s3-size" style="margin-top:12px"></p>
  </div>
</div>

<p>The left histogram is spiky because English text clusters — lots of lowercase letters, spaces
and digits, nothing in the high byte values. The right one is flat because every byte value now
occurs about equally often. That flatness is what an entropy score measures.</p>

<div class="note">
<p><b>Encryption does not compress or shuffle.</b> It maps structured data onto output that is
statistically indistinguishable from random noise. Notice the size: the ciphertext is slightly
<em>larger</em>, because a block cipher pads the input up to a multiple of 16 bytes.</p>
</div>
""",
 sim="""<script>
const S3KEY = (async()=>await demoKeyBytes('module-02'))();
async function s3run(){
  const v = document.getElementById('s3-in').value;
  const pt = bytes(v), k = await S3KEY;
  const ct = await aesCBC(pt, k, new Uint8Array(16));
  document.getElementById('s3-pt').textContent = hexdump(pt, 48);
  document.getElementById('s3-ct').textContent = hexdump(ct, 48);
  document.getElementById('s3-ph').textContent = histogram(pt);
  document.getElementById('s3-ch').textContent = histogram(ct);
  document.getElementById('s3-pe').textContent = shannon(pt).toFixed(3);
  document.getElementById('s3-ce').textContent = shannon(ct).toFixed(3);
  document.getElementById('s3-size').textContent =
    'size before ' + pt.length + ' bytes  ·  after ' + ct.length +
    ' bytes  ·  +' + (ct.length - pt.length) + ' bytes of block padding';
}
document.getElementById('s3-in').addEventListener('input', s3run);
s3run();
</script>""",
 prev=("01-what-encryption-is.html","What encryption is"), nxt=("03-modes.html","Modes of operation"))


# ===========================================================================
# 03 — MODES
# ===========================================================================
build("03-modes.html", "03", "Foundations · 03",
 "Modes of operation",
 "AES is not broken. AES-ECB is. The mode decides whether a perfectly correct cipher produces a "
 "secure result or leaks your data in plain sight.",
 """
<h2>The problem a mode solves</h2>
<p>A block cipher encrypts exactly 16 bytes. Real files are larger, so something has to decide how
the blocks relate to each other. That decision is the <em>mode of operation</em>, and it matters
more than the choice of cipher.</p>

<table>
<tr><th>Mode</th><th>How blocks relate</th><th>Recognisable by</th></tr>
<tr><td><strong>ECB</strong></td><td>Each block encrypted independently</td><td><strong>Repeating 16-byte ciphertext blocks</strong></td></tr>
<tr><td><strong>CBC</strong></td><td>Each block XORed with the previous ciphertext</td><td>16-byte IV, size a multiple of 16, padding</td></tr>
<tr><td><strong>CTR</strong></td><td>Counter encrypted to make a keystream</td><td>Output identical in size to input</td></tr>
<tr><td><strong>GCM</strong></td><td>CTR plus an authentication tag</td><td>12-byte nonce, 16-byte tag appended</td></tr>
<tr><td><strong>XTS</strong></td><td>Tweaked per disk sector</td><td>Full-disk encryption; used by BitLocker</td></tr>
</table>

<h2>Why ECB fails, seen directly</h2>
<p>ECB encrypts each block on its own, with no reference to any other block. So identical
plaintext blocks always produce identical ciphertext blocks. Any large uniform region of a
file — a background, a run of zeroes, a repeated record — stays uniform after encryption.</p>
<p>The image below is encrypted with real AES-256. Both panels use the same key.</p>

<div class="sim">
  <div class="sim-head"><b>Simulation · the same image, two modes</b><span>real AES-256, identical key</span></div>
  <div class="sim-body">
    <div class="grid2">
      <div><canvas id="s4-src" width="160" height="120" style="width:100%"></canvas>
        <p class="cap">original</p></div>
      <div><canvas id="s4-ecb" width="160" height="120" style="width:100%"></canvas>
        <p class="cap c-cipher">AES-256-ECB — still readable</p></div>
    </div>
    <div class="grid2" style="margin-top:14px">
      <div><canvas id="s4-cbc" width="160" height="120" style="width:100%"></canvas>
        <p class="cap c-plain">AES-256-CBC — structure destroyed</p></div>
      <div>
        <p class="stat" id="s4-stats"></p>
        <p class="stat" style="margin-top:10px">ECB scores high entropy <em>and is still broken</em>.
        Entropy measures how evenly bytes are distributed. It cannot see that the same block
        keeps repeating, which is exactly what leaks the picture.</p>
      </div>
    </div>
  </div>
</div>

<p>The measurement that catches ECB is not entropy but <strong>distinct block count</strong>. If a
file's 16-byte blocks repeat, the plaintext blocks repeated too — and that leaks structure
without needing the key at all.</p>

<h2>The avalanche effect</h2>
<p>Change one bit of input and roughly half of every output bit changes. This is a design
requirement, and it is why there is no such thing as a nearly-correct key.</p>

<div class="sim">
  <div class="sim-head"><b>Simulation · one bit in, half the output changes</b><span>AES-256-CBC</span></div>
  <div class="sim-body">
    <div class="row"><input type="text" id="s5-in" value="Transfer 1000.00 GBP to account 4417"></div>
    <div class="row"><label>Flip bit</label><input type="range" id="s5-b" min="0" max="63" value="0" style="flex:1">
      <span class="stat" id="s5-bv"></span></div>
    <div class="out tight" id="s5-out"></div>
    <p class="stat" id="s5-stat"></p>
  </div>
</div>

<div class="note">
<p><b>What this rules out.</b> There is no partial progress against a cipher. Guessing 255 of 256
key bits correctly produces output as wrong as guessing none of them. Brute force is not a
strategy against a correctly used cipher — which is why the interesting questions are always
about how the key was made and where it went, not about the cipher itself.</p>
</div>
""",
 sim="""<script>
/* ---- ECB vs CBC on a real image ---- */
function drawSource(ctx,w,h){
  ctx.fillStyle='#FCFCFA'; ctx.fillRect(0,0,w,h);
  ctx.fillStyle='#191D21';
  ctx.fillRect(46,52,68,52);                                  // body
  ctx.lineWidth=11; ctx.strokeStyle='#191D21';
  ctx.beginPath(); ctx.arc(80,52,22,Math.PI,0); ctx.stroke();  // shackle
  ctx.fillStyle='#FCFCFA';
  ctx.beginPath(); ctx.arc(80,72,8,0,Math.PI*2); ctx.fill();   // keyhole
  ctx.fillRect(76,72,8,20);
}
async function s4run(){
  const w=160,h=120;
  const src=document.getElementById('s4-src'), sc=src.getContext('2d');
  drawSource(sc,w,h);
  const img=sc.getImageData(0,0,w,h);
  // one byte per pixel, padded to a 16-byte multiple
  const n=w*h, pad=(16-(n%16))%16, gray=new Uint8Array(n+pad);
  for(let i=0;i<n;i++) gray[i]=img.data[i*4];
  const k=await demoKeyBytes('module-03-image');
  const ecb=await aesECB(gray,k);
  const cbc=await aesCBC(gray,k,new Uint8Array(16));
  const paint=(id,data)=>{
    const c=document.getElementById(id), cx=c.getContext('2d');
    const o=cx.createImageData(w,h);
    for(let i=0;i<n;i++){ const v=data[i];
      o.data[i*4]=o.data[i*4+1]=o.data[i*4+2]=v; o.data[i*4+3]=255; }
    cx.putImageData(o,0,0);
  };
  paint('s4-ecb',ecb); paint('s4-cbc',cbc);
  const total=Math.floor(gray.length/16);
  document.getElementById('s4-stats').innerHTML =
    'plaintext entropy <b>'+shannon(gray).toFixed(2)+'</b><br>'+
    'ECB entropy <b>'+shannon(ecb).toFixed(2)+'</b><br>'+
    'CBC entropy <b>'+shannon(cbc).toFixed(2)+'</b><br><br>'+
    'distinct 16-byte blocks<br>ECB <b class="c-cipher">'+distinctBlocks(ecb)+'</b> of '+total+
    '<br>CBC <b class="c-plain">'+distinctBlocks(cbc)+'</b> of '+total;
}
s4run();

/* ---- avalanche ---- */
async function s5run(){
  const v=document.getElementById('s5-in').value;
  const bit=+document.getElementById('s5-b').value;
  const a=bytes(v); const b=new Uint8Array(a);
  const byteI=Math.floor(bit/8)%b.length;
  b[byteI]^=(1<<(bit%8));
  document.getElementById('s5-bv').textContent='byte '+byteI+', bit '+(bit%8);
  const k=await demoKeyBytes('module-03-av'), iv=new Uint8Array(16);
  const ca=await aesCBC(a,k,iv), cb=await aesCBC(b,k,iv);
  let diffBits=0,diffBytes=0;
  for(let i=0;i<Math.min(ca.length,cb.length);i++){
    const x=ca[i]^cb[i]; if(x) diffBytes++;
    for(let j=0;j<8;j++) if(x&(1<<j)) diffBits++;
  }
  const tot=Math.min(ca.length,cb.length)*8;
  document.getElementById('s5-out').textContent =
    'input A   '+hex(a.slice(0,16))+'\\n'+
    'input B   '+hex(b.slice(0,16))+'   ← one bit different\\n\\n'+
    'cipher A  '+hex(ca.slice(0,16))+'\\n'+
    'cipher B  '+hex(cb.slice(0,16));
  document.getElementById('s5-stat').textContent =
    'bytes changed '+diffBytes+' of '+Math.min(ca.length,cb.length)+
    '   ·   bits changed '+diffBits+' of '+tot+'  ('+(diffBits/tot*100).toFixed(1)+'%)';
}
document.getElementById('s5-b').addEventListener('input',s5run);
document.getElementById('s5-in').addEventListener('input',s5run);
s5run();
</script>""",
 prev=("02-symmetric.html","Symmetric encryption"), nxt=("04-asymmetric.html","Asymmetric encryption"))

print("built: 02, 03")


# ===========================================================================
# 04 — ASYMMETRIC
# ===========================================================================
build("04-asymmetric.html", "04", "Foundations · 04",
 "Asymmetric encryption",
 "Two keys instead of one. It solves the distribution problem that symmetric encryption cannot, "
 "and it is far too slow and too small to encrypt anything substantial.",
 """
<h2>A mailbox, not a padlock</h2>
<p>Asymmetric encryption uses a matched pair. The <strong>public key</strong> locks; only the
<strong>private key</strong> opens. Publish the public half freely — it cannot undo its own work.</p>
<p>The everyday analogy is a mailbox with a posting slot. Anyone can post. Only the person holding
the box key can take anything out. You can hand the slot to the world without risk.</p>

<h2>Two hard limits</h2>
<p>These are the constraints that decide how ransomware is built, so they are worth stating precisely.</p>

<h3>Limit one: it can barely hold anything</h3>
<p>An RSA operation cannot encrypt more data than its modulus, minus padding overhead.</p>
<table>
<tr><th>Key size</th><th>Modulus</th><th>Maximum plaintext per operation</th></tr>
<tr><td>RSA-2048</td><td>256 bytes</td><td>190 bytes</td></tr>
<tr><td>RSA-4096</td><td>512 bytes</td><td><strong>446 bytes</strong></td></tr>
</table>
<p>To encrypt a 10 GB disk image with RSA-4096 alone you would need roughly 24 million separate
operations.</p>

<h3>Limit two: it is thousands of times slower</h3>
<table>
<tr><th>Operation</th><th>Rough throughput</th></tr>
<tr><td>AES-256 with hardware acceleration</td><td>1–5 GB/s</td></tr>
<tr><td>ChaCha20 in software</td><td>1–3 GB/s</td></tr>
<tr><td>RSA-4096 encryption</td><td>~10,000 ops/sec ≈ 4 MB/s</td></tr>
</table>
<p>That 10 GB disk takes seconds with AES and days with RSA. Ransomware races detection; it cannot
afford days.</p>

<div class="sim">
  <div class="sim-head"><b>Simulation · a working keypair, with tiny numbers</b><span>real RSA maths, unsafe key size</span></div>
  <div class="sim-body">
    <p>RSA with two small primes so the arithmetic is visible. The maths is identical to the real
    thing — only the size differs, and that size is the entire security.</p>
    <div class="row">
      <label>p</label><select id="s6-p"><option>11</option><option selected>17</option><option>23</option></select>
      <label>q</label><select id="s6-q"><option>13</option><option selected>19</option><option>29</option></select>
      <button id="s6-gen">Generate keypair</button>
    </div>
    <div class="out" id="s6-keys"></div>
    <div class="row"><label>Message (a number below n)</label>
      <input type="text" id="s6-m" value="42" style="max-width:120px"></div>
    <div class="out tight" id="s6-out"></div>
    <p class="stat">Try encrypting with the private key instead — the public one then reverses it.
    That direction is how digital signatures work.</p>
  </div>
</div>

<h2>Elliptic curves</h2>
<p>ECC achieves comparable security with far smaller keys. A 256-bit elliptic curve key is roughly
equivalent to RSA-3072. Modern ransomware families increasingly prefer Curve25519 for this reason.</p>
<table>
<tr><th></th><th>RSA</th><th>Elliptic curve</th></tr>
<tr><td>Typical key size</td><td>2048–4096 bits</td><td>256 bits</td></tr>
<tr><td>Stored alongside a file</td><td>256 or 512 bytes</td><td><strong>32 bytes</strong></td></tr>
<tr><td>Common curve</td><td>—</td><td>Curve25519, secp256k1, NIST P-256</td></tr>
</table>
<p>The practical consequence shows up in module 09: a large fixed-size blob attached to an
encrypted file suggests RSA, while a small 32-byte one suggests elliptic curve.</p>

<h3>Key agreement, not encryption</h3>
<p>Elliptic curves are usually used differently from RSA. Rather than encrypting a key directly,
two parties each combine their own private key with the other's public key and independently
arrive at the <em>same</em> shared secret, without that secret ever crossing the wire. This is
Diffie-Hellman, and it is how the most current ransomware schemes work — see module 07.</p>

<div class="note">
<p><b>Where this is heading.</b> Asymmetric cryptography cannot encrypt your files. It is far too
slow and far too small. But it can encrypt something small — like a 32-byte symmetric key — and
that is precisely enough. Module 05 puts the two halves together.</p>
</div>
""",
 sim="""<script>
function egcd(a,b){ if(!b) return [a,1,0]; const [g,x,y]=egcd(b,a%b); return [g,y,x-Math.floor(a/b)*y]; }
function modinv(a,m){ const [g,x]=egcd(((a%m)+m)%m,m); return g!==1?null:((x%m)+m)%m; }
function modpow(b,e,m){ let r=1n; b=BigInt(b)%BigInt(m); e=BigInt(e); m=BigInt(m);
  while(e>0n){ if(e&1n) r=r*b%m; b=b*b%m; e>>=1n; } return Number(r); }
function s6run(){
  const p=+document.getElementById('s6-p').value, q=+document.getElementById('s6-q').value;
  const n=p*q, phi=(p-1)*(q-1);
  let e=3; while(egcd(e,phi)[0]!==1) e+=2;
  const d=modinv(e,phi);
  document.getElementById('s6-keys').textContent =
    'p = '+p+'   q = '+q+'\\n'+
    'n = p × q = '+n+'          ← the modulus, published\\n'+
    'φ(n) = (p-1)(q-1) = '+phi+'   ← kept secret\\n\\n'+
    'PUBLIC  key (e, n) = ('+e+', '+n+')     anyone may have this\\n'+
    'PRIVATE key (d, n) = ('+d+', '+n+')     only the owner has this';
  let m=parseInt(document.getElementById('s6-m').value||'0',10);
  if(isNaN(m)) m=0;
  if(m>=n){ document.getElementById('s6-out').textContent =
    'Message must be smaller than n = '+n+'.\\n\\nThis IS the capacity limit, in miniature: RSA can '+
    'never encrypt anything\\nlarger than its modulus. Real keys are 2048 or 4096 bits, which is '+
    'still\\nonly a few hundred bytes.'; return; }
  const c=modpow(m,e,n), back=modpow(c,d,n);
  document.getElementById('s6-out').textContent =
    'message   m = '+m+'\\n'+
    'encrypt   c = m^e mod n = '+m+'^'+e+' mod '+n+' = '+c+'   ← using the PUBLIC key\\n'+
    'decrypt   m = c^d mod n = '+c+'^'+d+' mod '+n+' = '+back+'   ← using the PRIVATE key\\n\\n'+
    (back===m ? 'Round trip succeeded. The public key locked it; only d opened it.'
              : 'Round trip failed — pick a different message.');
}
['s6-p','s6-q','s6-m'].forEach(id=>document.getElementById(id).addEventListener('input',s6run));
document.getElementById('s6-gen').addEventListener('click',s6run);
s6run();
</script>""",
 prev=("03-modes.html","Modes of operation"), nxt=("05-hybrid.html","The hybrid scheme"))


# ===========================================================================
# 05 — HYBRID
# ===========================================================================
build("05-hybrid.html", "05", "Ransomware encryption · 05",
 "The hybrid scheme",
 "Symmetric encryption is fast but cannot protect its own key. Asymmetric encryption protects "
 "keys but cannot encrypt data. Combine them and you get the design behind every modern family.",
 """
<h2>The combination</h2>
<p>Neither family is sufficient alone, but their weaknesses are complementary. The hybrid scheme
uses each for exactly what it is good at:</p>
<ol>
  <li>Generate a random symmetric key on the victim's machine</li>
  <li>Encrypt the file with it — fast, handles any size</li>
  <li>Encrypt <em>that key</em> with an embedded public key — slow, but it is only 32 bytes</li>
  <li>Store the wrapped key alongside the file</li>
  <li>Erase the plaintext symmetric key from memory</li>
</ol>

<p>The result is asymmetric security at symmetric speed. This is not sinister engineering — it is
exactly how TLS and PGP work. The cryptography is textbook. Only the intent differs.</p>

<div class="note">
<p><b>The sentence that describes every ransomware incident:</b> the locked file and the key that
opens it are both sitting on the victim's disk. Neither helps, because the key is sealed under a
public key whose private half was never on the network.</p>
</div>

<div class="sim">
  <div class="sim-head"><b>Simulation · walk the scheme</b><span>step through it</span></div>
  <div class="sim-body">
    <div class="row"><button id="s7-next">Next step</button><button class="ghost" id="s7-reset">Reset</button>
      <span class="stat" id="s7-step"></span></div>
    <div class="out tight" id="s7-out" style="min-height:230px"></div>
  </div>
</div>

<h2>Why it is so effective</h2>
<table>
<tr><th>Property</th><th>Consequence</th></tr>
<tr><td>The public key is embedded in the payload</td><td>No network call needed to encrypt; it works fully offline</td></tr>
<tr><td>The private key never leaves attacker infrastructure</td><td>Analysing the sample reveals nothing that opens files</td></tr>
<tr><td>The symmetric key is random per victim, often per file</td><td>Nothing is reusable between targets</td></tr>
<tr><td>The plaintext key is erased after use</td><td>It exists only briefly, in memory, during encryption</td></tr>
</table>

<p>Each property closes a door. Together they produce a situation where the encrypted data is
intact and complete, and remains unreadable regardless of how much of the malware you understand.</p>

<h2>Where the wrapped key is stored</h2>
<p>The wrapped key has to travel with the file, or the attacker could not decrypt it later either.
Four common placements:</p>
<div class="out tight">FOOTER (most common)
[ ciphertext ......................... ][ wrapped key ][ marker ]

HEADER
[ wrapped key ][ IV ][ ciphertext ......................... ]

SIDECAR
  invoice.xlsx.locked        ciphertext only
  invoice.xlsx.locked.key    wrapped key

ONE PER HOST
  every file shares a key; a single wrapped blob is stored once</div>

<p>The placement and shape of that blob is one of the most reliable ways to tell schemes apart,
which is the subject of <a href="09-telling-them-apart.html">module 09</a>.</p>
""",
 sim="""<script>
const S7=[
 {t:'Before anything happens — off the victim network',
  b:'The operator generates an asymmetric keypair on their own\\ninfrastructure.\\n\\n'+
    '  PUBLIC KEY   →  embedded in the payload\\n'+
    '  PRIVATE KEY  →  never leaves their machine. Ever.\\n\\n'+
    'This is the only step that does not happen on the victim host,\\nand it is the reason the '+
    'scheme works.'},
 {t:'A random symmetric key is generated on the victim machine',
  b:'  file key = 3f8a1c04 9b27ee51 6d0a4477 c1e9b382 …  (32 bytes)\\n\\n'+
    'Produced by the secure random generator built into the OS.\\nUnpredictable, and different '+
    'on every machine and often every file.\\n\\n'+
    'RIGHT NOW this key exists in plain form, in memory.'},
 {t:'The file is encrypted with that symmetric key',
  b:'  invoice.xlsx  ──[ AES-256 / ChaCha20 ]──▶  ciphertext\\n\\n'+
    'Fast. Gigabytes per second. Size is essentially unchanged.\\n\\n'+
    'The file is now unreadable — but the key that opens it is still\\nsitting in memory, a few '+
    'centimetres away.'},
 {t:'The symmetric key is wrapped with the embedded public key',
  b:'  file key (32 bytes) ──[ RSA / Curve25519 ]──▶ wrapped key\\n\\n'+
    'Only 32 bytes go through the slow operation, so the cost is\\ntrivial. This is the step that '+
    'makes the whole design work.\\n\\n'+
    'The wrapped key can now only be opened by the private key,\\nwhich is not on this network.'},
 {t:'The wrapped key is written to disk with the file',
  b:'  [ ciphertext ........................ ][ wrapped key ]\\n\\n'+
    'It has to be stored, or the operator could not decrypt later\\neither. It is safe to leave in '+
    'the open — without the private\\nkey it is just noise.'},
 {t:'The plaintext symmetric key is erased',
  b:'  file key = 00000000 00000000 00000000 00000000\\n\\n'+
    'Overwritten in memory. The only remaining copy of that key is\\nthe wrapped one on disk, and '+
    'it cannot be opened here.\\n\\n'+
    'The file, the wrapped key and the malware are all present and\\nfully understood. None of it '+
    'opens the data.'}
];
let s7i=-1;
function s7draw(){
  const o=document.getElementById('s7-out');
  if(s7i<0){ o.textContent='Press "Next step" to walk through the scheme.';
    document.getElementById('s7-step').textContent=''; return; }
  const s=S7[s7i];
  o.textContent='STEP '+(s7i+1)+' — '+s.t+'\\n'+'─'.repeat(62)+'\\n\\n'+s.b;
  document.getElementById('s7-step').textContent='step '+(s7i+1)+' of '+S7.length;
}
document.getElementById('s7-next').addEventListener('click',()=>{
  if(s7i<S7.length-1) s7i++; s7draw(); });
document.getElementById('s7-reset').addEventListener('click',()=>{ s7i=-1; s7draw(); });
s7draw();
</script>""",
 prev=("04-asymmetric.html","Asymmetric encryption"), nxt=("06-coverage.html","How much gets encrypted"))

print("built: 04, 05")


# ===========================================================================
# 06 — COVERAGE
# ===========================================================================
build("06-coverage.html", "06", "Ransomware encryption · 06",
 "How much gets encrypted",
 "Encrypting an entire file server takes hours. Breaking every file on it takes minutes. Modern "
 "families exploit that difference, and it produces four distinct patterns you can see directly.",
 """
<h2>The insight being exploited</h2>
<p>You do not need to encrypt a file to make it unusable. You need to break its <em>structure</em>.
A database with its header and a few interior pages scrambled will not mount. A VM disk with its
descriptor damaged will not boot. The remaining bytes are irrelevant to whether the file opens.</p>
<p>So families encrypt less, and finish faster. This is a speed optimisation, and it produces four
recognisable coverage patterns.</p>

<h2>The four patterns</h2>
<table>
<tr><th>Pattern</th><th>What is encrypted</th><th>Why it is chosen</th></tr>
<tr><td><strong>Full</strong></td><td>Every byte</td><td>Simple, thorough, slow on large files</td></tr>
<tr><td><strong>Header-only</strong></td><td>The first few kilobytes</td><td>Fastest possible; most formats die without a header</td></tr>
<tr><td><strong>Intermittent</strong></td><td>Alternating bands throughout</td><td>Damage spread evenly at a fraction of the I/O</td></tr>
<tr><td><strong>Distributed chunks</strong></td><td>Regions at the start, middle and end</td><td>Hits header, index and trailer structures specifically</td></tr>
</table>

<p>A single incident frequently shows <strong>two patterns at once</strong>, split by file size.
Fast modes usually apply only above a threshold — often 1 MB — because the bookkeeping is not
worth it on a small file. So small documents get fully encrypted while large databases get a few
percent.</p>

<div class="sim">
  <div class="sim-head"><b>Simulation · coverage explorer</b><span>real AES on the encrypted regions</span></div>
  <div class="sim-body">
    <div class="row">
      <label>Pattern</label>
      <select id="s8-mode">
        <option value="full">Full encryption</option>
        <option value="header">Header-only</option>
        <option value="inter" selected>Intermittent bands</option>
        <option value="chunk">Distributed chunks</option>
      </select>
      <label>Coverage</label><input type="range" id="s8-pct" min="1" max="100" value="20" style="flex:1">
      <span class="stat" id="s8-pctv"></span>
    </div>
    <p class="stat">File map — each cell is a slice of the file</p>
    <div class="out tight" id="s8-map" style="font-size:15px;line-height:1.35"></div>
    <p class="stat">Entropy profile — measured per slice</p>
    <div class="out tight" id="s8-prof" style="font-size:15px;line-height:1.35"></div>
    <p class="stat" id="s8-stat"></p>
  </div>
</div>

<h2>Why the pattern is visible at all</h2>
<p>Encrypted bytes look random; structured bytes do not. Measuring entropy across a file in slices
produces a profile, and each coverage pattern draws a different shape:</p>
<div class="out tight">FULL                ████████████████████████████████████████████████

HEADER-ONLY         ████········································

INTERMITTENT        ████····████····████····████····████····████····

DISTRIBUTED CHUNKS  ██··························██··························██</div>

<div class="note">
<p><b>A trap worth knowing.</b> High entropy does not mean encrypted. JPEG, MP4 and ZIP files all
score near the maximum because compression also produces evenly distributed bytes. Entropy alone
cannot distinguish ciphertext from a photograph — module 09 covers what actually can.</p>
</div>

<h2>Fine striping</h2>
<p>Some families take this further, encrypting very small blocks — 512 bytes — at computed
intervals across the whole file. The effect is that damage is spread everywhere while total
coverage stays low.</p>
<p>This matters for identification because a coarse measurement misses it entirely. If you sample
entropy in 4 KB windows and each window is 512 encrypted bytes among 3,584 plaintext ones, every
window reads as mostly plaintext, and the file appears untouched. The pattern only appears when
you measure at a finer resolution than the stripe.</p>
""",
 sim="""<script>
async function s8run(){
  const mode=document.getElementById('s8-mode').value;
  const pct=+document.getElementById('s8-pct').value;
  document.getElementById('s8-pctv').textContent=pct+'%';
  const CELLS=48, SLICE=512, N=CELLS*SLICE;
  const rec=bytes('BEGIN RECORD; customer=ACME; amount=48200.00; status=OPEN; ');
  const buf=new Uint8Array(N);
  for(let i=0;i<N;i++) buf[i]=rec[i%rec.length];
  const cells=Math.max(1,Math.round(CELLS*pct/100));
  const encIdx=new Set();
  if(mode==='full'){ for(let i=0;i<CELLS;i++) encIdx.add(i); }
  else if(mode==='header'){ for(let i=0;i<cells;i++) encIdx.add(i); }
  else if(mode==='inter'){ const step=Math.max(1,Math.round(CELLS/cells));
    for(let i=0;i<CELLS;i+=step) encIdx.add(i); }
  else { const per=Math.max(1,Math.round(cells/3));
    for(let i=0;i<per;i++){ encIdx.add(i); encIdx.add(Math.floor(CELLS/2)+i); encIdx.add(CELLS-1-i); } }
  const k=await demoKeyBytes('module-06');
  for(const i of encIdx){
    if(i<0||i>=CELLS) continue;
    const ct=await aesCBC(buf.slice(i*SLICE,(i+1)*SLICE),k,new Uint8Array(16));
    buf.set(ct.slice(0,SLICE), i*SLICE);
  }
  let map='',prof='';
  const bars=' ▁▂▃▄▅▆▇█';
  for(let i=0;i<CELLS;i++){
    map += encIdx.has(i) ? '█' : '·';
    const e=shannon(buf.slice(i*SLICE,(i+1)*SLICE))/8;
    prof += bars[Math.min(bars.length-1,Math.round(e*(bars.length-1)))];
  }
  document.getElementById('s8-map').innerHTML =
    '<span class="c-cipher">'+map.replace(/·/g,'</span><span class="c-plain">·</span><span class="c-cipher">')+'</span>';
  document.getElementById('s8-prof').textContent = prof;
  const encBytes=encIdx.size*SLICE;
  document.getElementById('s8-stat').textContent =
    'encrypted '+encIdx.size+' of '+CELLS+' slices  ('+(encBytes/N*100).toFixed(1)+'% of the file)'+
    '   ·   overall entropy '+shannon(buf).toFixed(3)+' / 8.000';
}
['s8-mode','s8-pct'].forEach(id=>document.getElementById(id).addEventListener('input',s8run));
s8run();
</script>""",
 prev=("05-hybrid.html","The hybrid scheme"), nxt=("07-key-models.html","Key models"))


# ===========================================================================
# 07 — KEY MODELS
# ===========================================================================
build("07-key-models.html", "07", "Ransomware encryption · 07",
 "Key models",
 "One key for the whole machine, or a fresh key for every file. This single design choice changes "
 "more about a scheme than the choice of cipher does.",
 """
<h2>Two designs</h2>
<table>
<tr><th></th><th>Session key</th><th>Per-file keys</th></tr>
<tr><td>Keys generated</td><td>One, for the whole host</td><td>One per file</td></tr>
<tr><td>Wrapped blobs on disk</td><td>All identical, or stored once</td><td>All different</td></tr>
<tr><td>Speed</td><td>Slightly faster — one wrap operation</td><td>One wrap per file</td></tr>
<tr><td>Cross-file analysis</td><td>Possible — patterns may repeat</td><td>Impossible — nothing is shared</td></tr>
</table>

<p>Older families frequently used a session key because it is simpler. Modern ones use per-file
keys almost universally, because it removes an entire category of weakness: with a fresh key and
fresh nonce for every file, no two files share anything an analyst could compare.</p>

<div class="sim">
  <div class="sim-head"><b>Simulation · what each model leaves on disk</b><span>compare the wrapped blobs</span></div>
  <div class="sim-body">
    <div class="row">
      <label>Key model</label>
      <select id="s9-mode">
        <option value="session">Session key — one for the host</option>
        <option value="perfile" selected>Per-file keys</option>
      </select>
      <button id="s9-go">Encrypt five files</button>
    </div>
    <div class="out tight" id="s9-out" style="min-height:150px"></div>
    <p class="stat" id="s9-stat"></p>
  </div>
</div>

<h2>Ephemeral key agreement</h2>
<p>The most current designs go further than a random key per file. For each file they generate a
whole throwaway <em>keypair</em>, then use elliptic-curve Diffie-Hellman against the operator's
embedded public key to derive a shared secret. That secret becomes the file's encryption key.</p>

<div class="out tight">for every file:
  1. generate a throwaway keypair          (ephemeral private + public)
  2. combine ephemeral private + operator public   → shared secret
  3. use the shared secret as the file key
  4. store the ephemeral PUBLIC key with the file
  5. discard the ephemeral private key</div>

<p>Several properties fall out of this, and they are worth understanding because they explain why
these schemes have no analytical weak points:</p>
<ul>
  <li><strong>Nothing sensitive is stored.</strong> The value written to the file is a public key.
      On its own it reveals nothing.</li>
  <li><strong>No nonce field is needed.</strong> The nonce can be derived deterministically from
      the stored public key, so it never has to be written separately.</li>
  <li><strong>A fixed nonce becomes safe.</strong> Reusing a nonce is normally a serious bug, but
      it is only dangerous when the <em>key</em> repeats. Here every file has a unique shared
      secret, so a constant nonce never repeats under the same key.</li>
</ul>

<div class="note">
<p><b>Why that last point is worth remembering.</b> Seeing a zero nonce in a scheme usually
indicates a mistake. In a per-file ephemeral design it does not — the key lifecycle makes it
sound. Judging the nonce without checking how the key was produced gets this exactly backwards.</p>
</div>
""",
 sim="""<script>
async function s9run(){
  const mode=document.getElementById('s9-mode').value;
  const names=['invoice.xlsx','ledger.mdf','contract.docx','archive.pst','backup.vmdk'];
  const session=crypto.getRandomValues(new Uint8Array(32));
  let o='', blobs=[];
  for(const n of names){
    const fileKey = mode==='session' ? session : crypto.getRandomValues(new Uint8Array(32));
    // stand-in for a wrapped key: a deterministic transform of the file key
    const wrapped = hex(await crypto.subtle.digest('SHA-256', fileKey)).slice(0,32);
    blobs.push(wrapped);
    o += (n+'.locked').padEnd(22)+'wrapped key  '+wrapped+'\\n';
  }
  const uniq=new Set(blobs).size;
  document.getElementById('s9-out').textContent = o + '\\n' +
    'distinct wrapped blobs: '+uniq+' of '+blobs.length;
  document.getElementById('s9-stat').innerHTML = mode==='session'
    ? 'Every blob is <b>identical</b>. One key encrypted all five files, so the same wrapped value '+
      'is repeated on each. Comparing any two files reveals the model immediately.'
    : 'Every blob is <b>different</b>. Five files, five keys, five wraps. Nothing is shared between '+
      'files, so there is nothing to compare across them.';
}
document.getElementById('s9-go').addEventListener('click',s9run);
document.getElementById('s9-mode').addEventListener('change',s9run);
s9run();
</script>""",
 prev=("06-coverage.html","How much gets encrypted"), nxt=("08-os-native.html","OS-native encryption"))

print("built: 06, 07")


# ===========================================================================
# 08 — OS-NATIVE
# ===========================================================================
build("08-os-native.html", "08", "Ransomware encryption · 08",
 "OS-native encryption",
 "Some families ship no cryptography at all. They use the encryption already built into the "
 "operating system — which changes the shape of the problem completely.",
 """
<h2>Encryption without an encryptor</h2>
<p>Every scheme so far assumes the malware contains a cipher. That assumption fails against an
approach that simply switches on the disk encryption the operating system already provides.</p>
<p>There is no cipher to examine, because Microsoft wrote it. The encryption is correct,
well-tested and performed by signed system components doing exactly what they were designed to do.</p>

<table>
<tr><th></th><th>Custom encryptor</th><th>OS-native</th></tr>
<tr><td>Cipher</td><td>Compiled into the malware</td><td>Built into the operating system</td></tr>
<tr><td>Scope</td><td>Files matching a target list</td><td><strong>The entire volume, including the OS</strong></td></tr>
<tr><td>Victim experience</td><td>Files present but unreadable</td><td><strong>The machine will not boot</strong></td></tr>
<tr><td>Speed</td><td>Bounded by disk throughput</td><td>Can be near-instant — see below</td></tr>
</table>

<h2>How full-disk encryption is layered</h2>
<p>BitLocker is the common example, and its layering is what makes the attack work. There are
three levels, and the interesting one is in the middle.</p>

<div class="out tight">        YOUR DATA on the volume
              ▲
              │ encrypted with
        FVEK  (Full Volume Encryption Key)      AES-XTS
              ▲
              │ encrypted with
        VMK   (Volume Master Key)               ◀── the attack surface
              ▲
              │ protected by one or more PROTECTORS
      ┌───────┴────────┬──────────┬─────────────┐
     TPM          TPM + PIN    recovery      startup key
                              password</div>

<p>The volume is <strong>never re-encrypted when protectors change</strong>. Adding or removing a
protector rewrites only the small layer that guards the VMK — a few kilobytes. The terabytes of
data underneath are untouched.</p>

<p>That is the whole mechanism: <strong>add a protector only the attacker knows, remove the ones
the owner knows.</strong> The data never moves, so it takes seconds rather than hours.</p>

<div class="sim">
  <div class="sim-head"><b>Simulation · why swapping protectors is instant</b><span>compare the work done</span></div>
  <div class="sim-body">
    <div class="row">
      <label>Volume size</label>
      <select id="s10-size">
        <option value="500">500 GB</option>
        <option value="2000" selected>2 TB</option>
        <option value="10000">10 TB</option>
      </select>
      <label>Scenario</label>
      <select id="s10-mode">
        <option value="custom">Custom encryptor — rewrite every file</option>
        <option value="fresh">OS encryption from scratch — encrypt the volume</option>
        <option value="swap" selected>Volume already encrypted — swap the protector</option>
      </select>
    </div>
    <div class="out tight" id="s10-out" style="min-height:130px"></div>
  </div>
</div>

<h2>Two very different scenarios</h2>
<p>The distinction above matters a great deal, and it is often missed:</p>
<ul>
  <li><strong>The volume is already encrypted.</strong> Only the key-protection layer is rewritten.
      Seconds of work. No bulk encryption happens at all.</li>
  <li><strong>The volume is not encrypted.</strong> Encryption must be switched on and a full pass
      performed, which takes as long as any other full-disk encryption. Considerably slower, and
      it leaves far more evidence.</li>
</ul>

<h2>Other OS-provided mechanisms</h2>
<table>
<tr><th>Mechanism</th><th>Platform</th><th>What gets encrypted</th></tr>
<tr><td>BitLocker</td><td>Windows</td><td>Whole volumes, including the boot volume</td></tr>
<tr><td>EFS</td><td>Windows</td><td>Individual files, under a certificate</td></tr>
<tr><td>LUKS / dm-crypt</td><td>Linux, NAS</td><td>Whole volumes</td></tr>
<tr><td>Hypervisor VM encryption</td><td>ESXi, vSphere</td><td>Entire virtual machines at once</td></tr>
<tr><td>Cloud storage encryption</td><td>Object storage</td><td>Objects rewritten under a supplied key</td></tr>
</table>

<div class="note">
<p><b>The conceptual point.</b> Encryption is not inherently hostile. The same BitLocker that
protects a stolen laptop can lock out its owner — nothing about the cryptography changed, only who
holds the key. That is true of every scheme on this site, and it is why encryption is studied as a
neutral mechanism rather than as a weapon.</p>
</div>
""",
 sim="""<script>
function s10run(){
  const gb=+document.getElementById('s10-size').value;
  const mode=document.getElementById('s10-mode').value;
  const MBps=800; // sustained disk throughput, generous
  const fmt=s=>{ if(s<1) return '< 1 second';
    if(s<60) return s.toFixed(0)+' seconds';
    if(s<3600) return (s/60).toFixed(1)+' minutes';
    return (s/3600).toFixed(1)+' hours'; };
  let o='';
  if(mode==='custom'){
    const secs=(gb*1024)/MBps;
    o='Custom encryptor — every file read, encrypted and written back\\n'+
      '─'.repeat(60)+'\\n\\n'+
      '  data to process   '+gb+' GB\\n'+
      '  disk throughput   ~'+MBps+' MB/s\\n\\n'+
      '  TIME  '+fmt(secs)+'\\n\\n'+
      'Every byte crosses the disk twice. This is the window in which\\nthe activity is visible.';
  } else if(mode==='fresh'){
    const secs=(gb*1024)/MBps;
    o='Volume not previously encrypted — full encryption pass required\\n'+
      '─'.repeat(60)+'\\n\\n'+
      '  data to process   '+gb+' GB\\n'+
      '  disk throughput   ~'+MBps+' MB/s\\n\\n'+
      '  TIME  '+fmt(secs)+'\\n\\n'+
      'Comparable to the custom encryptor, because the same amount of\\ndata has to be transformed. '+
      'Setup work is also needed first.';
  } else {
    o='Volume already encrypted — only the protector is swapped\\n'+
      '─'.repeat(60)+'\\n\\n'+
      '  data to process   0 GB          ← the volume is not touched\\n'+
      '  key layer rewritten   a few kilobytes\\n\\n'+
      '  TIME  < 1 second\\n\\n'+
      'The '+gb+' GB underneath is already encrypted and stays exactly as it\\nis. Only the small '+
      'layer protecting the master key is rewritten.\\n\\n'+
      'Same outcome for the owner. Roughly '+fmt((gb*1024)/MBps)+' less work.';
  }
  document.getElementById('s10-out').textContent=o;
}
['s10-size','s10-mode'].forEach(id=>document.getElementById(id).addEventListener('input',s10run));
s10run();
</script>""",
 prev=("07-key-models.html","Key models"), nxt=("09-telling-them-apart.html","Telling them apart"))


# ===========================================================================
# 09 — TELLING THEM APART
# ===========================================================================
build("09-telling-them-apart.html", "09", "Putting it together · 09",
 "Telling them apart",
 "Everything so far, applied backwards. Given an encrypted file and nothing else, what can you "
 "work out about the scheme that produced it?",
 """
<h2>What the output reveals</h2>
<p>Each design decision leaves a trace in the result. You cannot read the data, but you can often
describe the scheme quite precisely.</p>

<table>
<tr><th>Observation</th><th>What it indicates</th></tr>
<tr><td>Output the same size as the original</td><td>Stream cipher, or a counter-based mode</td></tr>
<tr><td>Size rounded up to a multiple of 16</td><td>Block cipher with padding — CBC or ECB</td></tr>
<tr><td>Repeating 16-byte blocks</td><td><strong>ECB.</strong> Structure is leaking</td></tr>
<tr><td>A consistent extra 16 bytes</td><td>An authentication tag — an AEAD mode</td></tr>
<tr><td>A 256 or 512-byte high-entropy tail</td><td>An RSA-wrapped key (2048 or 4096-bit)</td></tr>
<tr><td>A 32-byte tail</td><td>An elliptic-curve public key or shared secret</td></tr>
<tr><td>Tails identical across files</td><td><strong>Session key</strong> — one key for the host</td></tr>
<tr><td>Tails all different</td><td><strong>Per-file keys</strong></td></tr>
<tr><td>Entropy high throughout</td><td>Full encryption</td></tr>
<tr><td>Entropy high then low</td><td>Header-only</td></tr>
<tr><td>Entropy alternating</td><td>Intermittent bands</td></tr>
</table>

<div class="sim">
  <div class="sim-head"><b>Simulation · identify the scheme</b><span>five questions</span></div>
  <div class="sim-body">
    <p id="s11-q" style="font-weight:600"></p>
    <div class="out tight" id="s11-ev" style="min-height:90px"></div>
    <div class="row" id="s11-opts"></div>
    <div class="out" id="s11-fb" style="min-height:20px"></div>
    <div class="row"><button id="s11-next">Next question</button>
      <button class="ghost" id="s11-restart">Start over</button>
      <span class="stat" id="s11-score"></span></div>
  </div>
</div>

<h2>Two traps</h2>

<h3>High entropy does not mean encrypted</h3>
<p>JPEG images score around 7.9, MP4 video around 8.0, ZIP archives similarly. Compression produces
evenly distributed bytes for the same reason encryption does. Judging on entropy alone marks every
photograph and video as encrypted.</p>
<p>What separates them is <strong>structure</strong>. A JPEG begins with a recognisable header. If a
file claims to be a JPEG and that header is intact, it is almost certainly just a photograph. If
the header is gone and the body is high-entropy, something has been done to it.</p>

<h3>High entropy does not mean secure</h3>
<p>AES-ECB scores near the maximum and leaks the picture straight through, as you saw in
<a href="03-modes.html">module 03</a>. Entropy measures how evenly bytes are distributed. It cannot
see repetition at block level, which is precisely what breaks ECB. The measurement that catches it
is distinct block count, not entropy.</p>

<div class="note">
<p><b>The habit worth forming.</b> Entropy is one measurement among several, and on its own it is
the weakest of them. Size relationships, block repetition, header integrity and the shape of any
trailing data each say something entropy cannot.</p>
</div>

<h2>Where to go next</h2>
<p>You now have the concepts. If you want the underlying cryptography in more depth, the standard
references are <em>Serious Cryptography</em> by Jean-Philippe Aumasson for the algorithms themselves,
and the published threat intelligence writeups from vendors for how specific families combine them.</p>
""",
 sim="""<script>
const Q=[
 {q:'A file is 40,960 bytes. The original was 40,953 bytes. What does the size tell you?',
  e:'original    40,953 bytes\\nencrypted   40,960 bytes\\ndifference       +7 bytes\\n\\n40,960 ÷ 16 = 2,560 exactly',
  o:['A stream cipher','A block cipher with padding','An authentication tag','Header-only encryption'],
  a:1,
  why:'The output is an exact multiple of 16 and grew by just enough to reach it. That is block '+
      'padding — CBC or ECB. A stream cipher would have left the size unchanged.'},
 {q:'Scanning the ciphertext, the same 16 bytes appear 340 times. What does that mean?',
  e:'block 0x0000  a3 f1 09 7c 22 be 40 15 …\\nblock 0x0110  a3 f1 09 7c 22 be 40 15 …  ← identical\\nblock 0x0230  a3 f1 09 7c 22 be 40 15 …  ← identical\\n\\n340 repeats of one block',
  o:['Normal for any cipher','The file was encrypted twice','ECB mode','A corrupted file'],
  a:2,
  why:'Identical ciphertext blocks mean identical plaintext blocks. Only ECB has that property, '+
      'because it encrypts each block independently. Structure is leaking.'},
 {q:'Five encrypted files each end with a 32-byte high-entropy tail, and all five tails differ. What is the key model?',
  e:'invoice.locked   tail 3f8a…c412   (32 bytes)\\nledger.locked    tail 91b0…7ee3   (32 bytes)\\ncontract.locked  tail 04dd…a180   (32 bytes)\\n\\nall distinct',
  o:['One session key for the host','Per-file keys','No encryption key at all','RSA-4096 wrapping'],
  a:1,
  why:'Different tails mean different key material per file. The 32-byte size points to elliptic '+
      'curve rather than RSA — an RSA-wrapped key would be 256 or 512 bytes.'},
 {q:'A file scores 7.98 entropy. Its name ends .jpg and it starts with FF D8 FF E0 … JFIF. Encrypted?',
  e:'entropy   7.98 / 8.000\\nheader    ff d8 ff e0 00 10 4a 46 49 46   |......JFIF|\\nname      holiday.jpg',
  o:['Yes — the entropy is very high','No — the header is intact and matches','Cannot tell from this','Only the header is encrypted'],
  a:1,
  why:'JPEG is compressed, so high entropy is expected and normal. The JFIF header is present and '+
      'matches the extension. This is simply a photograph.'},
 {q:'Entropy measured across a large file alternates: high, low, high, low, evenly throughout. Which pattern?',
  e:'entropy profile, per slice\\n\\n████····████····████····████····████····████····\\n\\nhigh ≈ 7.9   low ≈ 4.2',
  o:['Full encryption','Header-only','Intermittent bands','Distributed chunks'],
  a:2,
  why:'Regular alternation throughout is intermittent encryption. Header-only would be high at the '+
      'start then flat. Distributed chunks would show high regions only at the start, middle and end.'}
];
let qi=0, score=0, answered=false;
function s11draw(){
  const q=Q[qi];
  document.getElementById('s11-q').textContent='Question '+(qi+1)+' of '+Q.length+' — '+q.q;
  document.getElementById('s11-ev').textContent=q.e;
  const box=document.getElementById('s11-opts'); box.innerHTML='';
  q.o.forEach((t,i)=>{
    const b=document.createElement('button'); b.className='ghost'; b.textContent=t;
    b.addEventListener('click',()=>{
      if(answered) return; answered=true;
      const ok=(i===q.a);
      if(ok) score++;
      document.getElementById('s11-fb').innerHTML =
        (ok?'<b class="c-plain">Correct.</b> ':'<b class="c-cipher">Not quite.</b> The answer is “'+q.o[q.a]+'”. ')+q.why;
      document.getElementById('s11-score').textContent='score '+score+' / '+Q.length;
    });
    box.appendChild(b);
  });
  document.getElementById('s11-fb').textContent='';
  answered=false;
}
document.getElementById('s11-next').addEventListener('click',()=>{
  if(qi<Q.length-1){ qi++; s11draw(); }
  else { document.getElementById('s11-fb').innerHTML =
    '<b>Finished.</b> Final score '+score+' of '+Q.length+
    '. Every one of these was answerable from the output alone — no key, no sample, no tooling.'; }
});
document.getElementById('s11-restart').addEventListener('click',()=>{ qi=0;score=0;s11draw();
  document.getElementById('s11-score').textContent=''; });
s11draw();
</script>""",
 prev=("08-os-native.html","OS-native encryption"))

print("built: 08, 09")
