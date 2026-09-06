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


# -------------------------------------------------------- 07 · key lifecycle
def lifecycle_diagram():
    steps = [
        ("1", "Public key obtained", "hardcoded at build time, or fetched from\nattacker infrastructure at run time", "box-k"),
        ("2", "Ephemeral keypair generated", "a throwaway pair, created on the victim\nmachine for this file or this session", "box-k"),
        ("3", "Symmetric key produced", "from the OS secure random generator, or\nderived by agreement with the public key", "box-c"),
        ("4", "File encrypted, key stored", "bulk encryption runs; the wrapped key or\nephemeral public key is written to the file", "box-c"),
        ("5", "Secrets wiped from memory", "the ephemeral private key and the plaintext\nsymmetric key are overwritten", "box-p"),
    ]
    out, y = "", 44
    for num, title, note, cls in steps:
        out += (f'<circle class="{cls}" cx="42" cy="{y+22}" r="15"/>'
                f'<text class="m" x="42" y="{y+27}" text-anchor="middle" font-size="13"'
                f' font-weight="600">{num}</text>'
                f'<rect class="{cls}" x="74" y="{y}" width="240" height="44" rx="4"/>'
                f'<text x="194" y="{y+27}" text-anchor="middle" font-size="12.5"'
                f' font-weight="600">{title}</text>')
        for i, line in enumerate(note.split("\n")):
            out += f'<text class="tiny" x="330" y="{y+18+i*15}">{line}</text>'
        if num != "5":
            out += f'<path class="arrow" d="M42 {y+40} v22" marker-end="url(#ah5)"/>'
        y += 66
    svg = f'''<svg viewBox="0 0 700 390" xmlns="http://www.w3.org/2000/svg">
<text x="24" y="28" font-size="14" font-weight="600">The key lifecycle, from build time to wiped memory</text>
{out}
<text class="tiny fill-c" x="24" y="378">After step 5 the only surviving key material on the machine is the form that requires the attacker's private key.</text>
<defs><marker id="ah5" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">
<path d="M0 0 L7 3.5 L0 7 z" fill="currentColor" class="lbl"/></marker></defs>
</svg>'''
    return fig(svg, "Five stages. Only stages three and four touch the data; the rest is key "
                    "handling, which is where every meaningful design difference lives.",
               "Five-step flowchart of the key lifecycle: the attacker public key is obtained, an "
               "ephemeral keypair is generated, a symmetric key is produced, the file is encrypted "
               "and the key stored with it, and finally the ephemeral private key and plaintext "
               "symmetric key are wiped from memory.")


