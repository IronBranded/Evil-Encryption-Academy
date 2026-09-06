"""Page content for the Evil Encryption Academy. Run engine.py to build."""
from engine import build
from svg_diagrams import *

# The reading order. Previous/next links are derived from this, so the chain
# cannot break when modules are renumbered — which it did, twice, when each
# page carried its own hand-written links.
ORDER = [
    ("index.html",                  "Overview"),
    ("01-what-encryption-is.html",  "What encryption is"),
    ("02-keys-and-randomness.html", "Keys and randomness"),
    ("03-hashing-and-integrity.html", "Hashing and integrity"),
    ("04-symmetric.html",           "Symmetric encryption"),
    ("05-modes.html",               "Modes of operation"),
    ("06-asymmetric.html",          "Asymmetric encryption"),
    ("07-implementation.html",      "Where the cryptography runs"),
    ("08-hybrid.html",              "The hybrid scheme"),
    ("09-coverage.html",            "How much gets encrypted"),
    ("10-key-models.html",          "Key models"),
    ("11-os-native.html",           "OS-native encryption"),
    ("12-hypervisor.html",          "Hypervisor encryption"),
    ("13-telling-them-apart.html",  "Telling them apart"),
    ("reference.html",              "Reference"),
]
_POS = {f: i for i, (f, _) in enumerate(ORDER)}

COUNT = 0
def page(fn, *a, **k):
    global COUNT
    COUNT += 1
    i = _POS[fn]
    if i > 0:
        k["prev"] = ORDER[i - 1]
    if i < len(ORDER) - 1:
        k["nxt"] = ORDER[i + 1]
    return build(fn, *a, **k)


# ===========================================================================
page("index.html", "index", "Evil Encryption Academy",
 "Encryption, and how ransomware uses it",
 "Ransomware is an applied cryptography problem wearing a Windows costume. This site explains the "
 "encryption itself — the types, how each works, how ransomware combines them, and how to tell "
 "the schemes apart. Eleven modules, each with a working simulation.",
 """
<div class="hero-vis">
  <div><canvas id="h-src" width="150" height="112" aria-hidden="true"></canvas>
    <p class="cap">original</p></div>
  <div><canvas id="h-ecb" width="150" height="112" aria-hidden="true"></canvas>
    <p class="cap c-cipher">AES-ECB — leaks</p></div>
  <div><canvas id="h-cbc" width="150" height="112" aria-hidden="true"></canvas>
    <p class="cap c-plain">AES-CBC — opaque</p></div>
</div>
<p class="stat" id="h-desc">The same image under real AES-256, twice, with the same key. Only the
mode differs — and one of them leaves the picture perfectly readable.</p>
<p class="sr" id="h-a11y" role="status"></p>

<h2>Why encryption is the whole story</h2>
<p>Strip away the delivery, the extortion and the branding, and every ransomware family reduces to
a handful of cryptographic decisions. Which cipher encrypts the data. Which one protects the key.
How much of each file gets touched. Whether one key is used or thousands.</p>
<p>Those four decisions determine everything that can be observed from outside and everything the
victim experiences. Learn them and the families stop looking like a hundred separate threats and
start looking like a small number of recurring designs, assembled from parts you can name.</p>
<p>None of those parts are unusual. The same hybrid construction that locks a file server also
secures your banking session and signs your software updates. What changes is not the mathematics
but who holds the key — which is why this site treats encryption as a neutral mechanism and spends
its time on how the mechanisms fit together.</p>

<h2>How the course is arranged</h2>
<p>Three groups, building on each other.</p>

<table>
<tr><th>#</th><th>Module</th><th>The idea</th></tr>
<tr><td colspan="3"><strong>Foundations</strong> — the vocabulary everything else assumes</td></tr>
<tr><td>01</td><td><a href="01-what-encryption-is.html">What encryption is</a></td><td>Four operations people confuse, and the one that actually locks something</td></tr>
<tr><td>02</td><td><a href="02-keys-and-randomness.html">Keys and randomness</a></td><td>Where keys come from, and why that origin decides everything</td></tr>
<tr><td>03</td><td><a href="03-hashing-and-integrity.html">Hashing and integrity</a></td><td>Proving data has not changed, which is a different problem from hiding it</td></tr>
<tr><td colspan="3"><strong>The two families</strong> — how the ciphers themselves work</td></tr>
<tr><td>04</td><td><a href="04-symmetric.html">Symmetric encryption</a></td><td>One key, enormous speed, and the two cipher designs</td></tr>
<tr><td>05</td><td><a href="05-modes.html">Modes of operation</a></td><td>Where a correct cipher still produces a broken result</td></tr>
<tr><td>06</td><td><a href="06-asymmetric.html">Asymmetric encryption</a></td><td>Two keys, tiny capacity, and why that is enough</td></tr>
<tr><td colspan="3"><strong>Ransomware encryption</strong> — how those parts get assembled</td></tr>
<tr><td>07</td><td><a href="08-hybrid.html">The hybrid scheme</a></td><td>The construction behind essentially every family</td></tr>
<tr><td>08</td><td><a href="09-coverage.html">How much gets encrypted</a></td><td>Full, header-only, intermittent, chunked</td></tr>
<tr><td>09</td><td><a href="10-key-models.html">Key models</a></td><td>One key for everything, or one key per file</td></tr>
<tr><td>10</td><td><a href="11-os-native.html">OS-native encryption</a></td><td>When the operating system does the encrypting</td></tr>
<tr><td colspan="3"><strong>Putting it together</strong></td></tr>
<tr><td>11</td><td><a href="13-telling-them-apart.html">Telling them apart</a></td><td>Identifying a scheme from its output alone</td></tr>
<tr><td>—</td><td><a href="reference.html">Reference</a></td><td>Every term, constant and number in one place</td></tr>
</table>

<h2>What you will be able to do</h2>
<ul>
  <li>Explain the difference between encoding, hashing, encryption and signing, and why only one of them hides anything</li>
  <li>Describe where a key comes from, and why a key derived from a timestamp is a different situation from one drawn from a secure generator</li>
  <li>Explain what AES and ChaCha20 actually do to bytes, round by round</li>
  <li>Say why the mode of operation matters more than the choice of cipher, and show a case where a correct cipher leaks the plaintext</li>
  <li>Explain why RSA and elliptic curves cannot encrypt a hard drive, and what they are genuinely for</li>
  <li>Describe the hybrid scheme end to end and name every property that makes it effective</li>
  <li>Recognise full, header-only, intermittent and chunked encryption from the shape of the output</li>
  <li>Work out a scheme's design from an encrypted file, with no key and no sample of the software</li>
</ul>

<div class="note">
<p><b>Concepts, not operations.</b> This site explains how encryption schemes work and how to
recognise them. It contains no encryption tooling, no malware and no operational procedures. The
simulations run entirely in your browser using the standard Web Crypto API, and every key is fixed
and printed on screen — nothing here is secret and nothing is irreversible.</p>
</div>

<h2>Start</h2>
<p>The modules assume the ones before them, so the order is the argument. If you already know the
foundations, module 09 is where the ransomware-specific material begins.</p>
<p style="margin-top:20px"><a href="01-what-encryption-is.html"><button>Begin with module 01</button></a></p>
""",
 sim="""<script>
async function heroDraw(){
  const w=150,h=112, dark = isDark();
  const src=document.getElementById('h-src'); if(!src) return;
  const sc=src.getContext('2d');
  const bg = dark ? '#14181C' : '#FCFCFA', fg = dark ? '#E7EAED' : '#191D21';
  sc.fillStyle=bg; sc.fillRect(0,0,w,h);
  sc.fillStyle=fg; sc.fillRect(42,50,66,48);
  sc.lineWidth=10; sc.strokeStyle=fg;
  sc.beginPath(); sc.arc(75,50,21,Math.PI,0); sc.stroke();
  sc.fillStyle=bg; sc.beginPath(); sc.arc(75,68,7,0,Math.PI*2); sc.fill();
  sc.fillRect(71,68,8,18);
  const img=sc.getImageData(0,0,w,h), n=w*h, pad=(16-(n%16))%16;
  const gray=new Uint8Array(n+pad);
  for(let i=0;i<n;i++) gray[i]=img.data[i*4];
  const k=await demoKeyBytes('hero');
  const ecb=await aesECB(gray,k), cbc=await aesCBC(gray,k,new Uint8Array(16));
  const paint=(id,d)=>{const c=document.getElementById(id),x=c.getContext('2d');
    const o=x.createImageData(w,h);
    for(let i=0;i<n;i++){o.data[i*4]=o.data[i*4+1]=o.data[i*4+2]=d[i];o.data[i*4+3]=255;}
    x.putImageData(o,0,0);};
  paint('h-ecb',ecb); paint('h-cbc',cbc);
  const total=Math.floor(gray.length/16);
  describe('h-a11y','Three images. The original shows a padlock. Encrypted with AES in ECB mode '+
    'the padlock is still clearly visible, because only '+distinctBlocks(ecb)+' of '+total+
    ' blocks are distinct. Encrypted with AES in CBC mode it is unreadable noise, with all '+
    distinctBlocks(cbc)+' blocks distinct.');
}
heroDraw();
document.addEventListener('themechange', heroDraw);
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', heroDraw);
</script>""")


# ===========================================================================
page("01-what-encryption-is.html", "01", "Foundations · 01",
 "What encryption is",
 "Four operations routinely get called encryption and only one of them is. Getting them apart is "
 "the most useful thing on this site, because every later idea depends on the distinction.",
 """
<h2>Four operations, one of which hides things</h2>
<table>
<tr><th></th><th>What it does</th><th>Reversible?</th><th>Needs a key?</th><th>Hides content?</th></tr>
<tr><td><strong>Encoding</strong></td><td>Changes representation for transport</td><td>Yes, by anyone</td><td>No</td><td>No</td></tr>
<tr><td><strong>Hashing</strong></td><td>Produces a fixed-size fingerprint</td><td><strong>Never</strong></td><td>No</td><td>Not its job</td></tr>
<tr><td><strong>Signing</strong></td><td>Proves who produced something</td><td>Verifiable, not reversible</td><td>Yes</td><td>No</td></tr>
<tr><td><strong>Encryption</strong></td><td>Makes data unreadable without a key</td><td>Yes, with the key</td><td><strong>Yes</strong></td><td><strong>Yes</strong></td></tr>
</table>

<h3>Encoding is not encryption</h3>
<p>Base64, hexadecimal, URL encoding and percent-encoding all change how data is <em>written</em>
without changing what it <em>is</em>. There is no key. Anyone can decode them, which is the point —
they exist so binary data can travel through channels that only accept text.</p>
<p>When base64 appears in a ransom note or attached to an encrypted file, it is being used for
storage, not protection. Something has usually already been encrypted, and base64 is only the
envelope it travels in.</p>

<h3>Hashing is not encryption</h3>
<p>A hash function takes input of any length and produces a fixed-size output — 32 bytes for
SHA-256, regardless of whether you fed it a word or a four-gigabyte video. That alone tells you the
original cannot be recovered from it: you cannot fit four gigabytes into 32 bytes.</p>
<p>Hashes identify and verify. They never conceal. Module 03 covers them properly, including the
cases where a hash <em>is</em> part of an encryption scheme.</p>

<h3>Signing is not encryption either</h3>
<p>A signature proves that a particular private key was involved in producing something, and that
it has not changed since. It answers "who made this and is it intact", not "can anyone read it".
Signed data is usually still perfectly readable — a signed software update is not a secret.</p>
<p>The confusion arises because signing uses the same key pairs as asymmetric encryption, run in
the opposite direction. Module 06 covers why that works.</p>

<h3>Encryption is not damage</h3>
<p>This one matters most when explaining an incident to someone who is not technical. An encrypted
file is completely intact. Every byte of the original is recoverable given the key. Nothing was
deleted, nothing was corrupted — a reversible transformation was applied, and it runs backwards.</p>
<p>The distinction is not pedantic. "Your data is destroyed" and "your data is intact but locked"
describe different situations and lead to different decisions.</p>

<div class="sim">
  <div class="sim-head"><b>Simulation · the three transforms</b><span>Web Crypto, real AES-256</span></div>
  <div class="sim-body">
    <p>Type anything. Each transform runs on the same input, then each is asked to reverse.</p>
    <div class="row"><input type="text" id="s1-in" value="Transfer 48200.00 to account 4417"
      aria-label="Text to transform"></div>
    <div class="row"><button id="s1-go">Transform</button>
      <button class="ghost" id="s1-rev">Try to reverse each</button></div>
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

<p>Notice the hash length never changes no matter how much you type. That is the property that
makes reversal impossible, and it is visible directly.</p>

<h2>What a cipher actually is</h2>
<p>A cipher is a pair of functions. One takes a key and a message and produces ciphertext. The
other takes the same key (or its partner) and the ciphertext, and returns the message. That is the
whole contract.</p>
<div class="out tight">encrypt(key, plaintext)  → ciphertext
decrypt(key, ciphertext) → plaintext</div>
<p>Everything interesting in cryptography is about how those two functions are constructed so that
without the key, the second one is not merely difficult but computationally hopeless.</p>

<h3>The security lives in the key, not the algorithm</h3>
<p>This principle is old enough to have a name — Kerckhoffs's principle, stated in 1883 — and it
governs how every modern cipher is designed. A cryptosystem should remain secure even if everything
about it except the key is public knowledge.</p>
<p>AES is public. Its specification is a free download; its reference implementations are on
GitHub; the exact sequence of operations is in this course. None of that helps you read AES
ciphertext, because none of it is the secret. The key is.</p>
<p>This has a direct consequence for ransomware. You can obtain the malware, disassemble it
completely, and understand every instruction — and still not be able to decrypt a single file.
The algorithm was never the secret. Understanding the software tells you <em>how</em> the scheme
works, which is exactly what this course teaches, and it does not hand you the key.</p>

<div class="note">
<p><b>The practical version.</b> When you read that a family "uses AES-256", you have learned
something about the design and nothing about whether anything can be recovered. Recovery depends on
where the key came from and where it went — the subject of modules 02 and 10.</p>
</div>

<h2>XOR: the operation underneath everything</h2>
<p>XOR compares two bits and returns 1 when they differ. It is the simplest operation in
cryptography and the one every cipher on this site eventually performs.</p>

""" + xor_diagram() + """

<p>The property that matters is that <strong>XOR is its own inverse</strong>. Apply the same key
twice and you are back where you started. Encryption and decryption become the same operation,
which is why stream ciphers need no separate decryption routine at all.</p>

<div class="sim">
  <div class="sim-head"><b>Simulation · XOR is its own inverse</b><span>watch it undo itself</span></div>
  <div class="sim-body">
    <div class="row"><input type="text" id="s2-in" value="CONFIDENTIAL" aria-label="Text to XOR"></div>
    <div class="row"><label for="s2-k">Key byte</label>
      <input type="range" id="s2-k" min="1" max="255" value="90" style="flex:1">
      <span class="stat" id="s2-kv">0x5A</span></div>
    <div class="out tight" id="s2-out"></div>
    <p class="stat">A single repeating key byte is the weakest possible cipher — 255 guesses breaks
    it, and you can check each guess by looking for readable text.</p>
  </div>
</div>

<h3>Why that toy is not a real cipher</h3>
<p>The simulation above uses one key byte repeated forever. That fails immediately for two reasons,
and understanding both explains what real ciphers must provide.</p>
<ul>
  <li><strong>The key space is tiny.</strong> 256 possibilities is not a search, it is a glance.
      A real key has 2<sup>256</sup> possibilities.</li>
  <li><strong>The key repeats.</strong> Even with a longer key, repetition leaks structure —
      identical plaintext at the same key offset produces identical ciphertext, which is exactly
      the flaw that breaks ECB mode in module 05.</li>
</ul>
<p>Real ciphers fix both by generating a keystream as long as the message, which never repeats,
derived from a key large enough that guessing is hopeless. AES and ChaCha20 differ only in how
they generate that stream — the combining step is still XOR.</p>

<div class="note">
<p><b>Where this is heading.</b> A file that has been base64-encoded looks scrambled and is
trivially readable. A file that has been hashed is gone. A file that has been encrypted is
perfectly intact and unreadable. Only the third produces the situation ransomware depends on: the
data still exists, and access to it is controlled entirely by who holds the key.</p>
</div>
""",
 sim="""<script>
const S1KEY = (async()=>await demoKeyBytes())();
async function s1run(){
  const v = document.getElementById('s1-in').value;
  const k = await S1KEY;
  document.getElementById('s1-b64').textContent = btoa(unescape(encodeURIComponent(v)));
  document.getElementById('s1-sha').textContent = hex(await crypto.subtle.digest('SHA-256', bytes(v)));
  const ct = await aesCBC(bytes(v), k, new Uint8Array(16));
  document.getElementById('s1-aes').textContent = hex(ct);
  document.getElementById('s1-key').textContent = 'demo key (public, fixed): ' + hex(k).slice(0,32) + '…';
}
async function s1rev(){
  const v = document.getElementById('s1-in').value, k = await S1KEY;
  const b64 = btoa(unescape(encodeURIComponent(v)));
  let o = '';
  o += 'Base64   → ' + decodeURIComponent(escape(atob(b64))) + '\\n';
  o += '           reversed with no key at all. This was never protection.\\n\\n';
  o += 'SHA-256  → cannot be reversed, by anyone, ever.\\n';
  o += '           The output is 32 bytes whatever the input size, so the\\n';
  o += '           original is not in there to recover.\\n\\n';
  const iv = new Uint8Array(16);
  const ct = await aesCBC(bytes(v), k, iv);
  const kk = await aesKey(k);
  const pt = await crypto.subtle.decrypt({name:'AES-CBC', iv}, kk, ct);
  o += 'AES-256  → ' + text(pt) + '\\n';
  o += '           reversed exactly, because we hold the key. Without it this\\n';
  o += '           line is unreachable. That gap is the whole of ransomware.';
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
  const enc = a.map(b => b ^ k), dec = enc.map(b => b ^ k);
  const show = u => [...u].map(b => (b>=32&&b<127)?String.fromCharCode(b):'·').join('');
  document.getElementById('s2-out').textContent =
    'plaintext   ' + show(a)   + '\\n' +
    'XOR key     ' + show(enc) + '   ← unreadable\\n' +
    'XOR again   ' + show(dec) + '   ← back to the start';
}
document.getElementById('s2-k').addEventListener('input', s2run);
document.getElementById('s2-in').addEventListener('input', s2run);
s2run();
</script>""")


