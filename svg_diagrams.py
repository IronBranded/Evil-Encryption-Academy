"""SVG diagram components. Every colour is a CSS variable, so they theme automatically."""


def fig(svg, caption, label):
    return (f'<figure role="img" aria-label="{label}">{svg}'
            f'<figcaption>{caption}</figcaption></figure>')


# ---------------------------------------------------------------- 01 · XOR
def xor_diagram():
    rows = [("0", "0", "0"), ("0", "1", "1"), ("1", "0", "1"), ("1", "1", "0")]
    cells = ""
    for i, (a, b, r) in enumerate(rows):
        y = 74 + i * 34
        cls = "box-c" if r == "1" else "box"
        cells += (f'<rect class="box" x="40" y="{y}" width="46" height="26" rx="3"/>'
                  f'<text class="m" x="63" y="{y+18}" text-anchor="middle" font-size="14">{a}</text>'
                  f'<rect class="box" x="98" y="{y}" width="46" height="26" rx="3"/>'
                  f'<text class="m" x="121" y="{y+18}" text-anchor="middle" font-size="14">{b}</text>'
                  f'<text class="lbl m" x="160" y="{y+18}" text-anchor="middle">=</text>'
                  f'<rect class="{cls}" x="178" y="{y}" width="46" height="26" rx="3"/>'
                  f'<text class="m" x="201" y="{y+18}" text-anchor="middle" font-size="14"'
                  f' font-weight="600">{r}</text>')
    svg = f'''<svg viewBox="0 0 700 250" xmlns="http://www.w3.org/2000/svg">
<text x="40" y="34" font-size="14" font-weight="600">XOR returns 1 only when the inputs differ</text>
<text class="lbl m" x="63" y="62" text-anchor="middle">a</text>
<text class="lbl m" x="121" y="62" text-anchor="middle">b</text>
<text class="lbl m" x="201" y="62" text-anchor="middle">out</text>
{cells}
<line class="arrow" x1="270" y1="70" x2="270" y2="212" stroke-dasharray="3 4"/>
<text x="308" y="86" font-size="14" font-weight="600">Applying it twice undoes it</text>
<rect class="box-p" x="308" y="104" width="118" height="30" rx="4"/>
<text class="m" x="367" y="124" text-anchor="middle" font-size="12.5">plaintext</text>
<text class="lbl m" x="444" y="124" text-anchor="middle">⊕ key</text>
<path class="arrow" d="M470 119 h26" marker-end="url(#ah)"/>
<rect class="box-c" x="504" y="104" width="118" height="30" rx="4"/>
<text class="m" x="563" y="124" text-anchor="middle" font-size="12.5">ciphertext</text>
<rect class="box-c" x="308" y="158" width="118" height="30" rx="4"/>
<text class="m" x="367" y="178" text-anchor="middle" font-size="12.5">ciphertext</text>
<text class="lbl m" x="444" y="178" text-anchor="middle">⊕ key</text>
<path class="arrow" d="M470 173 h26" marker-end="url(#ah)"/>
<rect class="box-p" x="504" y="158" width="118" height="30" rx="4"/>
<text class="m" x="563" y="178" text-anchor="middle" font-size="12.5">plaintext</text>
<text class="tiny" x="308" y="212">the same operation, run again, returns the original</text>
<defs><marker id="ah" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">
<path d="M0 0 L7 3.5 L0 7 z" fill="currentColor" class="lbl"/></marker></defs>
</svg>'''
    return fig(svg, "XOR is its own inverse. Every cipher on this site ends in this operation — "
                    "they differ only in how the key stream is produced.",
               "Truth table for XOR, and a diagram showing that applying XOR twice with the "
               "same key returns the original plaintext.")