# ---------------------------------------------------- 10 · hypervisor layers
def hypervisor_diagram():
    svg = '''<svg viewBox="0 0 700 340" xmlns="http://www.w3.org/2000/svg">
<text x="24" y="26" font-size="14" font-weight="600">Two places to encrypt the same virtual machine</text>

<text class="lbl m" x="24" y="60" font-size="11.5">INSIDE THE GUEST</text>
<rect class="box" x="24" y="70" width="300" height="118" rx="5"/>
<text class="tiny" x="174" y="90" text-anchor="middle">guest operating system</text>
<rect class="box-c" x="44" y="100" width="80" height="30" rx="3"/>
<text class="m" x="84" y="120" text-anchor="middle" font-size="10">file A</text>
<rect class="box-c" x="134" y="100" width="80" height="30" rx="3"/>
<text class="m" x="174" y="120" text-anchor="middle" font-size="10">file B</text>
<rect class="box-c" x="224" y="100" width="80" height="30" rx="3"/>
<text class="m" x="264" y="120" text-anchor="middle" font-size="10">file C</text>
<text class="tiny" x="174" y="152" text-anchor="middle">each file opened, encrypted, written back</text>
<text class="tiny" x="174" y="170" text-anchor="middle">one machine at a time, file by file</text>

<text class="lbl m" x="376" y="60" font-size="11.5">AT THE HYPERVISOR</text>
<rect class="box" x="376" y="70" width="300" height="118" rx="5"/>
<text class="tiny" x="526" y="90" text-anchor="middle">datastore holding whole machines</text>
<rect class="box-c" x="396" y="100" width="80" height="30" rx="3"/>
<text class="m" x="436" y="120" text-anchor="middle" font-size="10">vm1.vmdk</text>
<rect class="box-c" x="486" y="100" width="80" height="30" rx="3"/>
<text class="m" x="526" y="120" text-anchor="middle" font-size="10">vm2.vmdk</text>
<rect class="box-c" x="576" y="100" width="80" height="30" rx="3"/>
<text class="m" x="616" y="120" text-anchor="middle" font-size="10">vm3.vmdk</text>
<text class="tiny" x="526" y="152" text-anchor="middle">each machine is a single flat file</text>
<text class="tiny fill-c" x="526" y="170" text-anchor="middle">encrypt the file, the whole machine is gone</text>

<line class="arrow" x1="350" y1="52" x2="350" y2="196" stroke-dasharray="3 4"/>

<rect class="box-p" x="24" y="212" width="300" height="86" rx="4"/>
<text x="174" y="234" text-anchor="middle" font-size="12.5" font-weight="600">Scope: one guest</text>
<text class="tiny" x="174" y="254" text-anchor="middle">the hypervisor and other machines are untouched</text>
<text class="tiny" x="174" y="272" text-anchor="middle">work scales with the number of files</text>
<text class="tiny" x="174" y="290" text-anchor="middle">the guest must be running and reachable</text>

<rect class="box-c" x="376" y="212" width="300" height="86" rx="4"/>
<text x="526" y="234" text-anchor="middle" font-size="12.5" font-weight="600">Scope: every guest at once</text>
<text class="tiny" x="526" y="254" text-anchor="middle">hundreds of machines from one position</text>
<text class="tiny" x="526" y="272" text-anchor="middle">work scales with the number of machines</text>
<text class="tiny" x="526" y="290" text-anchor="middle">the guests need not be running at all</text>

<text class="tiny" x="24" y="326">The cryptography is identical in both. Only the layer it is applied at differs — and that decides the blast radius.</text>
</svg>'''
    return fig(svg, "Same ciphers, same key model, vastly different scope. Choosing the layer is a "
                    "more consequential decision than choosing the cipher.",
               "Diagram comparing encryption inside a guest operating system, which affects one "
               "machine file by file, with encryption at the hypervisor layer, where each virtual "
               "machine is a single flat disk file and one action affects every machine at once.")


# ------------------------------------------------ 12 · implementation location
def implementation_diagram():
    svg = '''<svg viewBox="0 0 700 320" xmlns="http://www.w3.org/2000/svg">
<text x="24" y="26" font-size="14" font-weight="600">Where the cipher code actually sits</text>

<text class="lbl m" x="24" y="58" font-size="11.5">CALLING THE OPERATING SYSTEM</text>
<rect class="box" x="24" y="68" width="300" height="40" rx="4"/>
<text x="174" y="93" text-anchor="middle" font-size="12.5">the ransomware</text>
<path class="arrow" d="M174 112 v20" marker-end="url(#ah6)"/>
<text class="tiny" x="184" y="126">calls a documented function</text>
<rect class="box-k" x="24" y="138" width="300" height="40" rx="4"/>
<text class="m" x="174" y="163" text-anchor="middle" font-size="11.5">BCryptEncrypt / CryptGenKey</text>
<path class="arrow" d="M174 182 v20" marker-end="url(#ah6)"/>
<rect class="box-c" x="24" y="208" width="300" height="40" rx="4"/>
<text x="174" y="233" text-anchor="middle" font-size="12.5">the OS cipher implementation</text>
<text class="tiny" x="24" y="272">The cipher is a shared system component.</text>
<text class="tiny" x="24" y="290">The program contains no cryptography of its own.</text>

<line class="arrow" x1="350" y1="50" x2="350" y2="300" stroke-dasharray="3 4"/>

<text class="lbl m" x="376" y="58" font-size="11.5">CARRYING ITS OWN COPY</text>
<rect class="box" x="376" y="68" width="300" height="180" rx="4"/>
<text x="526" y="93" text-anchor="middle" font-size="12.5">the ransomware</text>
<rect class="box-c" x="400" y="112" width="252" height="36" rx="3"/>
<text class="m" x="526" y="135" text-anchor="middle" font-size="11">compiled-in cipher (libsodium, tiny-AES)</text>
<rect class="box-c" x="400" y="158" width="252" height="36" rx="3"/>
<text class="m" x="526" y="181" text-anchor="middle" font-size="11">its own key handling</text>
<rect class="box-c" x="400" y="204" width="252" height="32" rx="3"/>
<text class="m" x="526" y="225" text-anchor="middle" font-size="11">its own random source, sometimes</text>
<text class="tiny" x="376" y="272">Everything is inside one file. Nothing is called out to,</text>
<text class="tiny" x="376" y="290">so the program depends on nothing but the kernel.</text>
<defs><marker id="ah6" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">
<path d="M0 0 L7 3.5 L0 7 z" fill="currentColor" class="lbl"/></marker></defs>
</svg>'''
    return fig(svg, "The same AES, reached two different ways. One borrows the system's copy; the "
                    "other brings its own and asks the system for nothing.",
               "Diagram contrasting two implementation choices: calling documented operating "
               "system cryptography functions such as BCryptEncrypt, versus compiling a cipher "
               "library directly into the program so it depends on nothing external.")