# ===========================================================================
page("02-keys-and-randomness.html", "02", "Foundations · 02",
 "Keys and randomness",
 "Every cipher on this site is public. The key is the only secret, which makes where that key came "
 "from the most consequential question you can ask about any scheme.",
 """
<h2>What a key actually is</h2>
<p>A key is a number. Not a password, not a phrase — a number, usually written as a run of bytes.
An AES-256 key is 32 bytes, which is a number between zero and roughly 1.2 × 10<sup>77</sup>.</p>
<div class="out tight">3f 8a 1c 04 9b 27 ee 51 6d 0a 44 77 c1 e9 b3 82
7a 55 20 cf 18 4e 9d 6b 03 f2 8c 31 a0 db 56 74</div>
<p>There is nothing special about that particular number. Any other 32 bytes would work equally
well. What makes it a good key is not its content but the fact that nobody else can predict it.</p>

<h2>Key size, and why the numbers stop mattering</h2>
<p>Key size determines how many values an attacker would have to try. Each additional bit doubles
that count, so the growth is not gradual — it falls off a cliff.</p>

""" + keyspace_diagram() + """

<p>A 128-bit key has about 3.4 × 10<sup>38</sup> possible values. To put that in physical terms:
if every computer on Earth tested a billion keys per second, and had been doing so since the
formation of the planet, the search would not be measurably closer to finished.</p>
<p>This is why the question "how long would it take to brute-force AES-256?" has no useful answer.
It is not a difficult problem, it is an impossible one, and no amount of hardware changes that. The
consequence is important: <strong>nobody attacks the key space.</strong> They attack how the key
was produced, stored or handled — which is the rest of this module.</p>

<table>
<tr><th>Key size</th><th>Used by</th><th>Status</th></tr>
<tr><td>56-bit</td><td>DES</td><td>Broken in practice since the 1990s</td></tr>
<tr><td>128-bit</td><td>AES-128</td><td>Considered secure</td></tr>
<tr><td>256-bit</td><td>AES-256, ChaCha20</td><td>Considered secure with margin</td></tr>
<tr><td>2048-bit</td><td>RSA</td><td>Secure; not comparable to symmetric sizes</td></tr>
<tr><td>256-bit</td><td>Elliptic curve</td><td>Roughly equal to RSA-3072</td></tr>
</table>

<div class="note">
<p><b>Do not compare key sizes across families.</b> A 256-bit AES key and a 256-bit RSA key are not
remotely comparable — RSA-256 would be broken in seconds. The numbers measure different things,
because the underlying problems are different. Asymmetric keys must be far larger to reach the same
strength, which is covered in module 06.</p>
</div>

<h2>Where keys come from</h2>
<p>This is the question that decides everything. The same AES-256 encryption can be effectively
unbreakable or trivially undone depending entirely on how the key was generated.</p>

""" + keyorigin_diagram() + """

<h3>Secure random generation</h3>
<p>A cryptographically secure pseudo-random number generator (CSPRNG) produces output that cannot
be predicted even by someone who knows the algorithm and has seen previous output. Operating
systems provide one, seeded from genuinely unpredictable physical sources — timing jitter,
interrupt patterns, hardware noise.</p>
<p>This is the correct source for an encryption key, and it is what any competent scheme uses. When
a key comes from here, there is no shortcut. The only route to the plaintext is the key itself.</p>

<h3>Ordinary random generators are not the same thing</h3>
<p>A general-purpose random function — the kind used to shuffle a list or pick a colour — is
designed to be fast and statistically even, not unpredictable. Given a few outputs, its internal
state can often be reconstructed, and once you have the state you have every value it will ever
produce.</p>
<p>The classic failure is seeding from the clock. If a key is generated from the current time in
seconds, and you know roughly when it happened, the search space collapses from 2<sup>256</sup> to
a few thousand. That is not cryptography, it is a lookup.</p>

<div class="sim">
  <div class="sim-head"><b>Simulation · predictable versus unpredictable</b><span>see the search space collapse</span></div>
  <div class="sim-body">
    <p>Both produce 32 bytes that look equally random. Only one of them is.</p>
    <div class="row">
      <label for="s-src">Key source</label>
      <select id="s-src">
        <option value="csprng">Secure random generator</option>
        <option value="time">Seeded from the clock</option>
      </select>
      <button id="s-gen">Generate a key</button>
    </div>
    <div class="out tight" id="s-key"></div>
    <div class="out" id="s-analysis"></div>
  </div>
</div>

<h3>Keys derived from passwords</h3>
<p>Sometimes a key has to come from something a human can remember. A password is not a key — it is
short, drawn from a small alphabet and often guessable — so it must be stretched into one by a
<strong>key derivation function</strong>.</p>
<p>A KDF does two things. It converts arbitrary input into a fixed-size key, and it is deliberately
slow, so that testing each guess costs real time. PBKDF2, scrypt and Argon2 are the common choices,
and they can be tuned so that a single derivation takes a noticeable fraction of a second.</p>
<div class="out tight">password  →  [ KDF, deliberately slow ]  →  256-bit key
                        ↑
                  salt + iteration count</div>
<p>The <strong>salt</strong> is a random value stored alongside the result. It ensures that two
people with the same password get different keys, which prevents an attacker precomputing a table
of answers once and reusing it against everyone.</p>
<p>A KDF cannot make a weak password strong. If the password is in a wordlist, a slow KDF only
means the attacker's list takes longer to work through. What it changes is the cost per guess, and
that is often decisive.</p>

<h2>Nonces and initialisation vectors</h2>
<p>Keys are not the only values a cipher needs. Most schemes also take a second input — called an
IV or a nonce depending on the mode — that makes each encryption unique even when the key is
reused.</p>
<table>
<tr><th></th><th>Key</th><th>IV / nonce</th></tr>
<tr><td>Secret?</td><td><strong>Yes, always</strong></td><td>No — usually stored in the open</td></tr>
<tr><td>Reusable?</td><td>Yes, across many messages</td><td><strong>Never with the same key</strong></td></tr>
<tr><td>Typical size</td><td>16 or 32 bytes</td><td>12 or 16 bytes</td></tr>
<tr><td>If it repeats</td><td>Fine, by design</td><td>Depends on the mode — sometimes catastrophic</td></tr>
</table>
<p>The rule that matters: <strong>a nonce must never repeat under the same key</strong>. It may be
public, predictable, even a simple counter — but it must be unique. Module 05 shows exactly what
breaks when this is violated, and module 11 shows a case where an apparently reused nonce is
perfectly safe because the key never repeats.</p>

<h2>Why this module exists</h2>
<p>Everything that follows assumes a key exists and is secret. That assumption is doing enormous
work, and it is the part of a real scheme most likely to be wrong.</p>
<p>When you are looking at any encryption scheme — in a product, in a protocol, or in ransomware —
the productive questions are not about the cipher. They are:</p>
<ul>
  <li>Where did the key come from, and could that source be predicted or reproduced?</li>
  <li>Was it used once, or reused across many things?</li>
  <li>Where did it go afterwards — is a copy still somewhere?</li>
  <li>Was the nonce unique for every use of that key?</li>
</ul>

<div class="note">
<p><b>The thread running through this course.</b> Ciphers are essentially never broken. Key handling
is broken constantly. When you read that some encryption scheme "was defeated", the story is
almost always about one of the four questions above and almost never about mathematics.</p>
</div>
""",
 sim="""<script>
async function keyGen(){
  const src=document.getElementById('s-src').value;
  let k, analysis;
  if(src==='csprng'){
    k = crypto.getRandomValues(new Uint8Array(32));
    analysis =
      'SOURCE   operating system secure random generator\\n\\n'+
      'Possible values   ~1.2 × 10^77\\n'+
      'Reproducible?     no — not even by the machine that made it\\n'+
      'Attack            none available. The key must be obtained, not guessed.\\n\\n'+
      'Press generate again: the result is completely different every time,\\n'+
      'and knowing this one tells you nothing about the next.';
  } else {
    // key derived from the current second - the classic weak-seeding pattern
    const secs = Math.floor(Date.now()/1000);
    k = new Uint8Array(await crypto.subtle.digest('SHA-256', bytes('seed:'+secs)));
    analysis =
      'SOURCE   SHA-256 of the current time, in seconds\\n\\n'+
      'Seed used         '+secs+'\\n'+
      'Possible values   one per second\\n'+
      'Reproducible?     yes — anyone who knows the second reproduces it exactly\\n\\n'+
      'If an attacker knows the encryption happened within a given day,\\n'+
      'the search is 86,400 candidates. A laptop finishes that instantly.\\n\\n'+
      'The bytes below look exactly as random as the secure ones. Output\\n'+
      'appearance tells you nothing about key strength.';
  }
  document.getElementById('s-key').textContent =
    hex(k).replace(/(.{32})/g,'$1\\n').trim();
  document.getElementById('s-analysis').textContent = analysis;
}
document.getElementById('s-gen').addEventListener('click', keyGen);
document.getElementById('s-src').addEventListener('change', keyGen);
keyGen();
</script>""")


# ===========================================================================
page("03-hashing-and-integrity.html", "03", "Foundations · 03",
 "Hashing and integrity",
 "Encryption answers whether anyone can read something. It says nothing about whether the data has "
 "been altered, or who produced it. Those are separate problems with separate tools.",
 """
<h2>Three properties, often confused</h2>

""" + integrity_diagram() + """

<p>Encryption alone provides <strong>confidentiality</strong> and nothing else. An attacker who
cannot read your ciphertext can still modify it, and depending on the mode, those modifications may
decrypt into something meaningful rather than obvious garbage. Detecting that requires a separate
mechanism.</p>

<h2>Hash functions</h2>
<p>A hash function takes input of any size and returns a fixed-size fingerprint. SHA-256 always
returns 32 bytes, whether you feed it one character or a terabyte.</p>
<p>Four properties make one useful for cryptography:</p>
<table>
<tr><th>Property</th><th>Means</th></tr>
<tr><td><strong>Deterministic</strong></td><td>The same input always gives the same output</td></tr>
<tr><td><strong>One-way</strong></td><td>Given the output, you cannot find the input</td></tr>
<tr><td><strong>Avalanche</strong></td><td>Changing one bit of input changes about half the output bits</td></tr>
<tr><td><strong>Collision-resistant</strong></td><td>Finding two inputs with the same output is infeasible</td></tr>
</table>

<div class="sim">
  <div class="sim-head"><b>Simulation · fixed size and avalanche</b><span>real SHA-256</span></div>
  <div class="sim-body">
    <p>Type anything, then change a single character. Watch the length stay constant and the
    output change completely.</p>
    <div class="row"><textarea id="h-in">The quick brown fox jumps over the lazy dog</textarea></div>
    <div class="out tight" id="h-out"></div>
    <p class="stat" id="h-stat"></p>
  </div>
</div>

<p>The avalanche property is what makes a hash useful for detecting change. There is no such thing
as a "close" hash — any modification, however small, produces an output that looks entirely
unrelated. You cannot tell from two hashes whether the inputs were similar.</p>

<h3>What hashes are used for</h3>
<ul>
  <li><strong>Integrity checking.</strong> Publish the hash of a file; anyone can verify their copy
      matches.</li>
  <li><strong>Identification.</strong> A hash is a compact, unique name for a piece of content.</li>
  <li><strong>Inside other constructions.</strong> Key derivation, message authentication and
      digital signatures all use hashes as a component.</li>
</ul>

<h3>What they are not used for</h3>
<p>Hashes do not hide anything. If the input space is small — a phone number, a date of birth, a
common password — anyone can hash every possibility and look yours up. Hashing is not a substitute
for encryption and never was.</p>

<h2>The problem hashes alone do not solve</h2>
<p>Publishing a hash proves integrity only if the hash itself cannot be tampered with. An attacker
who can change the file can usually change the published hash alongside it, and the check passes.</p>
<p>What is needed is a fingerprint that <strong>only someone with a key can produce</strong>. That
is a Message Authentication Code.</p>

<div class="out tight">hash:  fingerprint(data)              anyone can compute it
MAC:   fingerprint(key, data)         only a key holder can compute it</div>

<p>HMAC is the standard construction, built from an ordinary hash function plus a key. Verifying an
HMAC proves two things at once: the data has not changed, and it was produced by someone holding
the key. That second property is authenticity, and a plain hash cannot provide it.</p>

<h2>Authenticated encryption</h2>
<p>Historically, confidentiality and integrity were bolted together by hand — encrypt the data,
then MAC the result. Doing that correctly turns out to be subtle, and getting the order wrong has
produced real vulnerabilities.</p>
<p>Modern practice is to use a mode that does both in one operation. These are called
<strong>AEAD</strong> modes — Authenticated Encryption with Associated Data.</p>

<table>
<tr><th>Scheme</th><th>Built from</th><th>Overhead</th></tr>
<tr><td><strong>AES-GCM</strong></td><td>AES in counter mode + GHASH</td><td>16-byte tag</td></tr>
<tr><td><strong>ChaCha20-Poly1305</strong></td><td>ChaCha20 + Poly1305</td><td>16-byte tag</td></tr>
<tr><td><strong>AES-CCM</strong></td><td>AES counter mode + CBC-MAC</td><td>variable tag</td></tr>
</table>

<p>An AEAD mode appends an <strong>authentication tag</strong> to the ciphertext. On decryption the
tag is checked first. If it does not match, decryption fails outright rather than returning
plausible-looking garbage.</p>

<div class="note">
<p><b>Why this matters for identification.</b> A consistent 16-byte overhead beyond what padding
explains is a strong signal that an AEAD mode is in use. When you are reconciling the size of an
encrypted file against its original — a technique used throughout module 13 — the tag has to be
accounted for, or the arithmetic will not close.</p>
</div>

<h3>Why a ransomware scheme would bother</h3>
<p>Authentication seems like an odd thing for an attacker to want. Nobody is tampering with the
files. There are two practical reasons it appears anyway:</p>
<ul>
  <li><strong>It proves the decryption worked.</strong> If a victim pays, the tag check confirms the
      right key was used and the output is correct — useful for a service that has to deliver
      something that works.</li>
  <li><strong>It comes for free.</strong> Modern cryptographic libraries make AEAD the default and
      the easiest thing to call. Choosing a raw unauthenticated mode is now the harder path.</li>
</ul>

<h2>Hashes inside encryption schemes</h2>
<p>Hashes turn up throughout the schemes covered later in this course, in three distinct roles:</p>
<table>
<tr><th>Role</th><th>Example</th></tr>
<tr><td>Deriving a key from a password</td><td>PBKDF2 runs a hash many thousands of times</td></tr>
<tr><td>Deriving a key from a shared secret</td><td>The output of a key exchange is hashed into a usable key</td></tr>
<tr><td>Producing an identifier</td><td>A victim or campaign ID is often a hash of machine details</td></tr>
</table>
<p>None of these use the hash to hide anything. They use it to compress unpredictable input into a
fixed-size value with no exploitable structure — which is exactly what a key needs to be.</p>

<div class="note">
<p><b>Carry this forward.</b> When you meet a scheme in later modules, ask which of the three
properties it actually provides. Many provide only confidentiality, and that is a deliberate
choice rather than an oversight — integrity costs bytes and time, and an attacker encrypting a
file server may not care whether anyone tampers with the result.</p>
</div>
""",
 sim="""<script>
async function hashRun(){
  const v=document.getElementById('h-in').value;
  const h1=hex(await crypto.subtle.digest('SHA-256', bytes(v)));
  // flip one character to show avalanche
  const alt = v.length ? v.slice(0,-1) + String.fromCharCode(v.charCodeAt(v.length-1)^1) : 'a';
  const h2=hex(await crypto.subtle.digest('SHA-256', bytes(alt)));
  let diff=0;
  for(let i=0;i<h1.length;i++) if(h1[i]!==h2[i]) diff++;
  document.getElementById('h-out').textContent =
    'input      '+(v.length>52 ? v.slice(0,52)+'…' : v)+'\\n'+
    'SHA-256    '+h1.replace(/(.{32})/g,'$1\\n           ').trim()+'\\n\\n'+
    'one char changed\\n'+
    'SHA-256    '+h2.replace(/(.{32})/g,'$1\\n           ').trim();
  document.getElementById('h-stat').textContent =
    'input length '+v.length+' characters  ·  output length always 32 bytes  ·  '+
    diff+' of 64 hex digits differ after a one-character change';
}
document.getElementById('h-in').addEventListener('input', hashRun);
hashRun();
</script>""")


