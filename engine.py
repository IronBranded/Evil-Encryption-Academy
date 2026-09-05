#!/usr/bin/env python3
"""Builds the Evil Encryption Academy site. Run: python3 build_site.py"""
import os
from svg_diagrams import *

NAV = open("assets/_nav.html").read()

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__ — Evil Encryption Academy</title>
<meta name="description" content="__DESC__">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Evil Encryption Academy">
<meta property="og:title" content="__TITLE__">
<meta property="og:description" content="__DESC__">
<meta property="og:image" content="https://ironbranded.github.io/Evil-Encryption-Academy/assets/card.svg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="__TITLE__">
<meta name="twitter:description" content="__DESC__">
<meta name="twitter:image" content="https://ironbranded.github.io/Evil-Encryption-Academy/assets/card.svg">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/academy.css">
<script>
/* Apply the stored theme before first paint so the page never flashes the wrong one. */
(function(){try{var t=localStorage.getItem('eea-theme');
if(t&&t!=='system')document.documentElement.setAttribute('data-theme',t);}catch(e){}})();
</script>
</head>
<body>
<a class="skip" href="#content">Skip to content</a>
<button class="menu-btn ghost" aria-controls="sidenav" aria-expanded="false">Menu</button>
<div class="shell">
<aside class="side" id="sidenav">
__NAV__<div class="side-foot">
  <button class="theme-btn" type="button">System theme</button>
</div>
</aside>
<main id="content">
<p class="crumb"><span>__CRUMB__</span><span>__READ__</span></p>
<h1>__H1__</h1>
<p class="lede">__LEDE__</p>
__BODY__
__DONE__
<div class="pager">__PREV____NEXT__</div>
<p class="kbd-hint">Use <kbd>&larr;</kbd> and <kbd>&rarr;</kbd> to move between modules</p>
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
    import re as _re
    p = f'<a href="{prev[0]}"><em>Previous</em>{prev[1]}</a>' if prev else "<span></span>"
    n = f'<a class="nxt" href="{nxt[0]}"><em>Next</em>{nxt[1]}</a>' if nxt else "<span></span>"
    words = len(_re.sub(r"<[^>]+>", " ", body + lede).split())
    read = f"{max(2, round(words / 190))} min read"
    done = ("" if pid in ("index", "ref") else
            f'<div class="done-bar" data-p="{pid}"><p>Finished this module?</p>'
            f'<button type="button" aria-pressed="false">Mark as read</button></div>')
    html = (HEAD.replace("__NAV__", NAV).replace("__TITLE__", h1)
            .replace("__READ__", read).replace("__DONE__", done)
            .replace("__DESC__", (desc or lede)[:155].replace('"', "'"))
            .replace("__CRUMB__", crumb).replace("__H1__", h1).replace("__LEDE__", lede)
            .replace("__BODY__", body).replace("__PREV__", p).replace("__NEXT__", n)
            .replace("__PID__", pid).replace("__SIM__", sim))
    open(fn, "w", encoding="utf-8").write(html)
    return fn



if __name__ == "__main__":
    import pages          # every page is defined there
    print(f"built {pages.COUNT} pages")