# ------------------------------------------------------- 07 · where crypto runs
def implementation_diagram():
    svg = '''<svg viewBox="0 0 700 380" xmlns="http://www.w3.org/2000/svg">
<text x="24" y="26" font-size="14" font-weight="600">The same AES-256, two places to run it</text>

<text x="24" y="60" font-size="13" font-weight="600" class="fill-p">Calling the operating system</text>
<rect class="box-p" x="24" y="72" width="300" height="40" rx="4"/>
<text x="174" y="97" text-anchor="middle" font-size="12.5">the program</text>
<path class="arrow" d="M174 118 v22" marker-end="url(#ah5)"/>
<text class="lbl m" x="184" y="134" font-size="10.5">documented call</text>
<rect class="box-k" x="24" y="146" width="300" height="40" rx="4" stroke-width="2.4"/>
<text x="174" y="165" text-anchor="middle" font-size="12">bcrypt.dll / advapi32.dll</text>
<text class="tiny" x="174" y="179" text-anchor="middle">a named, published boundary</text>
<path class="arrow" d="M174 192 v22" marker-end="url(#ah5)"/>
<rect class="box" x="24" y="220" width="300" height="40" rx="4"/>
<text x="174" y="240" text-anchor="middle" font-size="12">OS cryptographic provider</text>
<text class="tiny" x="174" y="254" text-anchor="middle">the cipher runs here</text>
<text class="tiny fill-p" x="24" y="292">The key crosses a named boundary, so the operation is</text>
<text class="tiny fill-p" x="24" y="308">observable in principle without reading any code.</text>
<text class="tiny" x="24" y="332">Small binary. No cipher constants present.</text>
<text class="tiny" x="24" y="348">Depends on what the OS provides.</text>

<line class="arrow" x1="360" y1="46" x2="360" y2="358" stroke-dasharray="3 4"/>

<text x="392" y="60" font-size="13" font-weight="600" class="fill-c">Carrying its own</text>
<rect class="box-c" x="392" y="72" width="284" height="188" rx="4"/>
<text x="534" y="97" text-anchor="middle" font-size="12.5">the program</text>
<line class="arrow" x1="410" y1="112" x2="658" y2="112" stroke-dasharray="2 3"/>
<rect class="box-c" x="410" y="126" width="248" height="34" rx="3"/>
<text x="534" y="147" text-anchor="middle" font-size="11.5">compiled-in cipher code</text>
<rect class="box-c" x="410" y="170" width="248" height="34" rx="3"/>
<text x="534" y="191" text-anchor="middle" font-size="11.5">the cipher runs here too</text>
<text class="tiny" x="410" y="228">no call leaves the program</text>
<text class="tiny fill-c" x="392" y="292">Nothing crosses a boundary. The key is only ever an</text>
<text class="tiny fill-c" x="392" y="308">address inside the program.</text>
<text class="tiny" x="392" y="332">Larger binary. Cipher constants present.</text>
<text class="tiny" x="392" y="348">Runs anywhere, identically.</text>
<defs><marker id="ah5" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">
<path d="M0 0 L7 3.5 L0 7 z" fill="currentColor" class="lbl"/></marker></defs>
</svg>'''
    return fig(svg, "Identical cryptography, two architectures. The difference is whether the key "
                    "ever crosses a named interface.",
               "Diagram comparing two implementations. On the left the program calls the operating "
               "system's cryptographic libraries, so the key crosses a documented boundary. On the "
               "right the cipher is compiled into the program, so nothing crosses a boundary and "
               "the key is only ever an address inside the process.")