# ===========================================================================
page("04-symmetric.html", "04", "The two families · 04",
 "Symmetric encryption",
 "One key locks and unlocks. It is fast enough to encrypt an entire disk, which is why every "
 "ransomware family uses it to do the actual work on your files.",
 """
<h2>One key, both directions</h2>
<p>Symmetric encryption uses a single key for both operations, like a padlock where the same key
opens and closes it. That simplicity is where the speed comes from: a modern processor manages
somewhere between one and five gigabytes per second.</p>
<p>The obvious problem is distribution. Whoever encrypts must hold the key, and if the key stays
with the data then anyone holding the data holds the key. Ransomware borrows the solution from
asymmetric cryptography, which is what module 09 assembles.</p>

<h2>Two designs</h2>

""" + blockstream_diagram() + """

<table>
<tr><th></th><th>Block ciphers</th><th>Stream ciphers</th></tr>
<tr><td>Example</td><td>AES</td><td>ChaCha20, XChaCha20</td></tr>
<tr><td>Works on</td><td>Fixed 16-byte blocks</td><td>A keystream XORed with the data</td></tr>
<tr><td>Output size</td><td>Rounded up to a block multiple</td><td>Identical to the input</td></tr>
<tr><td>Needs padding</td><td>Yes</td><td>No</td></tr>
<tr><td>Speed comes from</td><td><strong>Hardware</strong> — AES-NI instructions</td><td><strong>Software</strong>, no special hardware</td></tr>
<tr><td>Chosen when</td><td>Running on x86 with acceleration</td><td>Cross-platform, no hardware assumptions</td></tr>
</table>

<p>That last row explains a real shift. Families written in Rust and Go — which target Windows,
Linux and hypervisors from one codebase — overwhelmingly pick ChaCha20 or its extended-nonce
variant, because it is fast everywhere without depending on CPU features that may not exist.</p>

<h2>AES, in detail</h2>
<p>AES takes 16 bytes at a time and arranges them into a 4×4 grid of bytes called the state. It
then applies a sequence of rounds — 10, 12 or 14 depending on key size — each of which performs
four operations.</p>

<table>
<tr><th>Step</th><th>What it does</th><th>Purpose</th></tr>
<tr><td><strong>SubBytes</strong></td><td>Replaces each byte using a fixed 256-entry lookup table</td><td>Non-linearity — the only step that is not a simple rearrangement</td></tr>
<tr><td><strong>ShiftRows</strong></td><td>Rotates each row of the grid by a different amount</td><td>Spreads bytes across columns</td></tr>
<tr><td><strong>MixColumns</strong></td><td>Combines the four bytes of each column</td><td>Spreads each byte's influence across the column</td></tr>
<tr><td><strong>AddRoundKey</strong></td><td>XORs in a round key</td><td>Introduces the secret</td></tr>
</table>

<p>The lookup table used by SubBytes is called the <strong>S-box</strong>, and it is a fixed public
constant. Every software AES implementation contains it, which is why its first bytes —
<code>63 7c 77 7b f2 6b 6f c5</code> — are one of the most recognisable patterns in any compiled
program that does cryptography.</p>

<h3>The key schedule</h3>
<p>AES never uses your key directly. It expands it into a series of round keys, one per round plus
one extra, through a process called the key schedule.</p>
<table>
<tr><th>Variant</th><th>Rounds</th><th>Round keys</th><th>Expanded size</th></tr>
<tr><td>AES-128</td><td>10</td><td>11</td><td>176 bytes</td></tr>
<tr><td>AES-192</td><td>12</td><td>13</td><td>208 bytes</td></tr>
<tr><td>AES-256</td><td>14</td><td>15</td><td>240 bytes</td></tr>
</table>
<p>The expansion is deterministic and reversible: given the full schedule you can recover the
original key. That has a consequence worth noting — while a cipher is running, the material sitting
in memory is not 32 bytes but 240, and it has a mathematically checkable internal structure.</p>

<h3>Hardware acceleration, and why it changed the landscape</h3>
<p>Modern x86 and ARM processors implement AES rounds as single instructions. On x86 these are
<code>AESENC</code>, <code>AESENCLAST</code>, <code>AESDEC</code> and
<code>AESKEYGENASSIST</code>, collectively called AES-NI. On ARM the equivalents are
<code>AESE</code> and <code>AESD</code>.</p>
<p>One instruction performs an entire AES round — the substitution, the row shift, the column mix
and the key XOR — in a handful of clock cycles.</p>

<table>
<tr><th>Implementation</th><th>Rough throughput per core</th><th>Contains lookup tables?</th></tr>
<tr><td>Naive software AES</td><td>~100–200 MB/s</td><td>Yes — S-box</td></tr>
<tr><td>Table-optimised software AES</td><td>~300–600 MB/s</td><td>Yes — four 1 KB T-tables</td></tr>
<tr><td><strong>AES-NI hardware</strong></td><td><strong>1–5 GB/s</strong></td><td><strong>No — none at all</strong></td></tr>
</table>

<p>Three consequences follow, and they matter well beyond raw speed.</p>
<ul>
  <li><strong>Encrypting a large disk became practical.</strong> At 200 MB/s a terabyte takes about
      an hour and a half. At 3 GB/s it takes under six minutes. Full-volume encryption stopped
      being a slow, conspicuous operation and became a fast one.</li>
  <li><strong>The recognisable constants disappear.</strong> A hardware implementation has no
      S-box and no T-tables, because the substitution lives in the silicon. The single most
      identifiable marker of software AES is simply absent.</li>
  <li><strong>A timing side channel closes.</strong> Table-based AES looks up memory at addresses
      that depend on the key, which can leak through cache timing. Hardware AES does not touch
      tables, so that class of attack does not apply.</li>
</ul>

<div class="note">
<p><b>Why this matters for identification.</b> Module 13 leans on recognisable constants, and this
is the case where they are not there. A program using AES-NI performs perfectly ordinary AES-256
and contains none of the byte patterns that would normally reveal it. The absence of an S-box is
not evidence that AES is absent.</p>
</div>

<h2>ChaCha20, in detail</h2>
<p>ChaCha20 never touches your data until the final step. It builds a 512-bit internal state from
four components, stirs it, and the stirred result becomes keystream.</p>

<div class="out tight">state = [ constant (16 bytes) ][ key (32 bytes) ][ counter (4) ][ nonce (12) ]
                 ↓
        20 rounds of add, XOR, rotate
                 ↓
        64 bytes of keystream  ⊕  plaintext  =  ciphertext</div>

<p>The constant is the ASCII string <code>expand 32-byte k</code>. It is fixed, public and required
by the algorithm, which makes it the single most recognisable marker of this cipher family in any
compiled program.</p>

<p>The stirring is built from one operation repeated — the <strong>quarter round</strong> — which
does nothing but addition, XOR and bit rotation on four state words. Twenty rounds of that, applied
in alternating column and diagonal patterns, is the entire cipher.</p>

<h3>Why this design won out</h3>
<ul>
  <li><strong>Fast without hardware.</strong> Addition, XOR and rotation are fast on every
      processor ever made.</li>
  <li><strong>No timing side channels.</strong> AES table lookups touch memory at key-dependent
      addresses, which can leak through cache timing. ChaCha20 has no tables.</li>
  <li><strong>Simple to implement correctly.</strong> Fewer moving parts means fewer
      opportunities to introduce a subtle bug.</li>
</ul>

<h3>XChaCha20 and the extended nonce</h3>
<p>A variant with a 24-byte nonce rather than 8 or 12. That sounds like a detail and is actually
the reason this cipher dominates modern cross-platform encryption.</p>

<p>Recall the rule from module 02: a nonce must never repeat under the same key. There are two ways
to guarantee that. Keep a counter, which requires state and coordination. Or pick at random and
rely on the space being large enough that a collision never happens.</p>

<table>
<tr><th>Nonce size</th><th>Space</th><th>Safe to pick at random?</th></tr>
<tr><td>8 bytes (original Salsa/ChaCha)</td><td>1.8 × 10<sup>19</sup></td><td>No — collisions become likely after billions</td></tr>
<tr><td>12 bytes (IETF ChaCha20)</td><td>7.9 × 10<sup>28</sup></td><td>Marginal at very large scale</td></tr>
<tr><td><strong>24 bytes (XChaCha20)</strong></td><td>3.9 × 10<sup>56</sup></td><td><strong>Yes, comfortably</strong></td></tr>
</table>

<p>With 24 bytes you can generate a random nonce for every file, forever, without tracking anything
and without any realistic chance of repeating one. <strong>That removes the need for coordinated
state entirely</strong> — which is precisely what you want when many threads are encrypting many
files independently, and there is nowhere sensible to keep a shared counter.</p>

<p>Internally XChaCha20 achieves this by first running a function called HChaCha20 over the key and
the first 16 bytes of the nonce, producing a derived subkey. That subkey and the remaining 8 bytes
then run ordinary ChaCha20. The extension is a wrapper, not a new cipher.</p>

<h3>XChaCha20-Poly1305</h3>
<p>Pairing XChaCha20 with the Poly1305 authenticator gives an AEAD construction — the idea from
module 03, in the form most modern software actually uses.</p>
<div class="out tight">plaintext ──[ XChaCha20, 32-byte key, 24-byte nonce ]──▶ ciphertext
                                                          +
                                          [ Poly1305 ]──▶ 16-byte tag</div>
<p>The combination is fast without hardware support, safe with random nonces at any scale, and
authenticated by default. Cryptographic libraries expose it as a single function, so it is often
the easiest correct thing to call — which is a large part of why it is chosen.</p>

<p>This matters especially for encryption targeting Linux systems and hypervisors, where the code
must run across varied hardware with no guarantee of AES acceleration. A cipher that is fast in
pure software and needs no nonce bookkeeping fits that constraint better than AES does.</p>

<div class="note">
<p><b>A caution for identification.</b> XChaCha20 uses the same <code>expand 32-byte k</code>
constant as ordinary ChaCha20. Nothing in the compiled output distinguishes them. The only
difference visible from outside is the nonce length — 24 bytes rather than 12 or 8 — which means
you determine it from the data layout, not from the code.</p>
</div>

<h2>Hardware acceleration, in more detail</h2>
<p>The performance gap between AES and everything else is not a property of the algorithm. It is a
property of the silicon. Since roughly 2010, mainstream processors have implemented AES rounds as
single instructions.</p>
<table>
<tr><th>Instruction</th><th>Does</th></tr>
<tr><td><code>AESENC</code></td><td>One full encryption round — substitute, shift, mix, add round key</td></tr>
<tr><td><code>AESENCLAST</code></td><td>The final round, which omits column mixing</td></tr>
<tr><td><code>AESDEC</code> / <code>AESDECLAST</code></td><td>The decryption equivalents</td></tr>
<tr><td><code>AESKEYGENASSIST</code></td><td>Assists key schedule expansion</td></tr>
</table>
<p>A software AES round is roughly twenty operations plus four table lookups. In hardware it is one
instruction with fixed latency. The result is several times faster and, importantly, <strong>constant
time</strong> — the table lookups that leak timing information in software implementations do not
exist.</p>
<p>This creates a fork in the design. On a processor with these instructions, AES is the fastest
option available by a wide margin. Without them — an older CPU, an unusual architecture, or a
runtime that cannot emit those instructions — AES in software is markedly slower than ChaCha20.</p>

<div class="note">
<p><b>Why this shapes what families choose.</b> Software that must run identically on Windows,
Linux and hypervisors, compiled once, cannot assume the instructions are present. Picking ChaCha20
removes the question entirely: it is fast everywhere, with no hardware dependency and no timing
side channel. Software targeting only modern Windows hosts has no such constraint and takes the
hardware path.</p>
</div>

<h2>XChaCha20-Poly1305</h2>
<p>The combination that turns up most often in cross-platform designs, and it is worth taking apart
because the name contains three separate decisions.</p>
<table>
<tr><th>Part</th><th>Provides</th><th>Why it was chosen</th></tr>
<tr><td><strong>ChaCha20</strong></td><td>The keystream</td><td>Fast in pure software, no hardware needed, no timing leak</td></tr>
<tr><td><strong>X</strong> — extended nonce</td><td>24-byte nonce instead of 12</td><td>Random nonces become safe at scale</td></tr>
<tr><td><strong>Poly1305</strong></td><td>A 16-byte authentication tag</td><td>Detects any modification; confirms correct decryption</td></tr>
</table>

<h3>Why the longer nonce matters</h3>
<p>A nonce must never repeat under the same key. With 12 bytes there are 2<sup>96</sup> values, and
if you pick them randomly, the chance of a collision becomes non-negligible after a few billion
messages. The usual fix is a counter — but a counter requires shared state, which means tracking a
number reliably across every file, every thread and every restart.</p>
<p>XChaCha20 extends the nonce to 24 bytes, giving 2<sup>192</sup> values. At that size you can
generate a fresh nonce at random for every single file and never think about collisions again. No
counter, no shared state, no coordination between threads.</p>
<p>For software encrypting millions of files across many machines in parallel, that removes an
entire class of implementation mistake. It is a small change with a disproportionate effect on how
easy the surrounding code is to get right.</p>

<div class="out tight">ChaCha20   12-byte nonce   2⁹⁶  values   → needs a counter, needs shared state
XChaCha20  24-byte nonce   2¹⁹² values  → pick at random, forget about it</div>

<p>Internally, XChaCha20 uses the first 16 bytes of the nonce to derive a subkey, then runs ordinary
ChaCha20 with that subkey and the remaining 8 bytes. It uses the identical
<code>expand 32-byte k</code> constant, so <strong>nothing in the compiled output distinguishes the
two</strong> — only the nonce length does.</p>

<h2>What it looks like from outside</h2>

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

<p>The left histogram is spiky because English text clusters heavily — lots of lowercase letters
and spaces, nothing in the high byte values at all. The right one is flat because every byte value
now occurs about equally often.</p>

<h3>Entropy, and its limits</h3>
<p>That flatness is what an entropy score measures: how evenly the byte values are distributed,
scored from 0 to 8. Encrypted data sits near 8.0.</p>
<p>Two limits are worth internalising now, because both cause real mistakes later:</p>
<ul>
  <li><strong>Compressed data also scores near 8.0.</strong> JPEG, MP4 and ZIP all produce evenly
      distributed bytes for the same reason encryption does. Entropy cannot distinguish
      ciphertext from a photograph.</li>
  <li><strong>Small samples never reach 8.0.</strong> A 128-byte sample of perfect ciphertext
      scores about 6.55, because 128 values cannot populate 256 slots. Judging a small blob
      against 8.0 makes real ciphertext look non-random.</li>
</ul>

<div class="note">
<p><b>Encryption does not compress or shuffle.</b> It maps structured data onto output that is
statistically indistinguishable from random noise. Notice the size in the simulation: the
ciphertext is slightly larger, because a block cipher pads the input up to a multiple of 16 bytes.
That size relationship is one of the most useful identification signals there is, and module 13
uses it repeatedly.</p>
</div>
""",
 sim="""<script>
const S3KEY = (async()=>await demoKeyBytes('module-04'))();
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
</script>""")


# ===========================================================================
page("05-modes.html", "05", "The two families · 05",
 "Modes of operation",
 "AES is not broken. AES-ECB is. The mode decides whether a perfectly correct cipher produces a "
 "secure result or leaves your data readable in plain sight.",
 """
<h2>The problem a mode solves</h2>
<p>A block cipher encrypts exactly 16 bytes. Real files are larger, so something has to decide how
successive blocks relate to one another. That decision is the mode of operation, and it matters
more than which cipher you picked.</p>

""" + chaining_diagram() + """

<h2>The modes worth knowing</h2>
<table>
<tr><th>Mode</th><th>How blocks relate</th><th>Output size</th><th>Recognisable by</th></tr>
<tr><td><strong>ECB</strong></td><td>Each block encrypted independently</td><td>Padded</td><td><strong>Repeating ciphertext blocks</strong></td></tr>
<tr><td><strong>CBC</strong></td><td>Each block XORed with the previous ciphertext</td><td>Padded</td><td>16-byte IV, size a multiple of 16</td></tr>
<tr><td><strong>CTR</strong></td><td>A counter is encrypted to make a keystream</td><td>Unchanged</td><td>Same size as the original</td></tr>
<tr><td><strong>GCM</strong></td><td>CTR plus an authentication tag</td><td>+16 bytes</td><td>12-byte nonce, 16-byte tag</td></tr>
<tr><td><strong>XTS</strong></td><td>Tweaked per disk sector</td><td>Unchanged</td><td>Full-disk encryption</td></tr>
</table>

<h3>ECB — independent blocks</h3>
<p>The simplest possible arrangement, and the one you must never use. Each block goes through the
cipher on its own with no reference to any other block.</p>
<p>The consequence is direct: identical plaintext blocks always produce identical ciphertext blocks.
Any large uniform region of a file — a background, a run of zeroes, a repeated record — stays
uniform after encryption.</p>

<div class="sim">
  <div class="sim-head"><b>Simulation · the same image, two modes</b><span>real AES-256, identical key</span></div>
  <div class="sim-body">
    <p class="sr" id="s4-a11y" role="status"></p>
    <div class="grid2">
      <div><canvas id="s4-src" width="160" height="120" style="width:100%" aria-hidden="true"></canvas>
        <p class="cap">original</p></div>
      <div><canvas id="s4-ecb" width="160" height="120" style="width:100%" aria-hidden="true"></canvas>
        <p class="cap c-cipher">AES-256-ECB — still readable</p></div>
    </div>
    <div class="grid2" style="margin-top:14px">
      <div><canvas id="s4-cbc" width="160" height="120" style="width:100%" aria-hidden="true"></canvas>
        <p class="cap c-plain">AES-256-CBC — structure destroyed</p></div>
      <div><p class="stat" id="s4-stats"></p></div>
    </div>
  </div>
</div>

<p>Both panels use the same key and the same correctly-implemented AES-256. Nothing is broken
except the arrangement, and the arrangement is enough.</p>
<p>Note the entropy figures: ECB scores high <em>and is still completely broken</em>. Entropy
measures how evenly bytes are distributed. It cannot see that the same block keeps repeating, which
is exactly what leaks the picture. The measurement that catches ECB is <strong>distinct block
count</strong>.</p>

<h3>CBC — chained blocks</h3>
<p>Before encryption, each block is XORed with the previous block's ciphertext. The first block has
no predecessor, so it is XORed with an <strong>initialisation vector</strong> instead.</p>
<div class="out tight">C1 = encrypt(P1 ⊕ IV)
C2 = encrypt(P2 ⊕ C1)
C3 = encrypt(P3 ⊕ C2)   …and so on</div>
<p>Identical plaintext blocks now produce different ciphertext, because each depends on everything
before it. The IV need not be secret, but it must be unpredictable and must not repeat under the
same key — otherwise two messages beginning identically produce identical opening blocks, which
leaks exactly as much as ECB does for that prefix.</p>

<h3>Padding</h3>
<p>Because CBC and ECB work on whole blocks, the last block must be filled. The standard scheme,
PKCS#7, appends N bytes each of value N.</p>
<div class="out tight">…6f 70 65 6e | 04 04 04 04     four bytes short → four bytes of 0x04
…6f 70 65 6e 21 | 03 03 03      three bytes short → three of 0x03</div>
<p>If the message is already an exact multiple of 16, a <em>whole extra block</em> of padding is
added, so the decryptor can always remove a non-zero amount. That is why encrypted output is
sometimes 16 bytes larger than a size calculation would suggest.</p>

<h3>CTR — turning a block cipher into a stream cipher</h3>
<p>Instead of encrypting the data, CTR encrypts a counter and XORs the result with the data. The
cipher becomes a keystream generator.</p>
<div class="out tight">keystream = encrypt(nonce ‖ counter), counter incrementing
ciphertext = plaintext ⊕ keystream</div>
<p>Two useful consequences. Output is exactly the same size as input, with no padding. And any
block can be decrypted without processing the ones before it, because you can jump the counter
straight to the position you want — which makes CTR the natural choice for encrypting only parts
of a large file, the subject of module 10.</p>
<p>The danger is nonce reuse. Encrypt two different messages with the same key and counter and they
share a keystream, at which point XORing the two ciphertexts together cancels the keystream
entirely and leaves the two plaintexts combined. This is the most consequential misuse in the whole
subject.</p>

<h3>GCM — CTR with proof of integrity</h3>
<p>GCM runs CTR mode and, alongside it, computes an authentication tag over the ciphertext. On
decryption the tag is verified first; if it fails, nothing is returned. This is the AEAD idea from
module 03, applied to AES.</p>

<h3>XTS — for disks</h3>
<p>Disk encryption has an unusual constraint: every sector must be encryptable and decryptable
independently, in place, without changing size. XTS handles this by mixing the sector number into
the encryption as a tweak, so identical sectors at different positions still encrypt differently.
It is what BitLocker uses, and it appears again in module 13.</p>

<h2>The avalanche effect</h2>
<p>Change one bit of input and roughly half of every output bit changes. This is a design
requirement of any decent cipher, and it is why there is no such thing as a nearly-correct key.</p>

<div class="sim">
  <div class="sim-head"><b>Simulation · one bit in, half the output changes</b><span>AES-256-CBC</span></div>
  <div class="sim-body">
    <div class="row"><input type="text" id="s5-in" value="Transfer 1000.00 GBP to account 4417"
      aria-label="Text to encrypt"></div>
    <div class="row"><label for="s5-b">Flip bit</label>
      <input type="range" id="s5-b" min="0" max="63" value="0" style="flex:1">
      <span class="stat" id="s5-bv"></span></div>
    <div class="out tight" id="s5-out"></div>
    <p class="stat" id="s5-stat"></p>
  </div>
</div>

<div class="note">
<p><b>What this rules out.</b> There is no partial progress against a cipher. Guessing 255 of 256
key bits correctly produces output as wrong as guessing none of them. Brute force is not a strategy
against a correctly used cipher — which is why every interesting question is about how the key was
made and where it went, never about the cipher itself.</p>
</div>
""",
 sim="""<script>
function drawSource(ctx,w,h){
  const dark = isDark();
  const bg = dark ? '#14181C' : '#FCFCFA', fg = dark ? '#E7EAED' : '#191D21';
  ctx.fillStyle=bg; ctx.fillRect(0,0,w,h);
  ctx.fillStyle=fg; ctx.fillRect(46,52,68,52);
  ctx.lineWidth=11; ctx.strokeStyle=fg;
  ctx.beginPath(); ctx.arc(80,52,22,Math.PI,0); ctx.stroke();
  ctx.fillStyle=bg; ctx.beginPath(); ctx.arc(80,72,8,0,Math.PI*2); ctx.fill();
  ctx.fillRect(76,72,8,20);
}
async function s4run(){
  const w=160,h=120;
  const src=document.getElementById('s4-src'); if(!src) return;
  const sc=src.getContext('2d'); drawSource(sc,w,h);
  const img=sc.getImageData(0,0,w,h), n=w*h, pad=(16-(n%16))%16;
  const gray=new Uint8Array(n+pad);
  for(let i=0;i<n;i++) gray[i]=img.data[i*4];
  const k=await demoKeyBytes('module-05-image');
  const ecb=await aesECB(gray,k), cbc=await aesCBC(gray,k,new Uint8Array(16));
  const paint=(id,d)=>{const c=document.getElementById(id),x=c.getContext('2d');
    const o=x.createImageData(w,h);
    for(let i=0;i<n;i++){o.data[i*4]=o.data[i*4+1]=o.data[i*4+2]=d[i];o.data[i*4+3]=255;}
    x.putImageData(o,0,0);};
  paint('s4-ecb',ecb); paint('s4-cbc',cbc);
  const total=Math.floor(gray.length/16);
  document.getElementById('s4-stats').innerHTML =
    'plaintext entropy <b>'+shannon(gray).toFixed(2)+'</b><br>'+
    'ECB entropy <b>'+shannon(ecb).toFixed(2)+'</b><br>'+
    'CBC entropy <b>'+shannon(cbc).toFixed(2)+'</b><br><br>'+
    'distinct 16-byte blocks<br>ECB <b class="c-cipher">'+distinctBlocks(ecb)+'</b> of '+total+
    '<br>CBC <b class="c-plain">'+distinctBlocks(cbc)+'</b> of '+total;
  describe('s4-a11y','A padlock image encrypted twice with the same AES-256 key. Under ECB the '+
    'padlock shape remains clearly visible because only '+distinctBlocks(ecb)+' of '+total+
    ' blocks are distinct. Under CBC it is unreadable noise, with all '+distinctBlocks(cbc)+
    ' blocks distinct.');
}
s4run();
document.addEventListener('themechange', s4run);
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', s4run);

async function s5run(){
  const v=document.getElementById('s5-in').value;
  const bit=+document.getElementById('s5-b').value;
  const a=bytes(v); const b=new Uint8Array(a);
  const byteI=Math.floor(bit/8)%b.length;
  b[byteI]^=(1<<(bit%8));
  document.getElementById('s5-bv').textContent='byte '+byteI+', bit '+(bit%8);
  const k=await demoKeyBytes('module-05-av'), iv=new Uint8Array(16);
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
</script>""")