# ------------------------------------------------------------- 03 · chaining
def chaining_diagram():
    def blocks(y, chained, cls):
        out = ""
        for i in range(4):
            x = 60 + i * 150
            out += (f'<rect class="box-p" x="{x}" y="{y}" width="96" height="30" rx="4"/>'
                    f'<text class="m" x="{x+48}" y="{y+20}" text-anchor="middle" font-size="11.5">'
                    f'block {i+1}</text>'
                    f'<path class="arrow" d="M{x+48} {y+34} v20" marker-end="url(#ah2)"/>'
                    f'<rect class="{cls}" x="{x}" y="{y+58}" width="96" height="30" rx="4"/>'
                    f'<text class="m" x="{x+48}" y="{y+78}" text-anchor="middle" font-size="11.5">'
                    f'cipher {i+1}</text>')
            if chained and i < 3:
                out += (f'<path class="arrow" d="M{x+96} {y+73} h30 v-45 h24" '
                        f'stroke-dasharray="3 3" marker-end="url(#ah2)"/>')
        return out
    svg = f'''<svg viewBox="0 0 700 400" xmlns="http://www.w3.org/2000/svg">
<text x="60" y="26" font-size="14" font-weight="600" class="fill-c">ECB — every block encrypted on its own</text>
{blocks(44, False, "box-c")}
<text class="tiny" x="60" y="166">no link between blocks, so identical input always gives identical output</text>
<line class="arrow" x1="60" y1="196" x2="660" y2="196" stroke-dasharray="3 4"/>
<text x="60" y="232" font-size="14" font-weight="600" class="fill-p">CBC — each block folded into the next</text>
{blocks(250, True, "box-p")}
<text class="tiny" x="60" y="372">each block depends on the one before it, so repetition disappears</text>
<defs><marker id="ah2" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">
<path d="M0 0 L7 3.5 L0 7 z" fill="currentColor" class="lbl"/></marker></defs>
</svg>'''
    return fig(svg, "The only structural difference between the two modes — and the entire reason "
                    "one of them leaks the picture.",
               "Diagram comparing ECB, where each block is encrypted independently, with CBC, "
               "where each ciphertext block feeds into the next block's encryption.")


# ------------------------------------------------------------ 04 · capacity
def capacity_diagram():
    bars = [("AES-256", 100, "box-p", "no practical limit"),
            ("RSA-4096", 3.2, "box-c", "446 bytes per operation"),
            ("RSA-2048", 1.4, "box-c", "190 bytes per operation")]
    out, y = "", 60
    for name, pct, cls, note in bars:
        w = max(8, pct * 5.4)
        out += (f'<text class="m" x="30" y="{y+19}" font-size="12.5">{name}</text>'
                f'<rect class="{cls}" x="120" y="{y}" width="{w:.0f}" height="28" rx="3"/>'
                f'<text class="lbl m" x="{120+w+12:.0f}" y="{y+19}" font-size="11.5">{note}</text>')
        y += 46
    svg = f'''<svg viewBox="0 0 700 220" xmlns="http://www.w3.org/2000/svg">
<text x="30" y="32" font-size="14" font-weight="600">How much data one operation can handle</text>
{out}
<text class="tiny" x="30" y="204">Bar length is proportional. RSA cannot encrypt a file — only something the size of a key.</text>
</svg>'''
    return fig(svg, "The capacity gap is why asymmetric cryptography never encrypts the data "
                    "itself. It encrypts the key that does.",
               "Bar chart comparing how much data a single operation can encrypt: AES has no "
               "practical limit, RSA-4096 manages 446 bytes, RSA-2048 manages 190 bytes.")