# ------------------------------------------------------------ 08 · key lifecycle
def lifecycle_diagram():
    svg = '''<svg viewBox="0 0 700 470" xmlns="http://www.w3.org/2000/svg">
<text x="24" y="24" font-size="14" font-weight="600">The key lifecycle, and where it forks</text>

<rect class="box-k" x="180" y="42" width="340" height="42" rx="4"/>
<text x="350" y="62" text-anchor="middle" font-size="12.5" font-weight="600">1 · Operator public key reaches the host</text>
<text class="tiny" x="350" y="76" text-anchor="middle">embedded at build time, or fetched from a server</text>
<path class="arrow" d="M350 96 v18" marker-end="url(#ah6)"/>

<rect class="box-p" x="180" y="118" width="340" height="42" rx="4"/>
<text x="350" y="138" text-anchor="middle" font-size="12.5" font-weight="600">2 · A symmetric key is produced on the host</text>
<text class="tiny" x="350" y="152" text-anchor="middle">from the secure random generator — the file key</text>
<path class="arrow" d="M350 172 v18" marker-end="url(#ah6)"/>

<rect class="box-c" x="180" y="194" width="340" height="38" rx="4"/>
<text x="350" y="218" text-anchor="middle" font-size="12.5" font-weight="600">3 · The file is encrypted with it</text>

<path class="arrow" d="M350 244 v14 M180 258 h340 M240 258 v18 M460 258 v18"
      marker-end="url(#ah6)"/>
<text class="lbl m" x="350" y="254" text-anchor="middle" font-size="10.5">two designs from here</text>

<rect class="box-k" x="60" y="282" width="220" height="62" rx="4"/>
<text x="170" y="302" text-anchor="middle" font-size="12" font-weight="600">4a · Wrap it</text>
<text class="tiny" x="170" y="317" text-anchor="middle">file key encrypted under the</text>
<text class="tiny" x="170" y="330" text-anchor="middle">operator public key</text>

<rect class="box-k" x="352" y="282" width="220" height="62" rx="4"/>
<text x="462" y="302" text-anchor="middle" font-size="12" font-weight="600">4b · Agree it</text>
<text class="tiny" x="462" y="317" text-anchor="middle">ephemeral keypair generated;</text>
<text class="tiny" x="462" y="330" text-anchor="middle">file key derived, never wrapped</text>

<path class="arrow" d="M170 350 v16 M462 350 v16" marker-end="url(#ah6)"/>
<rect class="box" x="60" y="370" width="220" height="40" rx="4"/>
<text x="170" y="386" text-anchor="middle" font-size="11.5">5a · store the wrapped key</text>
<text class="tiny" x="170" y="400" text-anchor="middle">256 or 512 bytes of ciphertext</text>
<rect class="box" x="352" y="370" width="220" height="40" rx="4"/>
<text x="462" y="386" text-anchor="middle" font-size="11.5">5b · store the ephemeral public key</text>
<text class="tiny" x="462" y="400" text-anchor="middle">32 bytes, and harmless</text>

<rect class="box-c" x="180" y="424" width="340" height="36" rx="4" stroke-width="2.4"/>
<text x="350" y="440" text-anchor="middle" font-size="12" font-weight="600">6 · Everything secret is erased from memory</text>
<text class="tiny" x="350" y="453" text-anchor="middle">the file key, and on the right the ephemeral private key too</text>
<defs><marker id="ah6" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">
<path d="M0 0 L7 3.5 L0 7 z" fill="currentColor" class="lbl"/></marker></defs>
</svg>'''
    return fig(svg, "Steps 1 to 3 and step 6 are common to both designs. Step 4 is where they "
                    "diverge, and it decides what ends up on disk.",
               "Flowchart of the key lifecycle. The operator public key reaches the host, a "
               "symmetric key is generated locally, the file is encrypted, then the design forks: "
               "either the file key is wrapped under the public key and the wrapped blob stored, "
               "or an ephemeral keypair is generated and the file key derived by agreement with "
               "only the ephemeral public key stored. Finally all secret material is erased from "
               "memory.")