# ===========================================================================
page("06-asymmetric.html", "06", "The two families · 06",
 "Asymmetric encryption",
 "Two keys instead of one. It solves the distribution problem symmetric encryption cannot, and it "
 "is far too slow and far too small to encrypt anything substantial.",
 """
<h2>A mailbox, not a padlock</h2>
<p>Asymmetric encryption uses a matched pair of keys. The <strong>public key</strong> locks; only
the <strong>private key</strong> opens. You can publish the public half freely, because it cannot
undo its own work.</p>
<p>The everyday analogy is a mailbox with a posting slot. Anyone may post. Only the holder of the
box key can take anything out. Handing the slot to the world costs you nothing.</p>
<p>The same pair works in reverse for signatures. Something encrypted with the private key can be
opened by anyone holding the public one — useless for secrecy, but it proves the holder of the
private key produced it. Same mathematics, opposite direction, entirely different purpose.</p>

<h2>How RSA works</h2>
<p>RSA rests on a simple asymmetry: multiplying two large primes is easy, and recovering them from
the product is not.</p>
<div class="out tight">pick two primes p and q
n = p × q                    ← published, the modulus
φ = (p−1)(q−1)               ← kept secret
pick e coprime to φ          ← published, the exponent
d = e⁻¹ mod φ                ← the private key

encrypt:  c = mᵉ mod n
decrypt:  m = c\u1d48 mod n</div>
<p>Anyone with <code>n</code> and <code>e</code> can encrypt. Only someone who can compute
<code>d</code> can decrypt, and computing <code>d</code> requires <code>φ</code>, which requires
knowing <code>p</code> and <code>q</code>. Factoring a 4096-bit <code>n</code> back into its primes
is the problem nobody has solved.</p>

<div class="sim">
  <div class="sim-head"><b>Simulation · a working keypair, with tiny numbers</b><span>real RSA maths, unsafe key size</span></div>
  <div class="sim-body">
    <p>RSA with two small primes so the arithmetic is visible. The mathematics is identical to the
    real thing — only the size differs, and that size is the entire security.</p>
    <div class="row">
      <label for="s6-p">p</label><select id="s6-p"><option>11</option><option selected>17</option><option>23</option></select>
      <label for="s6-q">q</label><select id="s6-q"><option>13</option><option selected>19</option><option>29</option></select>
      <button id="s6-gen">Generate keypair</button>
    </div>
    <div class="out" id="s6-keys"></div>
    <div class="row"><label for="s6-m">Message (a number below n)</label>
      <input type="text" id="s6-m" value="42" style="max-width:120px"></div>
    <div class="out tight" id="s6-out"></div>
    <p class="stat">With p and q this small, factoring n is trivial — which is precisely why real
    keys are 2048 bits or more.</p>
  </div>
</div>

<h3>Padding is not optional</h3>
<p>Raw RSA as written above is unsafe. It is deterministic, so the same message always produces the
same ciphertext, and it has algebraic structure an attacker can exploit. Real implementations wrap
the message in a padding scheme — OAEP is the modern choice — which adds randomness and structure
checks. That padding consumes part of the available space, which leads directly to the next
section.</p>

<h2>Two hard limits</h2>

<h3>Limit one: it can barely hold anything</h3>
<p>An RSA operation cannot encrypt more data than its modulus, minus padding overhead.</p>

""" + capacity_diagram() + """

<table>
<tr><th>Key size</th><th>Modulus</th><th>Maximum plaintext with OAEP</th></tr>
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
<p>That 10 GB disk takes seconds with AES and days with RSA. Ransomware races detection; days is
not available.</p>

<h2>Elliptic curves</h2>
<p>ECC achieves comparable security with far smaller keys, by relying on a different hard problem —
given a point on a curve and a multiple of it, recovering the multiplier is infeasible.</p>

<table>
<tr><th></th><th>RSA</th><th>Elliptic curve</th></tr>
<tr><td>Typical key size</td><td>2048–4096 bits</td><td>256 bits</td></tr>
<tr><td>Stored alongside a file</td><td>256 or 512 bytes</td><td><strong>32 bytes</strong></td></tr>
<tr><td>Equivalent strength</td><td>RSA-3072</td><td>256-bit curve</td></tr>
<tr><td>Common curves</td><td>—</td><td>Curve25519, secp256k1, NIST P-256</td></tr>
</table>

<p>The practical consequence appears in module 13: a large fixed-size blob attached to an encrypted
file suggests RSA, while a small 32-byte one suggests elliptic curve. That single observation
narrows the design considerably.</p>

<h2>Key agreement</h2>
<p>Elliptic curves are usually used differently from RSA. Rather than encrypting a key directly,
two parties each combine their own private key with the other's public key and independently arrive
at the <em>same</em> shared secret — without that secret ever crossing the wire.</p>

<div class="out tight">Alice has (a_private, a_public)      Bob has (b_private, b_public)

Alice computes:  a_private × b_public  ─┐
                                        ├─→  identical shared secret
Bob computes:    b_private × a_public  ─┘

An observer sees only a_public and b_public, and cannot derive it.</div>

<p>This is Diffie-Hellman, and in its elliptic-curve form (ECDH) it underpins the most current
ransomware schemes. Module 10 shows the variant where one side generates a throwaway keypair for
every single file.</p>

<h3>A note on quantum computing</h3>
<p>Both RSA and elliptic curves rest on problems a sufficiently large quantum computer would solve
efficiently. Symmetric ciphers are far less affected — the practical impact on AES-256 is roughly
halving its effective strength, which leaves it comfortable. No machine capable of this exists
today, and post-quantum replacements are being standardised, but it is worth knowing that the two
families face very different long-term futures.</p>

<div class="note">
<p><b>Where this is heading.</b> Asymmetric cryptography cannot encrypt your files. It is far too
slow and far too small. But it can encrypt something small — like a 32-byte symmetric key — and
that turns out to be exactly enough. Module 08 puts the two halves together.</p>
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
    'never encrypt anything\\nlarger than its modulus. Real keys are 2048 or 4096 bits, which is\\n'+
    'still only a few hundred bytes.'; return; }
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
</script>""")


# ===========================================================================
page("07-implementation.html", "07", "The two families · 07",
 "Where the cryptography runs",
 "Two programs can perform identical AES-256 and be completely different artefacts. The difference "
 "is whether the cipher belongs to the operating system or to the program itself.",
 """
<h2>The same cipher, two architectures</h2>
<p>Everything so far has treated a cipher as a thing that happens. It also has to happen
<em>somewhere</em>, and there are two choices. Call the cryptography the operating system already
provides, or compile your own into the program.</p>
<p>The mathematics is identical either way. Almost everything else differs.</p>

""" + implementation_diagram() + """

<h2>Calling the operating system</h2>
<p>Every general-purpose operating system ships cryptography, because everything from disk
encryption to network security needs it. On Windows there are two generations of interface.</p>

<table>
<tr><th></th><th>CryptoAPI — legacy</th><th>CNG — current</th></tr>
<tr><td>Introduced</td><td>Windows NT era</td><td>Windows Vista</td></tr>
<tr><td>Library</td><td><code>advapi32.dll</code></td><td><code>bcrypt.dll</code>, <code>ncrypt.dll</code></td></tr>
<tr><td>Generate a key</td><td><code>CryptGenKey</code></td><td><code>BCryptGenerateSymmetricKey</code></td></tr>
<tr><td>Encrypt</td><td><code>CryptEncrypt</code></td><td><code>BCryptEncrypt</code></td></tr>
<tr><td>Random bytes</td><td><code>CryptGenRandom</code></td><td><code>BCryptGenRandom</code></td></tr>
<tr><td>Import a public key</td><td><code>CryptImportKey</code></td><td><code>BCryptImportKeyPair</code></td></tr>
</table>

<p>A program taking this route contains almost no cryptography. It contains <em>requests</em> for
cryptography — a list of function names, and code to marshal arguments across a boundary.</p>

<h3>What that buys and costs</h3>
<table>
<tr><th>Consequence</th><th>Detail</th></tr>
<tr><td>Small program</td><td>The cipher is not shipped; it is already on the machine</td></tr>
<tr><td>No cipher constants</td><td>No S-box, no T-tables, no sigma string — they live in the OS library</td></tr>
<tr><td>Correctness is borrowed</td><td>A well-tested implementation rather than a hand-rolled one</td></tr>
<tr><td>Function names are visible</td><td>The program must name what it calls in order to call it</td></tr>
<tr><td>Tied to the platform</td><td>The same code does not run on Linux or a hypervisor</td></tr>
</table>

<h2>Carrying its own</h2>
<p>The alternative is to compile a cipher implementation directly into the program. Two common
sources:</p>
<ul>
  <li><strong>A full cryptographic library</strong> such as libsodium, statically linked. Brings a
      complete, well-audited set of primitives — and considerable size.</li>
  <li><strong>A minimal implementation</strong> such as tiny-AES, a few hundred lines providing one
      cipher and nothing else. Tiny, portable, and easy to embed.</li>
</ul>
<p>Languages matter here too. Rust and Go programs are statically linked by default, so a program
written in either carries its cryptography whether or not the author thought about it.</p>

<h3>What that buys and costs</h3>
<table>
<tr><th>Consequence</th><th>Detail</th></tr>
<tr><td>Runs anywhere</td><td>No dependency on what the host provides. The same binary works across platforms</td></tr>
<tr><td>Identical behaviour everywhere</td><td>No variation between OS versions or providers</td></tr>
<tr><td>Cipher constants are present</td><td>The S-box or sigma string is inside the file</td></tr>
<tr><td>No function names to read</td><td>Nothing is requested from outside, so nothing is named</td></tr>
<tr><td>Larger program</td><td>A statically linked crypto library adds substantial size</td></tr>
</table>

<h2>The property that actually differs</h2>
<p>Strip away the practical trade-offs and one structural difference remains: <strong>whether the
key ever crosses a named boundary.</strong></p>
<p>When a program calls the operating system, the key is handed across a documented interface with
a published signature. The operation happens at a place that has a name, in a component shared by
everything on the machine. That is true regardless of anyone's intent — it is a consequence of the
architecture.</p>
<p>When the cipher is compiled in, no such boundary exists. The key is an address in memory that
gets passed to a function with no name, inside a program that never asks the system for anything.
The whole operation is internal.</p>

<div class="note">
<p><b>Why this is worth understanding conceptually.</b> It explains something that otherwise looks
inconsistent: two programs performing identical cryptography can present completely differently
from outside. One announces every cryptographic step it takes, because it has to in order to take
them. The other announces nothing. Neither is doing anything unusual — the difference is entirely
architectural.</p>
</div>

<div class="sim">
  <div class="sim-head"><b>Simulation · what ends up inside each program</b><span>same cryptography, different artefact</span></div>
  <div class="sim-body">
    <p>Both programs perform AES-256-CBC on the same file. Toggle between the two architectures.</p>
    <div class="row">
      <label for="imp-mode">Architecture</label>
      <select id="imp-mode">
        <option value="os">Calls the operating system</option>
        <option value="static" selected>Carries its own cipher</option>
        <option value="hw">Carries its own, using hardware AES</option>
      </select>
    </div>
    <div class="out tight" id="imp-out" style="min-height:200px"></div>
    <p class="stat" id="imp-note"></p>
  </div>
</div>

<h2>Which gets chosen, and why</h2>
<table>
<tr><th>Situation</th><th>Typical choice</th><th>Reason</th></tr>
<tr><td>Windows-only, older codebase</td><td>CryptoAPI or CNG</td><td>It is there, it is free, it is correct</td></tr>
<tr><td>Cross-platform target</td><td>Embedded implementation</td><td>The OS interfaces differ or do not exist</td></tr>
<tr><td>Written in Rust or Go</td><td>Embedded, by default</td><td>Static linking is the language norm</td></tr>
<tr><td>Wants ChaCha20 or XChaCha20</td><td>Embedded</td><td>Not offered by the Windows interfaces</td></tr>
<tr><td>Targeting Linux or a hypervisor</td><td>Embedded</td><td>There is no CNG to call</td></tr>
</table>

<p>That last group explains a real pattern. Software intended to run on hypervisors and Linux hosts
has no Windows cryptographic interface available, so it must carry its own — and having carried its
own, it can freely choose ciphers Windows does not offer. The platform decision and the cipher
decision are linked, which is why cross-platform designs and ChaCha20 tend to appear together.</p>

<h2>What each looks like from outside</h2>
<table>
<tr><th>Observation</th><th>Suggests</th></tr>
<tr><td>Small program, names of OS crypto functions present</td><td>Calling the operating system</td></tr>
<tr><td>Cipher constants present, no crypto function names</td><td>Embedded implementation</td></tr>
<tr><td>Neither constants nor names</td><td>Hardware AES, or the program is compressed</td></tr>
<tr><td>Constants for many ciphers at once</td><td>A whole library was linked in, most of it unused</td></tr>
</table>
<p>That last row is a genuine trap. Statically linking a full cryptographic library brings every
primitive it contains, so a program can appear to support a dozen algorithms while using one.
<strong>Presence is not use.</strong></p>
""",
 sim="""<script>
const IMP={
 os:{title:'Calls the operating system',
   size:'48 KB',
   contains:['function names it must request:',
     '    BCryptOpenAlgorithmProvider',
     '    BCryptGenerateSymmetricKey',
     '    BCryptEncrypt',
     '    BCryptGenRandom',
     '','library it depends on:','    bcrypt.dll'],
   absent:['no AES S-box','no T-tables','no cipher code at all'],
   note:'The cipher is not in this program. It is a list of requests, and the '+
        'key crosses a documented boundary to reach the code that does the work.'},
 static:{title:'Carries its own cipher',
   size:'1.4 MB',
   contains:['cipher constants compiled in:',
     '    63 7c 77 7b f2 6b 6f c5 …   AES S-box',
     '    52 09 6a d5 30 36 a5 38 …   AES inverse S-box',
     '    a5 63 63 c6 84 7c 7c f8 …   T-table',
     '','possibly also, if a whole library was linked:',
     '    "expand 32-byte k"          ChaCha20 — maybe unused'],
   absent:['no crypto function names','no dependency on OS libraries'],
   note:'The cipher is inside this program. Nothing is requested from outside, so '+
        'nothing is named — but the constants the algorithm requires are present.'},
 hw:{title:'Carries its own, using hardware AES',
   size:'52 KB',
   contains:['processor instructions, not data:',
     '    AESENC        one AES round',
     '    AESENCLAST    the final round',
     '    AESKEYGENASSIST  key expansion'],
   absent:['no AES S-box','no T-tables','no crypto function names'],
   note:'The substitution table lives in the silicon, so the program contains '+
        'neither constants nor function names. It still performs ordinary AES-256.'}
};
function impRun(){
  const m=IMP[document.getElementById('imp-mode').value];
  let o='ARCHITECTURE   '+m.title+'\\n'
        +'PROGRAM SIZE   '+m.size+'\\n'
        +'\\u2500'.repeat(58)+'\\n\\nPRESENT\\n';
  o+=m.contains.map(l=>l?'  '+l:'').join('\\n');
  o+='\\n\\nABSENT\\n'+m.absent.map(l=>'  '+l).join('\\n');
  document.getElementById('imp-out').textContent=o;
  document.getElementById('imp-note').textContent=m.note;
}
document.getElementById('imp-mode').addEventListener('change',impRun);
impRun();
</script>""")


