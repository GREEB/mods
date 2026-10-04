#!/usr/bin/env python3
"""Builds the download page (GitHub Pages: https://greeb.github.io/mods/) into docs/.

    python3 build_site.py

Takes the release zips from each mod's dist/release folder, the thumbnails and avatar from
~/deadlock-branding/out, and the per-mod texts from ~/deadlock-branding/descriptions.py.
To publish a new version: build the mod's release zip, run this, commit and push.
"""
import html
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")
BRANDING = os.path.join(HOME, "deadlock-branding")
DOCS = os.path.join(HERE, "docs")
REPO = "https://github.com/GREEB/mods"

sys.path.insert(0, BRANDING)
import descriptions  # noqa: E402  (per-mod GameBanana texts, reused here)

# key: thumbnail name in deadlock-branding/out; folder: entry in descriptions.MODS
MODS = [
    {"key": "hudfit", "folder": "HUD Fit", "name": "HUD Fit", "accent": "#ffc83c",
     "tagline": "Move, resize and de-stretch every HUD element, live in game.",
     "dist": os.path.join(HOME, "deadlock-hudfit/dist/release"), "prefix": "hud_fit_v",
     "source": "https://github.com/GREEB/deadlock-hudfit"},
    {"key": "aspect43", "folder": "4-3 Video", "name": "4:3 Video", "accent": "#b48cff",
     "tagline": "Adds a 4x3 aspect ratio button to the video settings, without hiding new settings.",
     "dist": os.path.join(HOME, "deadlock-4x3/dist/release"), "prefix": "aspect_4x3_v"},
    {"key": "heroselect", "folder": "Hero Select Plus", "name": "Hero Select Plus", "accent": "#4fd1c5",
     "tagline": "Hero names, classes, search and filters on the hero select screen.",
     "dist": os.path.join(HOME, "deadlockmod/dist/release"), "prefix": "hero_select_plus_v"},
]


def version_key(v):
    return [int(x) for x in v.split(".")]


def latest_zip(m):
    found = []
    for f in os.listdir(m["dist"]):
        r = re.match(re.escape(m["prefix"]) + r"([0-9.]+)\.zip$", f)
        if r:
            found.append((version_key(r.group(1)), r.group(1), f))
    if not found:
        raise SystemExit("no release zip in " + m["dist"])
    found.sort()
    return found[-1][1], found[-1][2]


def details_html(folder):
    """The GameBanana description minus its GameBanana-only header (AI note) and footer."""
    body = descriptions.MODS[folder]["html"]
    body = body.split("<hr><i>Made by")[0]
    return body