# --------------------------------------------------------- 12 · hypervisor
def hypervisor_diagram():
    svg = '''<svg viewBox="0 0 700 340" xmlns="http://www.w3.org/2000/svg">
<text x="24" y="24" font-size="14" font-weight="600">Two layers to attack, very different reach</text>

<text x="24" y="58" font-size="12.5" font-weight="600" class="fill-p">Inside each guest</text>
<g>
<rect class="box" x="24" y="70" width="140" height="94" rx="4"/>
<text class="tiny" x="94" y="88" text-anchor="middle">guest OS</text>
<rect class="box-c" x="36" y="98" width="116" height="18" rx="2"/>
<rect class="box-c" x="36" y="122" width="116" height="18" rx="2"/>
<rect class="box-p" x="36" y="146" width="116" height="12" rx="2"/>
<rect class="box" x="176" y="70" width="140" height="94" rx="4"/>
<text class="tiny" x="246" y="88" text-anchor="middle">guest OS</text>
<rect class="box-p" x="188" y="98" width="116" height="18" rx="2"/>
<rect class="box-p" x="188" y="122" width="116" height="18" rx="2"/>
<rect class="box-p" x="188" y="146" width="116" height="12" rx="2"/>
</g>
<text class="tiny" x="24" y="186">Runs once per machine. Each guest must be reached</text>
<text class="tiny" x="24" y="200">separately, and each one can see it happening.</text>

<line class="arrow" x1="352" y1="44" x2="352" y2="318" stroke-dasharray="3 4"/>

<text x="384" y="58" font-size="12.5" font-weight="600" class="fill-c">At the hypervisor</text>
<rect class="box" x="384" y="70" width="132" height="94" rx="4"/>
<text class="tiny" x="450" y="88" text-anchor="middle">guest OS</text>
<text class="tiny" x="450" y="126" text-anchor="middle">untouched</text>
<rect class="box" x="528" y="70" width="132" height="94" rx="4"/>
<text class="tiny" x="594" y="88" text-anchor="middle">guest OS</text>
<text class="tiny" x="594" y="126" text-anchor="middle">untouched</text>
<path class="arrow" d="M450 172 v14 M594 172 v14" marker-end="url(#ah7)"/>
<rect class="box-c" x="384" y="192" width="276" height="46" rx="4" stroke-width="2.4"/>
<text x="522" y="212" text-anchor="middle" font-size="12">the files backing those guests</text>
<text class="tiny" x="522" y="228" text-anchor="middle">one .vmdk per virtual disk, on shared storage</text>
<text class="tiny fill-c" x="384" y="266">Runs once for the whole host. The guests are not</text>
<text class="tiny fill-c" x="384" y="280">touched, entered, or even aware — their disks are</text>
<text class="tiny fill-c" x="384" y="294">simply files, and the files are what gets encrypted.</text>
<defs><marker id="ah7" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">
<path d="M0 0 L7 3.5 L0 7 z" fill="currentColor" class="lbl"/></marker></defs>
</svg>'''
    return fig(svg, "The guests are irrelevant to the second approach. From the hypervisor's "
                    "perspective a virtual machine is a file, and files are easy to encrypt.",
               "Diagram contrasting two approaches. Encrypting inside each guest operating system "
               "requires reaching every machine separately. Encrypting at the hypervisor layer "
               "targets the virtual disk files backing those guests, so one operation covers every "
               "machine on the host without entering any of them.")