# ===========================================================================
page("08-hybrid.html", "08", "Ransomware encryption · 08",
 "The hybrid scheme",
 "Symmetric encryption is fast but cannot protect its own key. Asymmetric encryption protects keys "
 "but cannot encrypt data. Combine them and you have the design behind essentially every family.",
 """
<h2>The combination</h2>
<p>Neither family suffices alone, but their weaknesses are complementary. The hybrid scheme uses
each for exactly what it is good at.</p>
<ol>
  <li>Generate a random symmetric key on the victim's machine</li>
  <li>Encrypt the file with it — fast, and it handles any size</li>
  <li>Encrypt <em>that key</em> with an embedded public key — slow, but it is only 32 bytes</li>
  <li>Store the wrapped key alongside the file</li>
  <li>Erase the plaintext symmetric key from memory</li>
</ol>

<p>The result is asymmetric security at symmetric speed. This is not sinister engineering — it is
precisely how TLS and PGP work. The cryptography is textbook; only the intent differs.</p>

<div class="note">
<p><b>The sentence that describes every ransomware incident:</b> the locked file and the key that
opens it are both sitting on the victim's disk. Neither helps, because the key is sealed under a
public key whose private half was never on the network.</p>
</div>

""" + lifecycle_diagram() + """

<p>Step one has a variant worth naming. The public key is usually embedded at build time, but some
designs fetch it from attacker infrastructure when they run. That trades the offline property for
flexibility — the operator can issue a fresh key per victim — at the cost of a dependency that can
be cut. Embedding is the more robust choice and the more common one.</p>

""" + lifecycle_diagram() + """

<div class="sim">
  <div class="sim-head"><b>Simulation · walk the scheme</b><span>step through it</span></div>
  <div class="sim-body">
    <div class="row"><button id="s7-next">Next step</button>
      <button class="ghost" id="s7-reset">Reset</button>
      <span class="stat" id="s7-step"></span></div>
    <div class="out tight" id="s7-out" style="min-height:230px"></div>
  </div>
</div>

<h2>Why each property matters</h2>
<table>
<tr><th>Property</th><th>Consequence</th></tr>
<tr><td>The public key is embedded at build time</td><td>No network call is needed to encrypt; the scheme works fully offline, even on an isolated machine</td></tr>
<tr><td>The private key never leaves attacker infrastructure</td><td>Examining the software reveals the entire design and nothing that opens a file</td></tr>
<tr><td>The symmetric key is random, often per file</td><td>Nothing is reusable between victims or between files</td></tr>
<tr><td>The plaintext key is erased after use</td><td>It exists only briefly, in memory, while encryption runs</td></tr>
<tr><td>The wrapped key travels with the file</td><td>Decryption is possible later without a lookup table or a database</td></tr>
</table>

<p>Each property closes a door. Together they produce a situation where the data is intact and
complete, and remains unreadable no matter how thoroughly the software is understood — which is
Kerckhoffs's principle from module 01, working for the attacker.</p>

<h3>The offline property is worth dwelling on</h3>
<p>Older designs sometimes contacted a server to fetch or register a key. That created a dependency:
block the connection and encryption fails or becomes reversible. Embedding the public key removes
the dependency entirely. There is nothing to block, because nothing needs to be sent.</p>

<h2>Where the wrapped key is stored</h2>
<p>The wrapped key has to travel with the file, or the attacker could not decrypt it later either.
Four common placements:</p>

""" + layout_diagram() + """

<p>The placement and shape of that blob is one of the most reliable ways to tell schemes apart —
the subject of module 13. A 256-byte trailing blob and a 32-byte one imply completely different
asymmetric designs.</p>

<h2>Variations you will meet</h2>
<table>
<tr><th>Variation</th><th>What changes</th></tr>
<tr><td>Wrap with RSA</td><td>The stored blob is exactly the modulus size — 256 or 512 bytes</td></tr>
<tr><td>Wrap with ECIES</td><td>An ephemeral public key is stored instead — 32 or 33 bytes</td></tr>
<tr><td>One key per host</td><td>A single wrapped blob, stored once rather than per file</td></tr>
<tr><td>One key per file</td><td>A different wrapped blob attached to every file</td></tr>
<tr><td>Key derived, not wrapped</td><td>Nothing is stored; the key is recomputed from an agreement</td></tr>
</table>
<p>That last row is the most modern variant and the subject of module 11. Nothing sensitive is
stored at all — the value written to the file is a public key, which reveals nothing on its own.</p>

<h2>A worked example</h2>
<p>Follow one 40 KB spreadsheet through the scheme, watching the sizes.</p>
<table>
<tr><th>Stage</th><th>Size</th><th>Why</th></tr>
<tr><td>Original file</td><td>40,953 bytes</td><td>—</td></tr>
<tr><td>After AES-256-CBC</td><td>40,960 bytes</td><td>Padded up to the next multiple of 16</td></tr>
<tr><td>Wrapped key appended</td><td>41,216 bytes</td><td>+256 bytes — an RSA-2048 ciphertext</td></tr>
<tr><td>Marker appended</td><td>41,232 bytes</td><td>+16 bytes of family identifier</td></tr>
</table>
<p>Total overhead 279 bytes, and every one of them is accounted for: 7 bytes of padding, 256 for
the wrapped key, 16 for the marker. When that arithmetic closes exactly, your reading of the
scheme is probably right — which is the technique module 13 builds on.</p>
<p>Note the proportions. The asymmetric operation, which is thousands of times slower per byte,
ran once on 32 bytes. The symmetric operation ran on 40,953. That ratio is the entire design.</p>

<h2>The same construction, elsewhere</h2>
<p>Nothing here is unique to ransomware. The hybrid scheme is the standard way to combine the two
families, and you rely on it constantly.</p>
<table>
<tr><th>System</th><th>Symmetric part</th><th>Asymmetric part</th></tr>
<tr><td>TLS — every HTTPS connection</td><td>AES-GCM or ChaCha20-Poly1305 for the traffic</td><td>Key agreement during the handshake</td></tr>
<tr><td>PGP / GPG email</td><td>A session key encrypts the message</td><td>That session key is wrapped per recipient</td></tr>
<tr><td>Signal and similar messengers</td><td>Per-message symmetric keys</td><td>Curve25519 agreement to derive them</td></tr>
<tr><td>Ransomware</td><td>AES or ChaCha20 on file contents</td><td>The file key is wrapped or derived</td></tr>
</table>
<p>The rows are the same construction. What differs is who holds the private half and whether you
agreed to the arrangement. That is worth stating plainly, because it explains why the scheme cannot
simply be banned or broken — it is load-bearing infrastructure for the rest of the internet.</p>

<h2>How designs got here</h2>
<p>The construction was not obvious from the start, and earlier approaches failed in instructive
ways.</p>
<table>
<tr><th>Approach</th><th>Why it failed</th></tr>
<tr><td>A single key hardcoded in the software</td><td>Extract it once and every victim is covered</td></tr>
<tr><td>A key derived from machine details</td><td>Reproducible by anyone who knows the inputs</td></tr>
<tr><td>A random key fetched from a server</td><td>Block the connection and encryption fails or is reversible</td></tr>
<tr><td>Asymmetric encryption of file contents</td><td>Far too slow and too small to be practical</td></tr>
<tr><td><strong>Hybrid with an embedded public key</strong></td><td>None of the above apply</td></tr>
</table>
<p>Each earlier design left a lever a defender could pull. The hybrid scheme removes every one of
them, which is why it converged rather than continuing to vary.</p>

<h2>What an attacker has to protect</h2>
<p>Reduced to essentials, the scheme has exactly one secret: the private key on the operator's
infrastructure. Everything else can be public without weakening it.</p>
<ul>
  <li>The malware can be obtained and disassembled — the design is not the secret</li>
  <li>The embedded public key can be extracted — it only locks</li>
  <li>The wrapped blobs can be collected — they cannot be opened</li>
  <li>The cipher and mode can be identified — they are public standards</li>
</ul>
<p>This concentration is what makes the scheme robust, and it is also its only real fragility.
Every published decryption tool in history has come from the private key being seized or leaked, or
from an implementation mistake in how the symmetric key was produced — never from the mathematics
giving way.</p>
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
    'Produced by the secure random generator built into the OS.\\nUnpredictable, and different on '+
    'every machine and often every file.\\n\\nRIGHT NOW this key exists in plain form, in memory.'},
 {t:'The file is encrypted with that symmetric key',
  b:'  invoice.xlsx  ──[ AES-256 / ChaCha20 ]──▶  ciphertext\\n\\n'+
    'Fast. Gigabytes per second. Size essentially unchanged.\\n\\n'+
    'The file is now unreadable — but the key that opens it is still\\nsitting in memory, a few '+
    'centimetres away.'},
 {t:'The symmetric key is wrapped with the embedded public key',
  b:'  file key (32 bytes) ──[ RSA / Curve25519 ]──▶ wrapped key\\n\\n'+
    'Only 32 bytes go through the slow operation, so the cost is\\ntrivial. This is the step that '+
    'makes the whole design work.\\n\\nThe wrapped key can now only be opened by the private key,\\n'+
    'which is not on this network.'},
 {t:'The wrapped key is written to disk with the file',
  b:'  [ ciphertext ........................ ][ wrapped key ]\\n\\n'+
    'It has to be stored, or the operator could not decrypt later\\neither. It is safe to leave in '+
    'the open — without the private\\nkey it is just noise.'},
 {t:'The plaintext symmetric key is erased',
  b:'  file key = 00000000 00000000 00000000 00000000\\n\\n'+
    'Overwritten in memory. The only remaining copy of that key is\\nthe wrapped one on disk, and '+
    'it cannot be opened here.\\n\\nThe file, the wrapped key and the software are all present and\\n'+
    'fully understood. None of it opens the data.'}
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
document.getElementById('s7-next').addEventListener('click',()=>{ if(s7i<S7.length-1) s7i++; s7draw(); });
document.getElementById('s7-reset').addEventListener('click',()=>{ s7i=-1; s7draw(); });
s7draw();
</script>""")