def jpg(src, dst, width):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-vf", "scale=%d:-2" % width, "-q:v", "3", dst],
                   check=True)


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>dirtytomat0 Deadlock Mods</title>
<meta name="description" content="Deadlock mods by dirtytomat0: HUD Fit, 4:3 Video, Hero Select Plus. Free downloads.">
<link rel="icon" href="img/avatar.png">
<style>
:root {{ --bg:#0f0d0b; --panel:#1a1612; --line:#3a3026; --gold:#c9a45c; --text:#efe6d6; --muted:#a89a82; }}
* {{ box-sizing:border-box }}
body {{ margin:0; background:radial-gradient(ellipse at 50% 0%, #2a211a 0%, var(--bg) 60%) fixed; background-color:var(--bg);
       color:var(--text); font:16px/1.6 "Bahnschrift","Segoe UI",system-ui,sans-serif }}
a {{ color:var(--gold) }}
.wrap {{ max-width:1100px; margin:0 auto; padding:0 16px }}
header {{ text-align:center; padding:48px 0 24px }}
header img {{ width:88px; height:88px; border-radius:20px }}
header h1 {{ margin:12px 0 4px; font-size:34px; letter-spacing:1px }}
header h1 span {{ color:#d4573a }}
header p {{ margin:0; color:var(--muted) }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(300px, 1fr)); gap:20px; margin:28px 0 }}
.card {{ background:var(--panel); border:1px solid var(--line); border-radius:14px; overflow:hidden; display:flex; flex-direction:column }}
.card img {{ width:100%; aspect-ratio:16/9; object-fit:cover; display:block; background:#000 }}
.body {{ padding:16px 18px 18px; display:flex; flex-direction:column; gap:10px; flex:1 }}
.body h2 {{ margin:0; font-size:24px }}
.body p {{ margin:0; color:var(--muted) }}
.meta {{ font-size:13px; color:var(--muted) }}
.btn {{ display:block; text-align:center; padding:11px 14px; border-radius:9px; font-weight:700; text-decoration:none;
       color:#14110e; background:var(--accent); margin-top:auto }}
.btn:hover {{ filter:brightness(1.1) }}
details {{ border-top:1px solid var(--line); padding-top:8px }}
summary {{ cursor:pointer; color:var(--gold) }}
details .desc {{ font-size:14px; color:#d8ccb6 }}
details .desc h2 {{ font-size:17px; margin:14px 0 4px; color:var(--text) }}
details .desc h3 {{ font-size:15px; margin:12px 0 4px; color:var(--text) }}
details .desc ul {{ padding-left:20px; margin:4px 0 }}
details .desc hr {{ border:0; border-top:1px solid var(--line) }}
.GreenColor {{ color:#8fd46a }} .RedColor {{ color:#ff7a68 }} .OrangeColor {{ color:#ffad5a }}
.install {{ background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:6px 22px 14px; margin-bottom:28px }}
.install h2 {{ font-size:22px; margin:14px 0 6px }}
.install ol {{ padding-left:22px; margin:6px 0 }}
code {{ background:#0c0a08; padding:1px 6px; border-radius:5px; font-size:14px }}
footer {{ text-align:center; color:var(--muted); font-size:13px; padding:10px 0 40px }}
</style>
</head>
<body>
<div class="wrap">
<header>
  <img src="img/avatar.png" alt="">
  <h1>dirtytomat<span>0</span></h1>
  <p>Deadlock mods &middot; free downloads</p>
</header>

<div class="grid">
{cards}
</div>

<section class="install">
  <h2>Install with Deadlock Mod Manager</h2>
  <ol>
    <li>Download the mod's <code>.zip</code> above (don't unzip it).</li>
    <li>Open <a href="https://deadlockmods.app/">Deadlock Mod Manager</a> and choose <b>Add Local Mod</b>.</li>
    <li>Drop the zip in, give it a name, add it, and turn it on.</li>
  </ol>
  <h2>Install with Grimoire</h2>
  <ol>
    <li>Download the mod's <code>.zip</code> above.</li>
    <li>In <a href="https://grimoiremods.com/">Grimoire</a>, open <b>Installed</b> and choose <b>Import Local Mods</b>.</li>
    <li>Pick the zip and turn the mod on.</li>
  </ol>
  <h2>Install by hand</h2>
  <ol>
    <li>Unzip the download: it contains <code>pak01_dir.vpk</code>.</li>
    <li>Copy it to <code>Steam/steamapps/common/Deadlock/game/citadel/addons</code> and rename it to the next free number
        (<code>pak01_dir.vpk</code>, <code>pak02_dir.vpk</code>, ...; the game stops at the first missing number).</li>
    <li>The game only loads that folder once mods are enabled in <code>gameinfo.gi</code>; the Mod Manager does this for you.</li>
  </ol>
  <h2>Updating</h2>
  <p>Download the new zip from this page and add it again (remove the old one in your mod manager first).</p>
</section>

<footer>Questions or bugs: <a href="{repo}/issues">open an issue on GitHub</a> &middot; Not affiliated with Valve.</footer>
</div>
</body>
</html>
"""

CARD = """<article class="card" style="--accent:{accent}">
  <img src="img/{key}.jpg" alt="{name}" loading="lazy">
  <div class="body">
    <h2>{name}</h2>
    <p>{tagline}</p>
    <div class="meta">Version {version} &middot; {size} KB{source}</div>
    <a class="btn" href="downloads/{zip}" download>Download {name} {version}</a>
    <details><summary>Details</summary><div class="desc">{details}</div></details>
  </div>
</article>"""


def main():
    os.makedirs(os.path.join(DOCS, "img"), exist_ok=True)
    os.makedirs(os.path.join(DOCS, "downloads"), exist_ok=True)
    shutil.copyfile(os.path.join(BRANDING, "out/avatar_dark_256.png"), os.path.join(DOCS, "img/avatar.png"))
    cards, keep = [], set()
    for m in MODS:
        version, zipname = latest_zip(m)
        shutil.copyfile(os.path.join(m["dist"], zipname), os.path.join(DOCS, "downloads", zipname))
        keep.add(zipname)
        jpg(os.path.join(BRANDING, "out", m["key"] + ".png"), os.path.join(DOCS, "img", m["key"] + ".jpg"), 960)
        size = os.path.getsize(os.path.join(DOCS, "downloads", zipname)) // 1024 + 1
        source = ' &middot; <a href="%s">source</a>' % m["source"] if m.get("source") else ""
        cards.append(CARD.format(accent=m["accent"], key=m["key"], name=html.escape(m["name"]),
                                 tagline=html.escape(m["tagline"]), version=version, size=size, source=source,
                                 zip=zipname, details=details_html(m["folder"])))
        print("%-17s v%s  %s" % (m["name"], version, zipname))
    # old versions are dropped from the site (the git history keeps them)
    for f in os.listdir(os.path.join(DOCS, "downloads")):
        if f not in keep:
            os.remove(os.path.join(DOCS, "downloads", f))
    with open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8") as f:
        f.write(PAGE.format(cards="\n".join(cards), repo=REPO))
    open(os.path.join(DOCS, ".nojekyll"), "w").close()
    print("wrote", os.path.join(DOCS, "index.html"))


if __name__ == "__main__":
    main()