# ------------------------------------------------------- 07 · where crypto lives
def cryptolocation_diagram():
    svg = '''<svg viewBox="0 0 700 340" xmlns="http://www.w3.org/2000/svg">
<text x="24" y="26" font-size="14" font-weight="600">Two places the cipher can physically be</text>

<text class="m fill-c" x="24" y="58" font-size="12.5" font-weight="600">A · Calls the operating system</text>
<rect class="box" x="24" y="70" width="300" height="34" rx="4"/>
<text x="174" y="92" text-anchor="middle" font-size="12">the program</text>
<path class="arrow" d="M174 108 v18" marker-end="url(#ah5)"/>
<text class="lbl m" x="184" y="122" font-size="10.5">BCryptEncrypt</text>
<rect class="box-c" x="24" y="130" width="300" height="34" rx="4"/>
<text x="174" y="152" text-anchor="middle" font-size="12">bcrypt.dll — a shared OS library</text>
<path class="arrow" d="M174 168 v18" marker-end="url(#ah5)"/>
<rect class="box-k" x="24" y="190" width="300" height="34" rx="4"/>
<text x="174" y="212" text-anchor="middle" font-size="12">AES-NI instructions in the CPU</text>
<text class="tiny" x="24" y="248">The cipher is not in the program at all. It lives in a</text>
<text class="tiny" x="24" y="264">library shared by everything on the machine, and the</text>
<text class="tiny" x="24" y="280">boundary between them is a named, documented call.</text>

<line class="arrow" x1="356" y1="46" x2="356" y2="300" stroke-dasharray="3 4"/>

<text class="m fill-p" x="380" y="58" font-size="12.5" font-weight="600">B · Carries its own copy</text>
<rect class="box" x="380" y="70" width="296" height="154" rx="4"/>
<text x="528" y="92" text-anchor="middle" font-size="12">the program</text>
<rect class="box-p" x="400" y="106" width="256" height="30" rx="3"/>
<text class="m" x="528" y="126" text-anchor="middle" font-size="11">compiled-in AES / ChaCha20</text>
<rect class="box-p" x="400" y="144" width="256" height="30" rx="3"/>
<text class="m" x="528" y="164" text-anchor="middle" font-size="11">its own key handling</text>
<rect class="box-p" x="400" y="182" width="256" height="30" rx="3"/>
<text class="m" x="528" y="202" text-anchor="middle" font-size="11">its own random source</text>
<text class="tiny" x="380" y="248">Everything is inside one file. There is no call to</text>
<text class="tiny" x="380" y="264">watch and no boundary to observe, because the</text>
<text class="tiny" x="380" y="280">cipher never leaves the program.</text>

<text class="tiny" x="24" y="322">Both produce identical ciphertext. The difference is entirely structural.</text>
<defs><marker id="ah5" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">
<path d="M0 0 L7 3.5 L0 7 z" fill="currentColor" class="lbl"/></marker></defs>
</svg>'''
    return fig(svg, "The same AES, in two architectures. One borrows the operating system's copy; "
                    "the other brings its own.",
               "Diagram contrasting a program that calls a shared operating-system crypto library, "
               "which in turn uses CPU instructions, with a program that carries a compiled-in "
               "copy of the cipher, its own key handling and its own random source.")