# ===========================================================================
page("09-coverage.html", "09", "Ransomware encryption · 09",
 "How much gets encrypted",
 "Encrypting an entire file server takes hours. Breaking every file on it takes minutes. Modern "
 "families exploit that gap, and it produces four patterns you can see directly in the output.",
 """
<h2>The insight being exploited</h2>
<p>You do not need to encrypt a file to make it unusable. You need to break its
<strong>structure</strong>. A database with its header and a few interior pages scrambled will not
mount. A VM disk with its descriptor damaged will not boot. An archive with its index destroyed
cannot be opened. The remaining bytes are irrelevant to whether the file works.</p>
<p>So families encrypt less and finish faster. It is a speed optimisation, and it produces four
recognisable patterns.</p>

<h2>The four patterns</h2>

""" + coverage_diagram() + """

<table>
<tr><th>Pattern</th><th>What is encrypted</th><th>Why it is chosen</th></tr>
<tr><td><strong>Full</strong></td><td>Every byte</td><td>Simple and thorough; slow on large files</td></tr>
<tr><td><strong>Header-only</strong></td><td>The first few kilobytes</td><td>Fastest possible; most formats die without a header</td></tr>
<tr><td><strong>Intermittent</strong></td><td>Alternating bands throughout</td><td>Damage spread evenly at a fraction of the I/O</td></tr>
<tr><td><strong>Distributed chunks</strong></td><td>Regions at start, middle and end</td><td>Targets header, index and trailer structures specifically</td></tr>
</table>

<h3>Two patterns at once is normal</h3>
<p>A single incident frequently shows more than one pattern, split by file size. Fast modes usually
apply only above a threshold — often 1 MB — because the bookkeeping is not worth it on a small
file. So small documents get fully encrypted while large databases get a few percent.</p>
<p>Concluding "this family uses intermittent encryption" from one sample is therefore unreliable.
The behaviour is conditional, and the condition is usually size.</p>

<div class="sim">
  <div class="sim-head"><b>Simulation · coverage explorer</b><span>real AES on the encrypted regions</span></div>
  <div class="sim-body">
    <div class="row">
      <label for="s8-mode">Pattern</label>
      <select id="s8-mode">
        <option value="full">Full encryption</option>
        <option value="header">Header-only</option>
        <option value="inter" selected>Intermittent bands</option>
        <option value="chunk">Distributed chunks</option>
      </select>
      <label for="s8-pct">Coverage</label>
      <input type="range" id="s8-pct" min="1" max="100" value="20" style="flex:1">
      <span class="stat" id="s8-pctv"></span>
    </div>
    <p class="stat">File map — each cell is a slice of the file</p>
    <div class="out tight" id="s8-map" style="font-size:15px;line-height:1.35"></div>
    <p class="stat">Entropy profile — measured per slice</p>
    <div class="out tight" id="s8-prof" style="font-size:15px;line-height:1.35"></div>
    <p class="stat" id="s8-stat"></p>
  </div>
</div>

<div class="sim">
  <div class="sim-head"><b>Simulation · entropy visualiser</b><span>real AES, 256-byte resolution</span></div>
  <div class="sim-body">
    <p>Pick a file type and watch how its entropy profile changes under each coverage pattern.
    Each column is 256 bytes.</p>
    <div class="row">
      <label for="ev-type">File type</label>
      <select id="ev-type">
        <option value="text">Plain text / CSV</option>
        <option value="pdf" selected>PDF document</option>
        <option value="exe">Executable</option>
        <option value="png">PNG image</option>
        <option value="jpg">JPEG photograph</option>
      </select>
      <label for="ev-pct">Partial coverage</label>
      <input type="range" id="ev-pct" min="2" max="60" value="20" style="flex:1">
      <span class="stat" id="ev-pv"></span>
    </div>
    <p class="sr" id="ev-a11y" role="status"></p>
    <p class="stat"><b>Original</b> — <span id="ev-l1"></span></p>
    <canvas id="ev-c1" width="512" height="70" style="width:100%" aria-hidden="true"></canvas>
    <p class="stat" style="margin-top:14px"><b>Intermittently encrypted</b> — <span id="ev-l2"></span></p>
    <canvas id="ev-c2" width="512" height="70" style="width:100%" aria-hidden="true"></canvas>
    <p class="stat" style="margin-top:14px"><b>Fully encrypted</b> — <span id="ev-l3"></span></p>
    <canvas id="ev-c3" width="512" height="70" style="width:100%" aria-hidden="true"></canvas>
    <p class="stat" style="margin-top:12px">tall and dark = high entropy · short and pale = structured data</p>
  </div>
</div>

<p>Two things are worth noticing. A JPEG or PNG already sits near the top of the scale before
anything happens to it, so full encryption barely changes its profile — for those formats the
entropy plot is close to useless and you must look at structure instead. A text file or an
executable, by contrast, changes dramatically, because there was real structure to destroy.</p>

<h2>Why the pattern is visible</h2>
<p>Encrypted bytes look random; structured bytes do not. Measuring entropy across a file in slices
rather than as a single number produces a profile, and each pattern draws a different shape.</p>

<h3>Which formats survive what</h3>
<p>Coverage percentage is only half the story. What matters is whether the encrypted regions
happen to land on the parts of the format that carry meaning.</p>
<table>
<tr><th>Format</th><th>Critical structures</th><th>Effect of header-only damage</th></tr>
<tr><td>ZIP, OOXML</td><td>Central directory, at the <em>end</em></td><td>Often survives — the index is elsewhere</td></tr>
<tr><td>JPEG</td><td>Header, then a sequential entropy-coded stream</td><td>Fatal; everything after the damage is lost</td></tr>
<tr><td>Database files</td><td>Header page plus per-page structures</td><td>Will not mount, though pages remain individually structured</td></tr>
<tr><td>VM disks</td><td>Descriptor and allocation tables</td><td>Will not boot; the guest filesystem inside is independent</td></tr>
<tr><td>Plain text, CSV, logs</td><td>None</td><td>Only the damaged region is affected</td></tr>
</table>
<p>This is why the same 3% coverage can be devastating for one format and barely noticeable for
another. Formats with no global structure degrade gracefully. Formats with a single critical
header or a sequential dependency do not.</p>

<h2>Fine striping</h2>
<p>Some designs take the idea further, encrypting very small blocks — 512 bytes — at computed
intervals across the whole file. Total coverage stays low while damage is spread everywhere.</p>
<div class="out tight">total bytes to encrypt = file size × percentage
number of blocks       = total ÷ 512
skip interval          = (file size − total) ÷ number of blocks</div>
<p>Apply that at 10% on a 40 MB file and you get 512 encrypted bytes every 4,607. Almost every
structure of any size in that file contains a stripe.</p>

<div class="note">
<p><b>Why fine striping is easy to miss.</b> If you measure entropy in 4 KB windows, each window
contains roughly 512 random bytes among 3,584 plaintext ones — about 12% random, which reads as
mostly plaintext. The file appears untouched. The pattern only becomes visible when you measure at
a finer resolution than the stripe itself, which is a general lesson: <strong>your measurement
window has to be smaller than the feature you are looking for.</strong></p>
</div>

<h2>Seeing it on real file types</h2>
<p>The pattern is easiest to believe when you watch it happen to something with recognisable
structure. Below, each strip is one file, coloured by entropy measured in 256-byte windows.</p>

<div class="sim">
  <div class="sim-head"><b>Simulation · entropy heatmap</b><span>256-byte windows, real AES-256</span></div>
  <div class="sim-body">
    <div class="row">
      <label for="ev-type">File type</label>
      <select id="ev-type">
        <option value="text">Plain text / CSV</option>
        <option value="pdf" selected>PDF document</option>
        <option value="png">PNG image</option>
        <option value="exe">Executable</option>
        <option value="zip">ZIP archive</option>
      </select>
      <label for="ev-pct">Partial coverage</label>
      <input type="range" id="ev-pct" min="2" max="60" value="15" style="flex:1">
      <span class="stat" id="ev-pctv"></span>
    </div>
    <div class="row" style="margin-bottom:18px">
      <label for="ev-file">…or use your own file</label>
      <input type="file" id="ev-file" style="font-family:var(--sans);font-size:13px">
    </div>
    <p class="stat">Original</p>
    <canvas id="ev-a" width="512" height="34" style="width:100%" aria-hidden="true"></canvas>
    <p class="stat" id="ev-as"></p>
    <p class="stat" style="margin-top:14px">Intermittently encrypted</p>
    <canvas id="ev-b" width="512" height="34" style="width:100%" aria-hidden="true"></canvas>
    <p class="stat" id="ev-bs"></p>
    <p class="stat" style="margin-top:14px">Fully encrypted</p>
    <canvas id="ev-c" width="512" height="34" style="width:100%" aria-hidden="true"></canvas>
    <p class="stat" id="ev-cs"></p>
    <p class="cap" style="margin-top:12px">
      <span class="c-plain">green</span> low entropy, structured &nbsp;·&nbsp;
      <span class="c-key">amber</span> mixed &nbsp;·&nbsp;
      <span class="c-cipher">red</span> high entropy, indistinguishable from random</p>
    <p class="sr" id="ev-a11y" role="status"></p>
    <p class="stat" style="margin-top:12px">Your file is read in the browser and never uploaded
      anywhere. Only the first 128 KB is used.</p>
  </div>
</div>

<p>Two things are worth noticing as you switch types. The <strong>original</strong> strips differ
enormously — plain text is uniformly green, a PDF is mostly green with red bands where compressed
streams sit, and a ZIP is almost entirely red before anything is encrypted at all.</p>
<p>And the <strong>fully encrypted</strong> strips are identical for every type. That is the point:
once encrypted, a text file and a ZIP archive are indistinguishable. Which also means that for the
ZIP, comparing the original and encrypted strips tells you almost nothing — the very trap module 13
returns to.</p>

<h2>Working the arithmetic</h2>
<p>Take a 40 MB database at 10% coverage with 512-byte blocks.</p>
<div class="out tight">file size              41,943,040 bytes
coverage               10%
bytes to encrypt       4,194,304
number of blocks       4,194,304 ÷ 512  =  8,192
bytes left untouched   37,748,736
skip interval          37,748,736 ÷ 8,192  =  4,608 bytes</div>
<p>So: 512 encrypted bytes, then 4,608 untouched, repeating 8,192 times across the file.</p>
<p>Now ask what that means for the format. A database page is typically 8 KB. Every single page in
that file spans at least one stripe. The file is 90% intact and completely unusable — which is
exactly the outcome the design is aiming for.</p>
<p>Change one number and the picture changes entirely. At the same 10% coverage but with 64 KB
blocks instead of 512-byte ones, the encrypted regions are 128 large contiguous chunks, and the
overwhelming majority of pages sit between them untouched. <strong>Block size matters as much as
percentage</strong>, and the two are independent.</p>

<h2>The trade-off</h2>
<p>Coverage is a dial between speed and certainty. Encrypt everything and the outcome is not in
doubt, but the operation takes hours and is visible throughout. Encrypt 1% and it finishes in
seconds, at the cost of some files remaining usable.</p>
<p>Neither end is obviously correct, which is why real families make it configurable and choose per
file size. Understanding that the dial exists is more useful than memorising any particular
setting, because the settings change between versions and the dial does not.</p>
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
  const k=await demoKeyBytes('module-08');
  for(const i of encIdx){
    if(i<0||i>=CELLS) continue;
    const ct=await aesCBC(buf.slice(i*SLICE,(i+1)*SLICE),k,new Uint8Array(16));
    buf.set(ct.slice(0,SLICE), i*SLICE);
  }
  let map='',prof=''; const bars=' ▁▂▃▄▅▆▇█';
  for(let i=0;i<CELLS;i++){
    map += encIdx.has(i) ? '█' : '·';
    const e=shannon(buf.slice(i*SLICE,(i+1)*SLICE))/8;
    prof += bars[Math.min(bars.length-1,Math.round(e*(bars.length-1)))];
  }
  document.getElementById('s8-map').innerHTML =
    '<span class="c-cipher">'+map.replace(/·/g,'</span><span class="c-plain">·</span><span class="c-cipher">')+'</span>';
  document.getElementById('s8-prof').textContent = prof;
  document.getElementById('s8-stat').textContent =
    'encrypted '+encIdx.size+' of '+CELLS+' slices  ('+(encIdx.size*SLICE/N*100).toFixed(1)+
    '% of the file)   ·   overall entropy '+shannon(buf).toFixed(3)+' / 8.000';
}
['s8-mode','s8-pct'].forEach(id=>document.getElementById(id).addEventListener('input',s8run));
s8run();

/* ---- entropy heatmap over real file structures ---- */
const EV_N = 128*1024;
function synth(kind){
  const n = 96*1024, b = new Uint8Array(n);
  const rnd = (a,z)=>{ for(let i=a;i<z&&i<n;i++) b[i]=Math.floor(Math.random()*256); };
  const txt = (a,z)=>{ const s='BEGIN RECORD; customer=ACME; amount=48200.00; status=OPEN;\\n';
    for(let i=a;i<z&&i<n;i++) b[i]=s.charCodeAt((i-a)%s.length); };
  if(kind==='text'){ txt(0,n); }
  else if(kind==='pdf'){
    // header and object tables are text; embedded streams are compressed
    txt(0,n);
    for(const [a,w] of [[6000,9000],[26000,14000],[58000,11000]]) rnd(a,a+w);
    b.set([0x25,0x50,0x44,0x46,0x2d,0x31,0x2e,0x37],0);          // %PDF-1.7
  }
  else if(kind==='png'){
    rnd(0,n);
    b.set([0x89,0x50,0x4e,0x47,0x0d,0x0a,0x1a,0x0a],0);          // PNG magic
    txt(8,80);                                                    // IHDR-ish header
  }
  else if(kind==='exe'){
    // PE headers and import tables are structured; some sections are packed
    txt(0,n);
    b.set([0x4d,0x5a,0x90,0x00],0);                               // MZ
    for(const [a,w] of [[18000,10000],[62000,17000]]) rnd(a,a+w);
    for(let i=0;i<4000;i++) b[40000+i]=0;                          // a zeroed section
  }
  else { rnd(0,n); b.set([0x50,0x4b,0x03,0x04],0); }              // ZIP
  return b;
}
function evColour(e){
  // 0..1 normalised entropy -> green through amber to red
  const t=Math.max(0,Math.min(1,(e-0.55)/0.42));
  const g=[46,111,94], k=[176,148,60], c=[176,58,46];
  const mix=(a,b,f)=>a.map((v,i)=>Math.round(v+(b[i]-v)*f));
  const rgb = t<0.5 ? mix(g,k,t*2) : mix(k,c,(t-0.5)*2);
  return `rgb(${rgb[0]},${rgb[1]},${rgb[2]})`;
}
function evPaint(id, data){
  const c=document.getElementById(id), x=c.getContext('2d'), W=c.width, H=c.height;
  const win=256, count=Math.floor(data.length/win);
  x.clearRect(0,0,W,H);
  let sum=0;
  for(let i=0;i<count;i++){
    const e=shannon(data.slice(i*win,(i+1)*win))/8; sum+=e;
    x.fillStyle=evColour(e);
    x.fillRect(Math.floor(i/count*W),0,Math.ceil(W/count)+1,H);
  }
  return {mean:sum/count, windows:count};
}
async function evRun(bytesIn){
  const kind=document.getElementById('ev-type').value;
  const pct=+document.getElementById('ev-pct').value;
  document.getElementById('ev-pctv').textContent=pct+'%';
  const orig = bytesIn || synth(kind);
  const k=await demoKeyBytes('heatmap');
  // fully encrypted
  const full=await aesCBC(orig,k,new Uint8Array(16));
  // intermittent: encrypt every Nth 4KB band to hit the requested coverage
  const band=4096, bands=Math.floor(orig.length/band);
  const want=Math.max(1,Math.round(bands*pct/100));
  const step=Math.max(1,Math.round(bands/want));
  const inter=new Uint8Array(orig);
  for(let i=0;i<bands;i+=step){
    const ct=await aesCBC(orig.slice(i*band,(i+1)*band),k,new Uint8Array(16));
    inter.set(ct.slice(0,band), i*band);
  }
  const a=evPaint('ev-a',orig), b=evPaint('ev-b',inter), c=evPaint('ev-c',full.slice(0,orig.length));
  const pc=v=>(v*8).toFixed(2);
  document.getElementById('ev-as').textContent='mean entropy '+pc(a.mean)+' / 8.00   ·   '+a.windows+' windows';
  document.getElementById('ev-bs').textContent='mean entropy '+pc(b.mean)+' / 8.00   ·   ~'+
    Math.round(100*step>0?100/step:0)+'% of bands encrypted';
  document.getElementById('ev-cs').textContent='mean entropy '+pc(c.mean)+' / 8.00   ·   every window at ciphertext level';
  describe('ev-a11y','Three entropy strips. The original has mean entropy '+pc(a.mean)+
    ' out of 8. Intermittently encrypted it rises to '+pc(b.mean)+
    ', with alternating structured and random regions. Fully encrypted it reaches '+pc(c.mean)+
    ', uniform across the whole file.');
}
document.getElementById('ev-type').addEventListener('change',()=>evRun(null));
document.getElementById('ev-pct').addEventListener('input',()=>evRun(evUploaded));
let evUploaded=null;
document.getElementById('ev-file').addEventListener('change', e=>{
  const f=e.target.files[0]; if(!f) return;
  const r=new FileReader();
  r.onload=()=>{ evUploaded=new Uint8Array(r.result).slice(0,EV_N); evRun(evUploaded); };
  r.readAsArrayBuffer(f.slice(0,EV_N));
});
evRun(null);
</script>""")


# ===========================================================================
page("10-key-models.html", "10", "Ransomware encryption · 10",
 "Key models",
 "One key for the whole machine, or a fresh key for every file. This single design choice changes "
 "more about a scheme than the choice of cipher does.",
 """
<h2>Two designs</h2>

""" + keymodel_diagram() + """

<table>
<tr><th></th><th>Session key</th><th>Per-file keys</th></tr>
<tr><td>Keys generated</td><td>One, for the whole host</td><td>One per file</td></tr>
<tr><td>Wrapped blobs on disk</td><td>All identical, or stored once</td><td>All different</td></tr>
<tr><td>Wrap operations</td><td>One</td><td>One per file</td></tr>
<tr><td>Cross-file analysis</td><td>Possible — material is shared</td><td>Impossible — nothing is shared</td></tr>
<tr><td>Effect of one key being exposed</td><td>Everything opens</td><td>One file opens</td></tr>
</table>

<p>Older families frequently used a session key because it is simpler and marginally faster. Modern
ones use per-file keys almost universally, because it removes an entire category of weakness: with
a fresh key and fresh nonce per file, no two files share anything that could be compared.</p>

<div class="sim">
  <div class="sim-head"><b>Simulation · what each model leaves on disk</b><span>compare the wrapped blobs</span></div>
  <div class="sim-body">
    <div class="row">
      <label for="s9-mode">Key model</label>
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

<p>This is why comparing the trailing blob across a handful of files is such a productive first
move. It requires no key, no software and no decryption — and it settles the question immediately.</p>

<h2>Ephemeral key agreement</h2>
<p>The most current designs go further than a random key per file. For each file they generate an
entire throwaway <em>keypair</em>, then use elliptic-curve Diffie-Hellman against the operator's
embedded public key to derive a shared secret. That secret becomes the file's encryption key.</p>

<div class="out tight">for every file:
  1. generate a throwaway keypair          (ephemeral private + public)
  2. combine ephemeral private + operator public   → shared secret
  3. use the shared secret as the file key
  4. store the ephemeral PUBLIC key with the file
  5. discard the ephemeral private key</div>

<p>To decrypt later, the operator combines their private key with the stored ephemeral public key
and arrives at the same shared secret. Nothing else is needed.</p>

<h3>The properties this produces</h3>
<ul>
  <li><strong>Nothing sensitive is stored.</strong> The value written to the file is a public key.
      On its own it reveals nothing at all — publishing it costs the attacker nothing.</li>
  <li><strong>No wrapped key exists.</strong> There is no encrypted blob to attack, because the key
      was never encrypted. It was derived.</li>
  <li><strong>No nonce field is needed.</strong> The nonce can be derived deterministically from
      the stored public key, so it never has to be written separately.</li>
  <li><strong>A fixed nonce becomes safe.</strong> Reusing a nonce is normally a serious bug, but
      it is only dangerous when the <em>key</em> repeats. Here every file has a unique shared
      secret, so a constant nonce never repeats under the same key.</li>
</ul>

<div class="note">
<p><b>That last point is worth remembering carefully.</b> Seeing a zero or constant nonce usually
indicates a mistake, and in most schemes it is one. In a per-file ephemeral design it is not —
the key lifecycle makes it sound. Judging the nonce without first checking how the key was produced
gets this exactly backwards, and it is a mistake that is easy to make with confidence.</p>
</div>

<h3>Following it through, step by step</h3>
<p>The mechanism is easier to trust once you have watched the two sides arrive at the same value
without exchanging it.</p>
<div class="out tight">The operator, once, before deployment
  private key  d          kept on their infrastructure, never shipped
  public key   P = d·G    embedded in the payload

On the victim machine, for one file
  1.  generate ephemeral pair      e (private),  E = e·G (public)
  2.  shared secret  S = e·P       = e·(d·G)  =  (e·d)·G
  3.  file key = KDF(S)
  4.  encrypt the file with that key
  5.  write E alongside the file
  6.  discard e and S

Later, by the operator
  1.  read E from the file
  2.  shared secret  S = d·E       = d·(e·G)  =  (d·e)·G   ← the same value
  3.  file key = KDF(S)</div>
<p>Both sides compute <code>(e·d)·G</code>, arriving at an identical secret. Neither ever
transmitted it. An observer holding <code>E</code> and <code>P</code> — both public — cannot
derive it, because recovering <code>e</code> or <code>d</code> from them is the hard problem the
curve is chosen for.</p>
<p>Notice what is written to disk: <code>E</code>, a public key. It protects nothing and reveals
nothing. There is no wrapped blob to attack because no wrapping happened.</p>

<h3>Why this displaced simple wrapping</h3>
<table>
<tr><th>Concern</th><th>RSA-wrapped key</th><th>Ephemeral agreement</th></tr>
<tr><td>Stored per file</td><td>256 or 512 bytes</td><td>32 bytes</td></tr>
<tr><td>What is stored</td><td>An encrypted secret</td><td>A public key</td></tr>
<tr><td>Cost per file</td><td>One RSA operation</td><td>One curve multiplication — faster</td></tr>
<tr><td>Needs a nonce field</td><td>Usually yes</td><td>No — derive it from the stored key</td></tr>
</table>
<p>Smaller, faster, and less is written to disk. The move was driven by ordinary engineering
preference rather than by any weakness in the older approach.</p>

<h2>Where the key lives while it is being used</h2>
<p>Whatever the model, the symmetric key must exist in plain form at some point — a cipher cannot
work with a wrapped key. That window is brief and it is the only moment in the entire scheme where
the plaintext key and the data are in the same place.</p>
<div class="out tight">key generated ──▶ file encrypted ──▶ key wrapped or discarded ──▶ key erased
              └────────── the key exists in plain form ──────────┘</div>
<p>Before that window the key does not exist. After it, the only remaining form is one that
requires the operator's private key to open. Well-built schemes make the window as short as
possible and overwrite the memory afterwards rather than merely releasing it.</p>

<h2>Identifying the model in practice</h2>
<table>
<tr><th>Observation</th><th>Model</th></tr>
<tr><td>Trailing blobs identical across files</td><td>Session key</td></tr>
<tr><td>No trailing blob at all; one separate key file</td><td>Session key, stored once</td></tr>
<tr><td>Trailing blobs all different, 256 or 512 bytes</td><td>Per-file key, RSA-wrapped</td></tr>
<tr><td>Trailing blobs all different, 32 or 33 bytes</td><td>Per-file ephemeral key agreement</td></tr>
</table>
<p>Four observations, four distinct designs, and every one of them determinable from the encrypted
files alone. Module 13 develops this into a full identification method.</p>
""",
 sim="""<script>
async function s9run(){
  const mode=document.getElementById('s9-mode').value;
  const names=['invoice.xlsx','ledger.mdf','contract.docx','archive.pst','backup.vmdk'];
  const session=crypto.getRandomValues(new Uint8Array(32));
  let o='', blobs=[];
  for(const n of names){
    const fileKey = mode==='session' ? session : crypto.getRandomValues(new Uint8Array(32));
    const wrapped = hex(await crypto.subtle.digest('SHA-256', fileKey)).slice(0,32);
    blobs.push(wrapped);
    o += (n+'.locked').padEnd(22)+'wrapped key  '+wrapped+'\\n';
  }
  const uniq=new Set(blobs).size;
  document.getElementById('s9-out').textContent = o+'\\ndistinct wrapped blobs: '+uniq+' of '+blobs.length;
  document.getElementById('s9-stat').innerHTML = mode==='session'
    ? 'Every blob is <b>identical</b>. One key encrypted all five files, so the same wrapped value '+
      'repeats on each. Comparing any two files reveals the model immediately.'
    : 'Every blob is <b>different</b>. Five files, five keys, five wraps. Nothing is shared between '+
      'files, so there is nothing to compare across them.';
}
document.getElementById('s9-go').addEventListener('click',s9run);
document.getElementById('s9-mode').addEventListener('change',s9run);
s9run();
</script>""")