# -------------------------------------------------------------- 05 · layouts
def layout_diagram():
    def bar(y, title, segs):
        out = (f'<text class="m" x="30" y="{y-8}" font-size="12" font-weight="600">{title}</text>')
        x = 30
        for w, cls, lab in segs:
            out += (f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="30" rx="3"/>')
            if lab:
                out += (f'<text class="m" x="{x+w/2}" y="{y+19}" text-anchor="middle" '
                        f'font-size="10">{lab}</text>')
            x += w
        return out
    svg = f'''<svg viewBox="0 0 700 330" xmlns="http://www.w3.org/2000/svg">
{bar(38,  "Footer — most common",   [(430,"box-c","ciphertext"),(130,"box-k","wrapped key"),(80,"box","marker")])}
{bar(112, "Header",                 [(130,"box-k","wrapped key"),(60,"box","IV"),(450,"box-c","ciphertext")])}
{bar(186, "Sidecar — a second file",[(640,"box-c","ciphertext")])}
<rect class="box-k" x="30" y="228" width="220" height="26" rx="3"/>
<text class="m" x="140" y="246" text-anchor="middle" font-size="10">invoice.locked.key</text>
<text class="tiny" x="262" y="246">the wrapped key lives in its own file alongside</text>
<text class="m" x="30" y="292" font-size="12" font-weight="600">One key for the whole host</text>
<rect class="box-c" x="30" y="300" width="430" height="22" rx="3"/>
<rect class="box-c" x="470" y="300" width="90" height="22" rx="3"/>
<text class="tiny" x="574" y="315">one wrapped blob, stored once</text>
</svg>'''
    return fig(svg, "Where the wrapped key is stored is one of the most reliable ways to tell "
                    "two schemes apart — see module 09.",
               "Four diagrams showing where a wrapped key is placed relative to the ciphertext: "
               "appended as a footer, prepended as a header, stored in a separate sidecar file, "
               "or stored once for the whole host.")


# ------------------------------------------------------------- 06 · coverage
def coverage_diagram():
    CELLS, W = 48, 13
    pats = {
        "Full": list(range(CELLS)),
        "Header-only": list(range(5)),
        "Intermittent": [i for i in range(CELLS) if (i // 4) % 2 == 0],
        "Distributed chunks": [0, 1, 23, 24, 46, 47],
    }
    out, y = "", 44
    for name, idx in pats.items():
        out += f'<text class="m" x="30" y="{y-7}" font-size="12" font-weight="600">{name}</text>'
        for i in range(CELLS):
            enc = i in idx
            out += (f'<rect class="{"box-c" if enc else "box-p"}" x="{30+i*W}" y="{y}" '
                    f'width="{W-2}" height="26" rx="2"/>')
        pct = round(len(idx) / CELLS * 100)
        out += f'<text class="lbl m" x="{30+CELLS*W+14}" y="{y+18}" font-size="11">{pct}%</text>'
        y += 62
    svg = f'''<svg viewBox="0 0 700 290" xmlns="http://www.w3.org/2000/svg">
<text x="30" y="24" font-size="14" font-weight="600">The four coverage patterns, across one file</text>
{out}
<text class="tiny" x="30" y="282">red = encrypted   ·   green = untouched   ·   left edge is the start of the file</text>
</svg>'''
    return fig(svg, "Each pattern draws a different shape, and the shape is visible from the "
                    "encrypted file alone.",
               "Four horizontal bars showing coverage patterns across a file: full encryption "
               "covers everything, header-only covers the start, intermittent alternates in "
               "bands, and distributed chunks cover the start, middle and end.")


# ----------------------------------------------------------- 07 · key models
def keymodel_diagram():
    def files(x0, same):
        out = ""
        for i in range(4):
            y = 62 + i * 46
            out += (f'<rect class="box-c" x="{x0}" y="{y}" width="140" height="30" rx="3"/>'
                    f'<text class="m" x="{x0+70}" y="{y+20}" text-anchor="middle" font-size="10.5">'
                    f'file {i+1}</text>')
            cls = "box-k" if same else "box-k"
            out += (f'<rect class="{cls}" x="{x0+150}" y="{y}" width="86" height="30" rx="3"/>'
                    f'<text class="m" x="{x0+193}" y="{y+20}" text-anchor="middle" font-size="9.5">'
                    f'{"3f8a…c4" if same else ["3f8a…c4","91b0…7e","04dd…a1","c7e2…5b"][i]}</text>')
        return out
    svg = f'''<svg viewBox="0 0 700 290" xmlns="http://www.w3.org/2000/svg">
<text x="20" y="26" font-size="13.5" font-weight="600">Session key</text>
<text class="tiny" x="20" y="44">one key for the whole host</text>
{files(20, True)}
<text class="tiny fill-c" x="20" y="270">every wrapped blob is identical</text>
<line class="arrow" x1="350" y1="20" x2="350" y2="256" stroke-dasharray="3 4"/>
<text x="384" y="26" font-size="13.5" font-weight="600">Per-file keys</text>
<text class="tiny" x="384" y="44">a fresh key for every file</text>
{files(384, False)}
<text class="tiny fill-p" x="384" y="270">every wrapped blob differs</text>
</svg>'''
    return fig(svg, "Comparing the trailing blob across a handful of files reveals the key model "
                    "immediately, without decrypting anything.",
               "Two columns of four files each. Under a session key every wrapped key blob is "
               "identical; under per-file keys every blob is different.")


# ------------------------------------------------------------ 08 · bitlocker
def bitlocker_diagram():
    svg = '''<svg viewBox="0 0 700 360" xmlns="http://www.w3.org/2000/svg">
<rect class="box-c" x="180" y="22" width="340" height="42" rx="4"/>
<text x="350" y="48" text-anchor="middle" font-size="13.5" font-weight="600">Your data on the volume</text>
<path class="arrow" d="M350 78 v-10" marker-end="url(#ah3)"/>
<text class="lbl m" x="360" y="88" font-size="11">encrypted with</text>
<rect class="box-k" x="220" y="98" width="260" height="42" rx="4"/>
<text x="350" y="118" text-anchor="middle" font-size="13" font-weight="600">FVEK</text>
<text class="tiny" x="350" y="133" text-anchor="middle">full volume encryption key</text>
<path class="arrow" d="M350 154 v-10" marker-end="url(#ah3)"/>
<text class="lbl m" x="360" y="164" font-size="11">encrypted with</text>
<rect class="box-k" x="220" y="174" width="260" height="42" rx="4" stroke-width="2.6"/>
<text x="350" y="194" text-anchor="middle" font-size="13" font-weight="600">VMK</text>
<text class="tiny" x="350" y="209" text-anchor="middle">volume master key</text>
<text class="m fill-c" x="500" y="200" font-size="12" font-weight="600">← the attack surface</text>
<path class="arrow" d="M350 236 v-14" marker-end="url(#ah3)"/>
<text class="lbl m" x="360" y="246" font-size="11">protected by</text>
<g>
<rect class="box" x="34" y="262" width="140" height="38" rx="4"/>
<text x="104" y="286" text-anchor="middle" font-size="12">TPM</text>
<rect class="box" x="192" y="262" width="140" height="38" rx="4"/>
<text x="262" y="286" text-anchor="middle" font-size="12">TPM + PIN</text>
<rect class="box" x="350" y="262" width="140" height="38" rx="4"/>
<text x="420" y="286" text-anchor="middle" font-size="12">recovery password</text>
<rect class="box" x="508" y="262" width="140" height="38" rx="4"/>
<text x="578" y="286" text-anchor="middle" font-size="12">startup key</text>
</g>
<path class="arrow" d="M104 258 v-14 h474 v14 M262 258 v-14 M420 258 v-14"/>
<text class="tiny" x="34" y="330">Changing a protector rewrites only this bottom layer — a few kilobytes.</text>
<text class="tiny fill-c" x="34" y="348">The volume above it is never re-encrypted, which is why the swap takes seconds.</text>
<defs><marker id="ah3" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">
<path d="M0 0 L7 3.5 L0 7 z" fill="currentColor" class="lbl"/></marker></defs>
</svg>'''
    return fig(svg, "Three layers, and only the bottom one changes during an attack. That is the "
                    "entire mechanism.",
               "Layered diagram: volume data is encrypted by the FVEK, which is encrypted by the "
               "VMK, which is protected by one or more protectors such as TPM, TPM plus PIN, a "
               "recovery password, or a startup key.")


# ----------------------------------------------------------- 09 · signatures
def signature_diagram():
    pats = {"Full": [1]*40, "Header-only": [1]*5 + [0]*35,
            "Intermittent": [1 if (i//3) % 2 == 0 else 0 for i in range(40)],
            "Distributed chunks": [1 if i < 2 or 19 <= i <= 20 or i > 37 else 0 for i in range(40)]}
    out, y = "", 46
    for name, p in pats.items():
        out += f'<text class="m" x="30" y="{y+16}" font-size="12">{name}</text>'
        for i, v in enumerate(p):
            h = 26 if v else 9
            out += (f'<rect class="{"box-c" if v else "box-p"}" x="{200+i*11}" '
                    f'y="{y+26-h}" width="9" height="{h}" rx="1.5"/>')
        y += 52
    svg = f'''<svg viewBox="0 0 700 260" xmlns="http://www.w3.org/2000/svg">
<text x="30" y="26" font-size="14" font-weight="600">Entropy measured in slices across a file</text>
{out}
<text class="tiny" x="30" y="250">tall = high entropy (ciphertext)   ·   short = low entropy (structured data)</text>
</svg>'''
    return fig(svg, "Four profiles, four schemes. Measuring in slices rather than as one number "
                    "is what makes the pattern visible.",
               "Four entropy profiles drawn as bar sequences: full encryption is uniformly high, "
               "header-only is high then low, intermittent alternates, and distributed chunks are "
               "high at the start, middle and end.")


# --------------------------------------------------------- 02 · block/stream
def blockstream_diagram():
    blocks = "".join(
        f'<rect class="box-c" x="{146+i*66}" y="88" width="58" height="30" rx="3"/>'
        f'<text class="m" x="{175+i*66}" y="107" text-anchor="middle" font-size="10">16 B</text>'
        for i in range(6))
    pad = ('<rect class="box-k" x="542" y="88" width="58" height="30" rx="3"/>'
           '<text class="m" x="571" y="107" text-anchor="middle" font-size="10">pad</text>')
    ks = "".join(f'<rect class="box-k" x="{146+i*33}" y="228" width="28" height="30" rx="2"/>'
                 for i in range(13))
    svg = f'''<svg viewBox="0 0 700 300" xmlns="http://www.w3.org/2000/svg">
<text x="30" y="28" font-size="14" font-weight="600" class="fill-c">Block cipher — AES</text>
<text class="tiny" x="30" y="46">the message is cut into fixed 16-byte blocks</text>
<rect class="box-p" x="146" y="56" width="396" height="20" rx="3"/>
<text class="tiny" x="30" y="72">message</text>
<text class="m tiny" x="344" y="70" text-anchor="middle">93 bytes</text>
{blocks}{pad}
<text class="tiny" x="30" y="107">blocks</text>
<text class="tiny fill-k" x="146" y="136">the last block must be padded out, so the output grows to 96 bytes</text>
<line class="arrow" x1="30" y1="164" x2="670" y2="164" stroke-dasharray="3 4"/>
<text x="30" y="196" font-size="14" font-weight="600" class="fill-p">Stream cipher — ChaCha20</text>
<text class="tiny" x="30" y="214">a keystream is generated and XORed byte for byte</text>
<rect class="box-p" x="146" y="196" width="396" height="20" rx="3"/>
<text class="m tiny" x="344" y="210" text-anchor="middle">93 bytes</text>
{ks}
<text class="tiny" x="30" y="247">keystream</text>
<text class="tiny fill-p" x="146" y="284">no blocks and no padding, so the output is exactly 93 bytes</text>
</svg>'''
    return fig(svg, "The size relationship is the giveaway. A block cipher rounds up; a stream "
                    "cipher leaves the length untouched.",
               "Diagram comparing a block cipher, which splits a 93-byte message into six "
               "16-byte blocks plus padding to reach 96 bytes, with a stream cipher, which "
               "produces exactly 93 bytes with no padding.")


# ------------------------------------------------------------ 02 · key space
def keyspace_diagram():
    rows = [("4-digit PIN", "10 thousand", 4, "instant"),
            ("8-char password", "~6 quadrillion", 26, "hours to days"),
            ("56-bit DES key", "72 quadrillion", 30, "hours, since 1998"),
            ("128-bit key", "3.4 × 10³⁸", 62, "not reachable"),
            ("256-bit key", "1.2 × 10⁷⁷", 100, "not reachable")]
    out, y = "", 56
    for name, size, pct, note in rows:
        w = max(6, pct * 3.4)
        cls = "box-c" if pct < 50 else "box-p"
        out += (f'<text class="m" x="24" y="{y+18}" font-size="12">{name}</text>'
                f'<rect class="{cls}" x="160" y="{y}" width="{w:.0f}" height="26" rx="3"/>'
                f'<text class="lbl m" x="{160+w+12:.0f}" y="{y+18}" font-size="11">{size}</text>'
                f'<text class="tiny" x="530" y="{y+18}">{note}</text>')
        y += 40
    svg = f'''<svg viewBox="0 0 700 270" xmlns="http://www.w3.org/2000/svg">
<text x="24" y="32" font-size="14" font-weight="600">How many keys an attacker would have to try</text>
{out}
<text class="tiny" x="24" y="252">Bars are logarithmic — a linear scale could not show both ends on one page.</text>
</svg>'''
    return fig(svg, "Above roughly 128 bits the number stops being a difficulty and becomes a "
                    "physical impossibility. Which is why attacks target key handling instead.",
               "Logarithmic bar chart of key space sizes, from a 4-digit PIN at ten thousand "
               "possibilities up to a 256-bit key at 1.2 times ten to the seventy-seventh.")


# ----------------------------------------------------------- 02 · key origin
def keyorigin_diagram():
    srcs = [("Secure random generator", "box-p", "unpredictable", "no shortcut exists"),
            ("Password + slow KDF", "box-k", "as strong as the password", "guessable if weak"),
            ("Timestamp or process ID", "box-c", "a few million options", "searchable"),
            ("Hardcoded in the software", "box-c", "one value", "read it out")]
    out, y = "", 58
    for name, cls, strength, note in srcs:
        out += (f'<rect class="{cls}" x="24" y="{y}" width="230" height="34" rx="4"/>'
                f'<text x="139" y="{y+22}" text-anchor="middle" font-size="12.5">{name}</text>'
                f'<path class="arrow" d="M262 {y+17} h30" marker-end="url(#ah4)"/>'
                f'<text class="m" x="302" y="{y+14}" font-size="11.5">{strength}</text>'
                f'<text class="tiny" x="302" y="{y+29}">{note}</text>')
        y += 50
    svg = f'''<svg viewBox="0 0 700 280" xmlns="http://www.w3.org/2000/svg">
<text x="24" y="34" font-size="14" font-weight="600">The same AES-256 cipher, four different key origins</text>
{out}
<text class="tiny" x="24" y="272">The cipher is identical in all four cases. Only the origin of the key differs.</text>
<defs><marker id="ah4" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">
<path d="M0 0 L7 3.5 L0 7 z" fill="currentColor" class="lbl"/></marker></defs>
</svg>'''
    return fig(svg, "A scheme is only as strong as the weakest step that produced its key. "
                    "Naming the cipher tells you almost nothing on its own.",
               "Diagram showing four key origins and their resulting strength: a secure random "
               "generator is unpredictable, a password with a slow derivation function is only as "
               "strong as the password, a timestamp or process ID yields a searchable space, and "
               "a hardcoded key is a single readable value.")


# ------------------------------------------------------------- 03 · integrity
def integrity_diagram():
    svg = '''<svg viewBox="0 0 700 300" xmlns="http://www.w3.org/2000/svg">
<text x="24" y="28" font-size="14" font-weight="600">Three different questions, three different tools</text>

<rect class="box-c" x="24" y="48" width="200" height="60" rx="4"/>
<text x="124" y="74" text-anchor="middle" font-size="13" font-weight="600">Encryption</text>
<text class="tiny" x="124" y="92" text-anchor="middle">can anyone read this?</text>
<text class="lbl m" x="240" y="82" font-size="11">confidentiality</text>

<rect class="box-k" x="24" y="124" width="200" height="60" rx="4"/>
<text x="124" y="150" text-anchor="middle" font-size="13" font-weight="600">Hash / MAC</text>
<text class="tiny" x="124" y="168" text-anchor="middle">has this changed?</text>
<text class="lbl m" x="240" y="158" font-size="11">integrity</text>

<rect class="box-p" x="24" y="200" width="200" height="60" rx="4"/>
<text x="124" y="226" text-anchor="middle" font-size="13" font-weight="600">MAC / signature</text>
<text class="tiny" x="124" y="244" text-anchor="middle">who produced this?</text>
<text class="lbl m" x="240" y="234" font-size="11">authenticity</text>

<line class="arrow" x1="400" y1="44" x2="400" y2="266" stroke-dasharray="3 4"/>
<text x="428" y="72" font-size="13" font-weight="600">AEAD does two at once</text>
<rect class="box-p" x="428" y="88" width="242" height="46" rx="4"/>
<text class="m" x="549" y="108" text-anchor="middle" font-size="12">AES-GCM</text>
<text class="tiny" x="549" y="124" text-anchor="middle">encrypt + authenticate</text>
<rect class="box-p" x="428" y="146" width="242" height="46" rx="4"/>
<text class="m" x="549" y="166" text-anchor="middle" font-size="12">ChaCha20-Poly1305</text>
<text class="tiny" x="549" y="182" text-anchor="middle">encrypt + authenticate</text>
<text class="tiny" x="428" y="222">Output carries a 16-byte tag. Change one bit of the</text>
<text class="tiny" x="428" y="238">ciphertext and decryption fails rather than returning</text>
<text class="tiny" x="428" y="254">plausible-looking garbage.</text>
</svg>'''
    return fig(svg, "Confidentiality, integrity and authenticity are separate properties. A scheme "
                    "can have any combination of them.",
               "Diagram separating three properties: encryption provides confidentiality, hashes "
               "and MACs provide integrity, MACs and signatures provide authenticity. AEAD modes "
               "such as AES-GCM and ChaCha20-Poly1305 provide confidentiality and authenticity "
               "together, carrying a 16-byte tag.")