# ---------------------------------------------------------- 08 · key lifecycle
def lifecycle_diagram():
    steps = [
        ("1", "Public key obtained", "hardcoded at build time, or fetched from a server", "box-k"),
        ("2", "Ephemeral pair generated", "a throwaway keypair, on the victim machine", "box-p"),
        ("3", "Symmetric key produced", "32 bytes from the secure random generator", "box-p"),
        ("4", "File encrypted", "AES or ChaCha20 over the contents", "box-c"),
        ("5", "Symmetric key protected", "wrapped with the public key, or derived by agreement", "box-k"),
        ("6", "Result written to the file", "the wrapped key or ephemeral public key is appended", "box"),
        ("7", "Local secrets wiped", "the plaintext key and ephemeral private key are erased", "box-c"),
    ]
    out, y = "", 52
    for n, title, note, cls in steps:
        out += (f'<circle cx="40" cy="{y+17}" r="13" class="{cls}"/>'
                f'<text class="m" x="40" y="{y+22}" text-anchor="middle" font-size="12" '
                f'font-weight="600">{n}</text>'
                f'<rect class="{cls}" x="68" y="{y}" width="230" height="34" rx="4"/>'
                f'<text x="183" y="{y+22}" text-anchor="middle" font-size="12">{title}</text>'
                f'<text class="tiny" x="312" y="{y+22}">{note}</text>')
        if n != "7":
            out += f'<path class="arrow" d="M40 {y+32} v14" marker-end="url(#ah6)"/>'
        y += 46
    svg = f'''<svg viewBox="0 0 700 400" xmlns="http://www.w3.org/2000/svg">
<text x="24" y="28" font-size="14" font-weight="600">The key, from creation to erasure</text>
{out}
<rect x="60" y="128" width="252" height="186" rx="5" fill="none" class="fill-p"
      stroke="currentColor" stroke-dasharray="4 4" opacity="0.5"/>
<text class="tiny fill-p" x="322" y="376">Between steps 3 and 7 the plaintext key exists on the victim machine.</text>
<text class="tiny" x="322" y="392">Before step 3 it does not exist; after step 7 no local copy remains.</text>
<defs><marker id="ah6" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">
<path d="M0 0 L7 3.5 L0 7 z" fill="currentColor" class="lbl"/></marker></defs>
</svg>'''
    return fig(svg, "Seven steps. Only two of them involve the file at all — the rest is key "
                    "handling, which is where every interesting question lives.",
               "Flowchart of the key lifecycle: public key obtained, ephemeral pair generated, "
               "symmetric key produced, file encrypted, symmetric key protected, result written "
               "to the file, local secrets wiped.")


# ------------------------------------------------------------ 12 · virtualisation
def hypervisor_diagram():
    svg = '''<svg viewBox="0 0 700 360" xmlns="http://www.w3.org/2000/svg">
<text x="24" y="26" font-size="14" font-weight="600">Three layers at which the same data can be encrypted</text>

<rect class="box" x="24" y="44" width="652" height="96" rx="5"/>
<text class="m fill-c" x="40" y="66" font-size="12" font-weight="600">A · Inside the guest</text>
<rect class="box-c" x="40" y="76" width="190" height="48" rx="4"/>
<text x="135" y="96" text-anchor="middle" font-size="11.5">guest operating system</text>
<text class="tiny" x="135" y="112" text-anchor="middle">encrypts its own files</text>
<text class="tiny" x="252" y="94">One guest affected. Files inside that VM are encrypted</text>
<text class="tiny" x="252" y="110">individually, exactly as on a physical machine.</text>

<rect class="box" x="24" y="152" width="652" height="96" rx="5"/>
<text class="m fill-k" x="40" y="174" font-size="12" font-weight="600">B · At the hypervisor, per virtual machine</text>
<rect class="box-k" x="40" y="184" width="190" height="48" rx="4"/>
<text x="135" y="204" text-anchor="middle" font-size="11.5">VM encryption feature</text>
<text class="tiny" x="135" y="220" text-anchor="middle">a supported platform function</text>
<text class="tiny" x="252" y="202">Every VM on the host, in one action. The guests are</text>
<text class="tiny" x="252" y="218">untouched internally — their disks are encrypted from outside.</text>

<rect class="box" x="24" y="260" width="652" height="96" rx="5"/>
<text class="m fill-c" x="40" y="282" font-size="12" font-weight="600">C · At the datastore, on the raw files</text>
<rect class="box-c" x="40" y="292" width="190" height="48" rx="4"/>
<text class="m" x="135" y="312" text-anchor="middle" font-size="11.5">.vmdk / .vmx files</text>
<text class="tiny" x="135" y="328" text-anchor="middle">just files on a filesystem</text>
<text class="tiny" x="252" y="310">A virtual disk is a file. Encrypting it needs no knowledge of</text>
<text class="tiny" x="252" y="326">virtualisation at all — only the ability to write to the datastore.</text>
</svg>'''
    return fig(svg, "Moving one layer down multiplies the effect. The lowest layer requires the "
                    "least understanding of what is being encrypted.",
               "Three stacked layers: encryption inside the guest operating system affects one "
               "virtual machine; encryption by the hypervisor's own VM encryption feature affects "
               "every VM on the host; encryption of the raw virtual disk files on the datastore "
               "requires no knowledge of virtualisation at all.")