# ===========================================================================
page("11-os-native.html", "11", "Ransomware encryption · 11",
 "OS-native encryption",
 "Some families ship no cryptography at all. They switch on the encryption already built into the "
 "operating system, which changes the shape of the problem completely.",
 """
<h2>Encryption without an encryptor</h2>
<p>Every scheme so far assumes the software contains a cipher. That assumption fails against an
approach that simply enables the disk encryption the operating system already provides.</p>
<p>There is no cipher to examine, because the vendor wrote it. The encryption is correct,
well-tested, and performed by signed system components doing exactly what they were designed to
do. Nothing is malformed; only the ownership of the key has changed.</p>

<table>
<tr><th></th><th>Custom encryptor</th><th>OS-native</th></tr>
<tr><td>Cipher</td><td>Compiled into the software</td><td>Built into the operating system</td></tr>
<tr><td>Scope</td><td>Files matching a target list</td><td><strong>The entire volume, including the OS</strong></td></tr>
<tr><td>Victim experience</td><td>Files present but unreadable</td><td><strong>The machine will not boot</strong></td></tr>
<tr><td>Speed</td><td>Bounded by disk throughput</td><td>Can be near-instant — see below</td></tr>
<tr><td>What you can examine</td><td>The whole design</td><td>Nothing; it is a documented feature</td></tr>
</table>

<h2>How full-disk encryption is layered</h2>
<p>BitLocker is the common example, and its layering is precisely what makes the attack work.
There are three levels, and the interesting one is in the middle.</p>

""" + bitlocker_diagram() + """

<p>Reading it from the bottom: one or more <strong>protectors</strong> guard the volume master key.
The VMK in turn encrypts the full volume encryption key, and the FVEK encrypts the data itself.</p>

<h3>The protectors</h3>
<table>
<tr><th>Protector</th><th>Unlocks using</th><th>Notes</th></tr>
<tr><td>TPM</td><td>A hardware chip, automatically at boot</td><td>Transparent to the user</td></tr>
<tr><td>TPM + PIN</td><td>Hardware plus something typed</td><td>Resists an attacker with physical access</td></tr>
<tr><td>Recovery password</td><td>A 48-digit number</td><td>The fallback, often escrowed centrally</td></tr>
<tr><td>Startup key</td><td>A file on removable media</td><td>Used where there is no TPM</td></tr>
<tr><td>Password</td><td>A passphrase</td><td>Typically for data volumes</td></tr>
</table>

<h2>Why the swap is instant</h2>
<p>The volume is <strong>never re-encrypted when protectors change</strong>. Adding or removing a
protector rewrites only the small layer that guards the VMK — a few kilobytes. The terabytes
underneath are untouched.</p>
<p>That is the entire mechanism: <strong>add a protector only the attacker knows, remove the ones
the owner knows.</strong> The data never moves.</p>

<div class="sim">
  <div class="sim-head"><b>Simulation · why swapping protectors is instant</b><span>compare the work done</span></div>
  <div class="sim-body">
    <div class="row">
      <label for="s10-size">Volume size</label>
      <select id="s10-size">
        <option value="500">500 GB</option><option value="2000" selected>2 TB</option>
        <option value="10000">10 TB</option>
      </select>
      <label for="s10-mode">Scenario</label>
      <select id="s10-mode">
        <option value="custom">Custom encryptor — rewrite every file</option>
        <option value="fresh">OS encryption from scratch — encrypt the volume</option>
        <option value="swap" selected>Volume already encrypted — swap the protector</option>
      </select>
    </div>
    <div class="out tight" id="s10-out" style="min-height:130px"></div>
  </div>
</div>

<h3>Two very different scenarios</h3>
<p>The distinction above is often missed, and it changes the picture entirely:</p>
<ul>
  <li><strong>The volume is already encrypted.</strong> Only the key-protection layer is rewritten.
      Seconds of work. No bulk encryption happens at all.</li>
  <li><strong>The volume is not encrypted.</strong> Encryption must be switched on and a full pass
      performed, taking as long as any other full-disk encryption — and leaving far more
      evidence.</li>
</ul>

<h2>The key escrow question</h2>
<p>Full-disk encryption in a managed environment is normally configured to escrow its recovery key
centrally — into a directory service, a device management platform, or a dedicated database. The
key is held somewhere other than the machine.</p>
<p>This matters conceptually because it is the one case in this whole course where a copy of the
key material legitimately exists somewhere the attacker does not control. Everywhere else in the
hybrid scheme, the only key that opens the data is on the operator's infrastructure by design. Here
it may not be.</p>

<h2>File-level rather than volume-level</h2>
<p>Full-disk encryption is not the only mechanism an operating system provides. Windows also has
the Encrypting File System, which works per file rather than per volume.</p>
<p>EFS encrypts a file with a symmetric key, then wraps that key with a certificate belonging to a
user account. That is the hybrid scheme from module 09 again, built into the OS and keyed to an
identity rather than to a disk.</p>
<table>
<tr><th></th><th>Full-disk (BitLocker)</th><th>File-level (EFS)</th></tr>
<tr><td>Unit</td><td>The whole volume</td><td>Individual files and folders</td></tr>
<tr><td>Key is tied to</td><td>The machine, via protectors</td><td>A user account, via a certificate</td></tr>
<tr><td>Visible when running</td><td>Nothing — it is transparent</td><td>Nothing — it is transparent</td></tr>
<tr><td>Effect if the key is changed</td><td>The machine will not boot</td><td>Specific files become unreadable</td></tr>
</table>
<p>The pattern is the same in both: the encryption is a supported feature, correctly implemented,
and the only thing that changed is which identity controls the key.</p>

<h2>Encrypting at the hypervisor</h2>
<p>Virtualisation creates a layer that is unusually attractive to encrypt, for a reason that has
nothing to do with cryptography: on a hypervisor, an entire machine is one file.</p>

""" + hypervisor_diagram() + """

<p>A virtual machine's disk is stored as a flat image on a datastore — a <code>.vmdk</code> or
similar. From the hypervisor's perspective it is not an operating system with thousands of files.
It is a single large file, like any other.</p>
<p>That collapses the work enormously. Encrypting a guest from inside means enumerating and
rewriting every file in it, one machine at a time, with the guest running. Encrypting from the
hypervisor means writing to a handful of large files, and the guests need not be running at all.</p>

<h3>Two mechanisms at that layer</h3>
<table>
<tr><th>Approach</th><th>How it works</th><th>Effect</th></tr>
<tr><td><strong>Encrypt the disk images</strong></td><td>Treat each <code>.vmdk</code> as an ordinary file and encrypt it, often partially</td><td>The machine will not boot; the image is a foreign format to the hypervisor</td></tr>
<tr><td><strong>Use built-in VM encryption</strong></td><td>Enable the platform's own encryption with a key the operator controls</td><td>The same OS-native pattern as BitLocker, one layer up</td></tr>
</table>
<p>The first is the more common. It requires nothing from the platform — the images are just files,
and any cipher will do. Partial coverage is especially effective here, because a disk image has
critical structures at predictable positions, and damaging a few of them is enough to make the
whole image unreadable while touching a tiny fraction of its bytes.</p>

<h3>Why the scope multiplies</h3>
<p>Consolidation is the point of virtualisation, so a single host commonly carries dozens of
workloads and a cluster carries hundreds. Encryption applied at that layer inherits the
consolidation ratio.</p>
<div class="out tight">inside one guest      →  one machine affected
at the hypervisor     →  every machine on that host
at shared storage     →  every machine on every host using it</div>
<p>The cryptography is identical in all three. Only the layer differs, and the layer decides the
blast radius. That is the general lesson: <strong>choosing where to apply encryption is a more
consequential decision than choosing which cipher to apply.</strong></p>

<h2>Why this is a different category</h2>
<p>It is worth being precise about what makes this genuinely distinct rather than just a variation.</p>
<ul>
  <li><strong>There is no implementation to study.</strong> Everywhere else in this course, a
      design decision was made by whoever wrote the software. Here the decisions were made by the
      platform vendor and published.</li>
  <li><strong>Nothing is anomalous.</strong> A custom encryptor is unusual software doing unusual
      things. This is expected software doing expected things.</li>
  <li><strong>The scale is set by the layer, not the effort.</strong> One action at the volume or
      hypervisor layer covers everything beneath it, without touching anything individually.</li>
  <li><strong>A key copy may legitimately exist elsewhere</strong>, if escrow was configured — the
      one place in this course where that is true by design.</li>
</ul>

<h2>The broader category</h2>
<table>
<tr><th>Mechanism</th><th>Platform</th><th>What gets encrypted</th></tr>
<tr><td>BitLocker</td><td>Windows</td><td>Whole volumes, including the boot volume</td></tr>
<tr><td>EFS</td><td>Windows</td><td>Individual files, under a certificate</td></tr>
<tr><td>LUKS / dm-crypt</td><td>Linux, NAS appliances</td><td>Whole volumes</td></tr>
<tr><td>Hypervisor VM encryption</td><td>ESXi, vSphere</td><td>Entire virtual machines at once</td></tr>
<tr><td>Cloud storage encryption</td><td>Object storage</td><td>Objects rewritten under a supplied key</td></tr>
<tr><td>Archive tools with a password</td><td>Any</td><td>Files packed into an encrypted container</td></tr>
</table>

<p>The hypervisor case is worth singling out for scale. A single action at that layer encrypts every
virtual machine on the host simultaneously, which can be hundreds of workloads — without touching
any of them individually.</p>

<div class="note">
<p><b>The conceptual point.</b> Encryption is not inherently hostile. The same BitLocker that
protects a stolen laptop can lock out its owner — nothing about the cryptography changed, only who
holds the key. That is true of every scheme on this site, and it is why encryption is worth studying
as a neutral mechanism rather than as a weapon.</p>
</div>
""",
 sim="""<script>
function s10run(){
  const gb=+document.getElementById('s10-size').value;
  const mode=document.getElementById('s10-mode').value;
  const MBps=800;
  const fmt=s=>{ if(s<1) return '< 1 second';
    if(s<60) return s.toFixed(0)+' seconds';
    if(s<3600) return (s/60).toFixed(1)+' minutes';
    return (s/3600).toFixed(1)+' hours'; };
  let o='';
  if(mode==='custom'){
    o='Custom encryptor — every file read, encrypted and written back\\n'+'─'.repeat(60)+
      '\\n\\n  data to process   '+gb+' GB\\n  disk throughput   ~'+MBps+' MB/s\\n\\n'+
      '  TIME  '+fmt((gb*1024)/MBps)+'\\n\\n'+
      'Every byte crosses the disk twice. That is the window in which\\nthe activity is visible.';
  } else if(mode==='fresh'){
    o='Volume not previously encrypted — full encryption pass required\\n'+'─'.repeat(60)+
      '\\n\\n  data to process   '+gb+' GB\\n  disk throughput   ~'+MBps+' MB/s\\n\\n'+
      '  TIME  '+fmt((gb*1024)/MBps)+'\\n\\n'+
      'Comparable to the custom encryptor, because the same amount of\\ndata must be transformed. '+
      'Setup work is needed first as well.';
  } else {
    o='Volume already encrypted — only the protector is swapped\\n'+'─'.repeat(60)+
      '\\n\\n  data to process   0 GB          ← the volume is not touched\\n'+
      '  key layer rewritten   a few kilobytes\\n\\n  TIME  < 1 second\\n\\n'+
      'The '+gb+' GB underneath is already encrypted and stays exactly as it\\nis. Only the small '+
      'layer protecting the master key is rewritten.\\n\\nSame outcome for the owner. Roughly '+
      fmt((gb*1024)/MBps)+' less work.';
  }
  document.getElementById('s10-out').textContent=o;
}
['s10-size','s10-mode'].forEach(id=>document.getElementById(id).addEventListener('input',s10run));
s10run();
</script>""")


# ===========================================================================
page("12-hypervisor.html", "12", "Ransomware encryption · 12",
 "Hypervisor encryption",
 "A virtual machine is a file. That single fact makes the hypervisor the most efficient layer to "
 "attack, and it changes what encryption even means.",
 """
<h2>Why the layer matters so much</h2>
<p>A virtualisation host runs many guest operating systems, each believing it has a disk. It does
not. It has a <strong>file</strong> on the host — a virtual disk image, typically a
<code>.vmdk</code> or <code>.vhdx</code> — that the hypervisor presents as though it were hardware.</p>
<p>Encrypt inside a guest and you have encrypted one machine's files. Encrypt the virtual disk file
itself and you have taken that entire machine offline, without ever entering it.</p>

""" + hypervisor_diagram() + """

<h2>The arithmetic of the layer</h2>
<table>
<tr><th></th><th>Inside each guest</th><th>At the hypervisor</th></tr>
<tr><td>Machines reached per operation</td><td>One</td><td><strong>All of them</strong></td></tr>
<tr><td>Files to process</td><td>Thousands per guest</td><td>A handful per guest</td></tr>
<tr><td>Guest must be running</td><td>Yes</td><td>No — a powered-off guest is still a file</td></tr>
<tr><td>Guest security software applies</td><td>Yes</td><td><strong>No — it is not running at this layer</strong></td></tr>
<tr><td>Result</td><td>Files unreadable</td><td>The machine will not start</td></tr>
</table>

<p>A single host commonly runs dozens of virtual machines, and a cluster shares storage across many
hosts. One operation at this layer can therefore cover more workloads than any amount of effort at
the guest layer, which is why it is such an attractive target.</p>

<div class="sim">
  <div class="sim-head"><b>Simulation · the leverage of the layer</b><span>count the operations</span></div>
  <div class="sim-body">
    <div class="row">
      <label for="hv-hosts">Hosts</label>
      <input type="range" id="hv-hosts" min="1" max="40" value="8" style="flex:1">
      <span class="stat" id="hv-hv"></span>
    </div>
    <div class="row">
      <label for="hv-vms">Guests per host</label>
      <input type="range" id="hv-vms" min="1" max="60" value="24" style="flex:1">
      <span class="stat" id="hv-vv"></span>
    </div>
    <div class="out tight" id="hv-out" style="min-height:190px"></div>
  </div>
</div>

<h2>What actually gets encrypted</h2>
<p>A virtual machine is not one file. It is a small set, and they have different importance.</p>
<table>
<tr><th>File</th><th>Holds</th><th>Effect if encrypted</th></tr>
<tr><td><code>.vmdk</code> flat file</td><td>The guest's disk contents — usually the bulk</td><td>The disk is unreadable</td></tr>
<tr><td><code>.vmdk</code> descriptor</td><td>Geometry and layout, a few kilobytes</td><td>The disk cannot be interpreted at all</td></tr>
<tr><td><code>.vmx</code></td><td>The machine's configuration</td><td>The VM cannot be registered or started</td></tr>
<tr><td><code>.vswp</code>, snapshots</td><td>Runtime and point-in-time state</td><td>Snapshots become unusable</td></tr>
</table>
<p>Notice the asymmetry. The flat file may be hundreds of gigabytes; the descriptor is a few
kilobytes and equally load-bearing. Encrypting only the small files renders the machine
unstartable for a rounding error of the effort — the header-only idea from module 10, applied at
the level of a whole virtual machine.</p>

<h2>Direct volume access</h2>
<p>There is a further step available at this layer. Rather than opening a virtual disk as a file
through the filesystem, a program can address the underlying storage directly.</p>
<div class="out tight">through the filesystem        open the .vmdk, read, encrypt, write back
direct volume access          address the raw device, encrypt regions in place</div>
<p>Two conceptual differences follow.</p>
<ul>
  <li><strong>File locks stop mattering.</strong> A running virtual machine holds its disk open,
      which normally prevents another program from writing to it. Addressing the underlying storage
      sidesteps the question, because the lock is a filesystem construct.</li>
  <li><strong>Sizes never change.</strong> Writing back in place means the encrypted result occupies
      exactly the space the original did — the same constraint that makes disk encryption use
      length-preserving modes like XTS, from module 05.</li>
</ul>
<p>The trade-off is that nothing keeps track of structure. Writing directly to storage means
respecting layout by hand, and mistakes are not correctable.</p>

<h2>Native hypervisor encryption</h2>
<p>Virtualisation platforms also offer encryption as a feature. A virtual machine can be encrypted
by the platform itself, with keys supplied by a configured key management service.</p>
<p>This is module 13's pattern at a higher layer. The encryption is a supported feature, correctly
implemented, doing exactly what it was designed to do — and the only thing that determines who can
start those machines is which key service the platform is pointed at.</p>

<table>
<tr><th>Approach</th><th>Who performs the encryption</th><th>Reach</th></tr>
<tr><td>Encrypt inside each guest</td><td>Software running in the guest</td><td>One machine per operation</td></tr>
<tr><td>Encrypt the virtual disk files</td><td>Software running on the host</td><td>Every machine on the host</td></tr>
<tr><td>Direct volume access</td><td>Software running on the host</td><td>Every machine, ignoring locks</td></tr>
<tr><td>Native platform encryption</td><td><strong>The platform itself</strong></td><td>Every machine, as a feature</td></tr>
</table>

<h2>Why the ciphers differ here</h2>
<p>Virtualisation hosts are not Windows machines. They run purpose-built operating systems, often
on varied hardware, with no Windows cryptographic interface to call. Module 07's reasoning applies
directly: software targeting this layer must carry its own cryptography.</p>
<p>And having carried its own, it tends to choose the cipher that performs best without hardware
assumptions — which is why XChaCha20-Poly1305 and similar constructions appear far more often at
this layer than AES does. The platform constraint drives the implementation choice, which in turn
drives the cipher choice.</p>

<div class="note">
<p><b>The conceptual summary.</b> Encryption at the hypervisor layer is not a different kind of
cryptography. It is the same schemes from modules 08 through 10 applied to a smaller number of much
larger files, at a layer where a handful of operations reach everything. The leverage comes
entirely from where it is applied, not from what it does.</p>
</div>
""",
 sim="""<script>
function hvRun(){
  const hosts=+document.getElementById('hv-hosts').value;
  const vms=+document.getElementById('hv-vms').value;
  document.getElementById('hv-hostsv').textContent=hosts;
  document.getElementById('hv-vmsv').textContent=vms;
  const total=hosts*vms, vmdkPerGuest=3;
  const guestOps=total, guestFiles=total*4200;
  const hvOps=hosts,  hvFiles=total*vmdkPerGuest;
  const fmt=n=>n.toLocaleString();
  const NL='\\n';
  document.getElementById('hv-out').textContent =
    'INSIDE EACH GUEST'+NL+'\\u2500'.repeat(58)+NL
    +'  machines to reach       '+fmt(guestOps)+NL
    +'  files to process        '+fmt(guestFiles)+'   (~4,200 per guest)'+NL
    +'  guest must be running   yes'+NL
    +'  guest security applies  yes'+NL+NL
    +'AT THE HYPERVISOR'+NL+'\\u2500'.repeat(58)+NL
    +'  machines to reach       '+fmt(hvOps)+NL
    +'  files to process        '+fmt(hvFiles)+'   (~'+vmdkPerGuest+' per guest)'+NL
    +'  guest must be running   no - a powered-off guest is still a file'+NL
    +'  guest security applies  no - it is not running at this layer'+NL+NL
    +'RATIO'+NL
    +'  '+Math.round(guestOps/hvOps)+'x fewer machines to reach, '
    +Math.round(guestFiles/hvFiles)+'x fewer files to touch,'+NL
    +'  for the same '+fmt(total)+' workloads taken offline.';
}
['hv-hosts','hv-vms'].forEach(id=>document.getElementById(id).addEventListener('input',hvRun));
hvRun();
</script>""")


# ===========================================================================
page("13-telling-them-apart.html", "13", "Putting it together · 13",
 "Telling them apart",
 "Everything so far, applied backwards. Given an encrypted file and nothing else, how much can you "
 "work out about the scheme that produced it?",
 """
<h2>A method, not a lookup</h2>
<p>Each design decision leaves a trace. You cannot read the data, but you can often describe the
scheme quite precisely — and you can do it without the software, without a key, and without
decrypting anything.</p>
<p>Work through four questions in order. Each narrows the possibilities.</p>

<h3>1. Is it actually encrypted?</h3>
<p>Do not assume. Compressed formats score the same entropy as ciphertext, so the entropy number
alone cannot answer this. What answers it is <strong>structure</strong>: does the file still begin
with the header its extension implies?</p>
<table>
<tr><th>Observation</th><th>Conclusion</th></tr>
<tr><td>High entropy, header intact and matching the extension</td><td>Probably just a compressed file</td></tr>
<tr><td>High entropy, header absent where one is expected</td><td>The header has been encrypted</td></tr>
<tr><td>An unrecognised extension appended to a recognised one</td><td>Something was appended after the real name</td></tr>
</table>

<h3>2. What size relationship does it have?</h3>
<p>If an original is available for comparison, arithmetic settles a great deal.</p>
<table>
<tr><th>Size relationship</th><th>Indicates</th></tr>
<tr><td>Identical to the original</td><td>Stream cipher, or a counter-based mode. No padding</td></tr>
<tr><td>Rounded up to a multiple of 16</td><td>Block cipher with padding — CBC or ECB</td></tr>
<tr><td>Multiple of 16, plus a consistent 16 bytes</td><td>Padding plus an authentication tag — an AEAD mode</td></tr>
<tr><td>Plus a fixed 256 or 512 bytes</td><td>An RSA-wrapped key attached</td></tr>
<tr><td>Plus a fixed 32 or 33 bytes</td><td>An elliptic-curve public key attached</td></tr>
</table>
<p>Overhead usually decomposes cleanly. A file 272 bytes larger than its original is likely 256
bytes of RSA-2048 wrapped key plus 16 bytes of block padding. When the arithmetic closes exactly,
the reading is probably right.</p>

<h3>3. What is the coverage pattern?</h3>
<p>Measure entropy in slices rather than as one number, and the pattern draws itself.</p>

""" + signature_diagram() + """

<p>Remember the resolution rule from module 10: your measurement window must be smaller than the
feature you are looking for. Fine striping is invisible at 4 KB and obvious at 512 bytes.</p>

<h3>4. What is the key model?</h3>
<p>Compare the trailing bytes across several files. Identical means one key for the host; different
means one key per file. This takes seconds and it reshapes everything else you conclude.</p>

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

<h2>A worked identification</h2>
<p>Applying the four questions to a real set of observations, start to finish.</p>
<div class="out tight">Given: a folder of files ending .lok, plus one matching backup copy.

Q1  IS IT ENCRYPTED?
    ledger.mdf.lok    entropy 7.99, no MDF header where one is expected
    photo.jpg         entropy 7.94, JFIF header present, no appended extension
    → the .mdf is encrypted; the .jpg is simply a photograph

Q2  SIZE RELATIONSHIP?
    backup copy       8,412,517 bytes
    encrypted copy    8,412,821 bytes
    overhead                304 bytes
    8,412,821 − 304 = 8,412,517 … and 8,412,528 is the next multiple of 16
    → 11 bytes padding + 256 wrapped key + 37 unexplained
    → try again: 11 padding + 256 key + 16 AEAD tag + 21 marker
    → RSA-2048 wrap, an authenticated mode, and a small marker

Q3  COVERAGE PATTERN?
    entropy per 4 KB slice: uniformly 7.98 throughout
    → full encryption, no partial coverage

Q4  KEY MODEL?
    last 256 bytes of six files, hashed: six distinct values
    → per-file keys

CONCLUSION
    Per-file symmetric keys, an authenticated mode, each key wrapped with
    RSA-2048, full coverage, with a short family marker at the end.
    Reached without the software, without a key, and without decrypting.</div>
<p>Notice the second attempt at question two. The first decomposition left 37 bytes unexplained,
which usually means a term is missing rather than that the reading is wrong. Adding the
authentication tag closed it. <strong>An arithmetic that does not close is information</strong>,
not a dead end.</p>

<h2>Three traps</h2>

<h3>High entropy does not mean encrypted</h3>
<p>JPEG scores around 7.9, MP4 around 8.0, ZIP similarly. Compression produces evenly distributed
bytes for the same reason encryption does. Judging on entropy alone marks every photograph and
video as encrypted, which is not a small error — it is the difference between "three files were
affected" and "three hundred were".</p>

<h3>High entropy does not mean secure</h3>
<p>AES-ECB scores near the maximum and leaks the picture straight through, as module 05 showed
directly. Entropy measures distribution. It cannot see block-level repetition, which is exactly
what breaks ECB. The measurement that catches it is distinct block count.</p>

<h3>Small samples never reach 8.0</h3>
<p>A 128-byte sample of perfect ciphertext scores about 6.55, because 128 values cannot populate
256 slots. Comparing a small wrapped-key blob against 8.0 will make genuine ciphertext look
non-random and you will discard a correct finding.</p>

<div class="note">
<p><b>The habit worth forming.</b> Entropy is one measurement among several and on its own it is
the weakest of them. Size relationships, block repetition, header integrity and the shape of
trailing data each say something entropy cannot. A conclusion supported by two independent
observations is worth far more than one supported by a single number.</p>
</div>

<h2>What you can and cannot determine</h2>
<table>
<tr><th>Determinable from the output alone</th><th>Not determinable</th></tr>
<tr><td>Block or stream cipher</td><td>Which specific cipher</td></tr>
<tr><td>Whether padding is used</td><td>The key</td></tr>
<tr><td>Whether an AEAD tag is present</td><td>The plaintext</td></tr>
<tr><td>Coverage pattern and percentage</td><td>Which family, with certainty</td></tr>
<tr><td>Key model — session or per-file</td><td>Where the key came from</td></tr>
<tr><td>Probable asymmetric family, from blob size</td><td>Whether the key was well generated</td></tr>
</table>
<p>The right-hand column is not a failure. It marks the boundary of what an output-only analysis
can reach, and knowing where that boundary sits is part of doing the analysis honestly.</p>

<h2>Where to go next</h2>
<p>You now have the concepts. For the cryptography itself in more depth, <em>Serious
Cryptography</em> by Jean-Philippe Aumasson is the standard modern reference. For how specific
families combine these parts, published vendor threat-intelligence writeups give the detail — read
them for the scheme first and the indicators last.</p>
<p>The <a href="reference.html">reference page</a> collects every term, size and constant used
across these eleven modules in one place.</p>
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
 {q:'Five encrypted files each end with a 32-byte high-entropy tail, and all five differ. What is the key model?',
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
 {q:'Entropy across a large file alternates high, low, high, low, evenly throughout. Which pattern?',
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
    const b=document.createElement('button'); b.className='ghost'; b.type='button'; b.textContent=t;
    b.addEventListener('click',()=>{
      if(answered) return; answered=true;
      const ok=(i===q.a); if(ok) score++;
      document.getElementById('s11-fb').innerHTML =
        (ok?'<b class="c-plain">Correct.</b> ':'<b class="c-cipher">Not quite.</b> The answer is “'+q.o[q.a]+'”. ')+q.why;
      document.getElementById('s11-score').textContent='score '+score+' / '+Q.length;
    });
    box.appendChild(b);
  });
  document.getElementById('s11-fb').textContent=''; answered=false;
}
document.getElementById('s11-next').addEventListener('click',()=>{
  if(qi<Q.length-1){ qi++; s11draw(); }
  else { document.getElementById('s11-fb').innerHTML='<b>Finished.</b> Final score '+score+' of '+
    Q.length+'. Every one of these was answerable from the output alone — no key, no software, no tooling.'; }
});
document.getElementById('s11-restart').addEventListener('click',()=>{ qi=0;score=0;s11draw();
  document.getElementById('s11-score').textContent=''; });
s11draw();
</script>""")


# ===========================================================================
page("reference.html", "ref", "Reference",
 "Reference",
 "Every term, size and constant used across the eleven modules, in one place.",
 """
<h2>Sizes worth memorising</h2>
<table>
<tr><th>Value</th><th>Size</th><th>Where it appears</th></tr>
<tr><td>AES block</td><td>16 bytes</td><td>Padding, block repetition, size arithmetic</td></tr>
<tr><td>AES-128 / 192 / 256 key</td><td>16 / 24 / 32 bytes</td><td>Module 04</td></tr>
<tr><td>AES key schedule, expanded</td><td>176 / 208 / 240 bytes</td><td>Module 04</td></tr>
<tr><td>ChaCha20 key</td><td>32 bytes</td><td>Module 04</td></tr>
<tr><td>ChaCha20 nonce</td><td>8 or 12 bytes</td><td>Module 04</td></tr>
<tr><td>XChaCha20 nonce</td><td>24 bytes</td><td>The only thing distinguishing it from ChaCha20</td></tr>
<tr><td>CBC initialisation vector</td><td>16 bytes</td><td>Module 05</td></tr>
<tr><td>GCM nonce / tag</td><td>12 / 16 bytes</td><td>Modules 03 and 05</td></tr>
<tr><td>RSA-2048 ciphertext</td><td>256 bytes</td><td>Wrapped key size, module 13</td></tr>
<tr><td>RSA-4096 ciphertext</td><td>512 bytes</td><td>Wrapped key size, module 13</td></tr>
<tr><td>Curve25519 public key</td><td>32 bytes</td><td>Ephemeral key storage, module 11</td></tr>
<tr><td>SHA-256 output</td><td>32 bytes</td><td>Module 03</td></tr>
<tr><td>SHA-512 output</td><td>64 bytes</td><td>Module 03</td></tr>
</table>

<h2>Recognisable constants</h2>
<p>Cipher implementations must contain these verbatim, because the algorithms require them.</p>
<table>
<tr><th>Constant</th><th>Belongs to</th></tr>
<tr><td><code>63 7c 77 7b f2 6b 6f c5</code></td><td>AES S-box, first bytes</td></tr>
<tr><td><code>52 09 6a d5 30 36 a5 38</code></td><td>AES inverse S-box — decryption is implemented</td></tr>
<tr><td><code>expand 32-byte k</code></td><td>ChaCha20 / Salsa20 / XChaCha20</td></tr>
<tr><td><code>expand 16-byte k</code></td><td>The 128-bit key variant</td></tr>
<tr><td><code>-----BEGIN PUBLIC KEY-----</code></td><td>A PEM-encoded public key</td></tr>
</table>
<p>Their presence proves the algorithm is available, not that it is used. A statically linked
program may carry an entire cryptographic library of which it calls one function.</p>

<h2>Glossary</h2>
<table>
<tr><td><strong>AEAD</strong></td><td>Authenticated Encryption with Associated Data. Encrypts and authenticates in one operation, adding a tag.</td></tr>
<tr><td><strong>AES</strong></td><td>The standard block cipher. Operates on 16 bytes at a time, with 10 to 14 rounds.</td></tr>
<tr><td><strong>Avalanche</strong></td><td>The property that one changed input bit alters about half the output bits.</td></tr>
<tr><td><strong>Block cipher</strong></td><td>A cipher that transforms fixed-size blocks. Needs padding and a mode.</td></tr>
<tr><td><strong>ChaCha20</strong></td><td>A stream cipher, fast in software with no hardware support.</td></tr>
<tr><td><strong>Ciphertext</strong></td><td>The output of encryption.</td></tr>
<tr><td><strong>Collision resistance</strong></td><td>The difficulty of finding two inputs with the same hash.</td></tr>
<tr><td><strong>CSPRNG</strong></td><td>A random generator whose output cannot be predicted. The correct source for a key.</td></tr>
<tr><td><strong>Curve25519</strong></td><td>An elliptic curve widely used for key agreement. Keys are 32 bytes.</td></tr>
<tr><td><strong>Diffie-Hellman</strong></td><td>A method for two parties to derive a shared secret without transmitting it.</td></tr>
<tr><td><strong>ECB</strong></td><td>A mode that encrypts each block independently. Leaks structure; never use it.</td></tr>
<tr><td><strong>ECDH</strong></td><td>Diffie-Hellman using elliptic curves.</td></tr>
<tr><td><strong>Entropy</strong></td><td>A measure of how evenly byte values are distributed, from 0 to 8.</td></tr>
<tr><td><strong>Ephemeral key</strong></td><td>A key generated for a single use and then discarded.</td></tr>
<tr><td><strong>FVEK</strong></td><td>Full Volume Encryption Key — encrypts the data in full-disk encryption.</td></tr>
<tr><td><strong>Hash</strong></td><td>A one-way fixed-size fingerprint of data.</td></tr>
<tr><td><strong>HMAC</strong></td><td>A keyed fingerprint. Proves integrity and authenticity together.</td></tr>
<tr><td><strong>Hybrid encryption</strong></td><td>Bulk-encrypt with a symmetric cipher, then protect that key asymmetrically.</td></tr>
<tr><td><strong>IV</strong></td><td>Initialisation vector. A non-secret value making each encryption unique.</td></tr>
<tr><td><strong>KDF</strong></td><td>Key derivation function. Turns a password or secret into a key, deliberately slowly.</td></tr>
<tr><td><strong>Kerckhoffs's principle</strong></td><td>A system should stay secure even if everything but the key is public.</td></tr>
<tr><td><strong>Key schedule</strong></td><td>The expansion of a key into per-round keys inside a block cipher.</td></tr>
<tr><td><strong>MAC</strong></td><td>Message Authentication Code. A fingerprint only a key holder can produce.</td></tr>
<tr><td><strong>Mode of operation</strong></td><td>How a block cipher handles data longer than one block.</td></tr>
<tr><td><strong>Nonce</strong></td><td>A number used once. Must never repeat under the same key.</td></tr>
<tr><td><strong>OAEP</strong></td><td>The modern padding scheme for RSA encryption.</td></tr>
<tr><td><strong>Padding</strong></td><td>Bytes added to fill the final block of a block cipher.</td></tr>
<tr><td><strong>Per-file key</strong></td><td>A fresh symmetric key for every file encrypted.</td></tr>
<tr><td><strong>Plaintext</strong></td><td>The original readable data.</td></tr>
<tr><td><strong>Protector</strong></td><td>In full-disk encryption, a method of unlocking the volume master key.</td></tr>
<tr><td><strong>RSA</strong></td><td>An asymmetric algorithm based on the difficulty of factoring.</td></tr>
<tr><td><strong>S-box</strong></td><td>The substitution table inside AES. A fixed public constant.</td></tr>
<tr><td><strong>Salt</strong></td><td>A random value mixed into key derivation so identical passwords yield different keys.</td></tr>
<tr><td><strong>Session key</strong></td><td>One symmetric key used for an entire host or session.</td></tr>
<tr><td><strong>Stream cipher</strong></td><td>A cipher producing a keystream XORed with the data. No padding.</td></tr>
<tr><td><strong>Symmetric / asymmetric</strong></td><td>One key for both directions, or a public and private pair.</td></tr>
<tr><td><strong>Tag</strong></td><td>The authentication value produced by an AEAD mode. Usually 16 bytes.</td></tr>
<tr><td><strong>VMK</strong></td><td>Volume Master Key — encrypts the FVEK and is guarded by protectors.</td></tr>
<tr><td><strong>XOR</strong></td><td>The bitwise operation underlying every cipher here. Its own inverse.</td></tr>
<tr><td><strong>XTS</strong></td><td>A mode designed for disk sectors. Used by BitLocker.</td></tr>
</table>

<h2>Things that are commonly stated and are wrong</h2>
<table>
<tr><th>Claim</th><th>Why it is wrong</th></tr>
<tr><td>"High entropy means it is encrypted"</td><td>Compressed formats score the same. Check structure instead.</td></tr>
<tr><td>"High entropy means it is secure"</td><td>AES-ECB scores high and leaks the plaintext.</td></tr>
<tr><td>"Random data always scores 8.0"</td><td>Only in large samples. 128 bytes tops out near 6.55.</td></tr>
<tr><td>"Encrypted files are damaged"</td><td>They are intact. The transformation is reversible with the key.</td></tr>
<tr><td>"We can brute-force the key"</td><td>Above 128 bits the search is physically impossible.</td></tr>
<tr><td>"A zero nonce is always a bug"</td><td>Not when the key never repeats. See module 11.</td></tr>
<tr><td>"RSA-4048"</td><td>Not a real key size. Real ones are 1024, 2048, 3072 and 4096.</td></tr>
<tr><td>"Knowing the algorithm helps decrypt it"</td><td>Every algorithm here is public. The key is the secret.</td></tr>
</table>
""")


