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
STEAM_SHOTS = "/mnt/c/Program Files (x86)/Steam/userdata/43593840/760/remote/1422450/screenshots"

sys.path.insert(0, BRANDING)
import descriptions  # noqa: E402  (per-mod GameBanana texts, reused here)

# key: thumbnail name in deadlock-branding/out; folder: entry in descriptions.MODS
MODS = [
    {"key": "hudfit", "folder": "HUD Fit", "name": "HUD Fit", "accent": "#ffc83c",
     "tagline": "Move, resize and de-stretch every HUD element, live in game.",
     "points": ["De-stretch the HUD for 4:3 stretched (or 5:4, 16:10)",
                "Scale the whole UI, or each element on its own, including the shop",
                "Drag any of 23 elements on the real HUD, with snapping and centering",
                "Hide, lock and reset elements; save and share layouts",
                "Fixes the health bar disappearing at 4:3"],
     "dist": os.path.join(HOME, "deadlock-hudfit/dist/release"), "prefix": "hud_fit_v",
     "shots": [("20261003084800_1.jpg", "Show all outlines: every element you can move and resize"),
               ("20261003085728_1.jpg", "Before: the stock HUD at 4:3 stretched"),
               ("20261003085833_1.jpg", "After: de-stretched, resized and a filter, with HUD Fit"),
               ("20261003082723_1.jpg", "The editor opens over the live HUD (Esc, then HUD Fit)"),
               ("20261003085741_1.jpg", "Layers: show, hide, lock or reset every element")],
     "compare": ("20261003085728_1.jpg", "20261003085833_1.jpg"),
     # these were taken at 4:3 stretched: show them 16:9 wide, as they look on the monitor
     "stretch43": True},
    {"key": "aspect43", "folder": "4-3 Video", "name": "4:3 Video", "accent": "#b48cff",
     "tagline": "Adds a 4x3 aspect ratio button to the video settings, without hiding new settings.",
     "points": ["4x3 next to 16:9, 16:10 and 21:9 in Settings \u2192 Video",
                "Lists the 4:3 resolutions your driver offers (1600x1200, 1440x1080...)",
                "Never replaces the settings screen, so new game settings keep showing",
                "Made to be used with HUD Fit"],
     "dist": os.path.join(HOME, "deadlock-4x3/dist/release"), "prefix": "aspect_4x3_v"},
    {"key": "heroselect", "folder": "Hero Select Plus", "name": "Hero Select Plus", "accent": "#4fd1c5",
     "tagline": "Hero names, classes, search and filters on the hero select screen.",
     "points": ["Names and colour-coded classes on every hero card",
                "Search by name, class, tag, weapon type or difficulty",
                "Class filters and a Beginner button",
                "Hover details: role, difficulty and playstyle"],
     "dist": os.path.join(HOME, "deadlockmod/dist/release"), "prefix": "hero_select_plus_v",
     "shots": [(os.path.join(HERE, "shots/heroselect_grid.png"), "Class on every card, search box, class and Beginner filters"),
               (os.path.join(HERE, "shots/heroselect_closeup.png"), "Close-up: hero names and colour-coded classes")]},
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


def jpg(src, dst, width, stretch=False):
    """Resized copy. stretch: a 4:3 capture is shown 16:9 wide, the way a 4:3 stretched player sees it."""
    vf = "scale=%d:%d" % (width, width * 9 // 16) if stretch else "scale='min(%d,iw)':-2" % width
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-vf", vf, "-q:v", "3", dst], check=True)


def is_43(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height", "-of", "csv=p=0", path],
                         capture_output=True, text=True, check=True).stdout.strip().split(",")
    return int(out[0]) / int(out[1]) < 1.5


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Deadlock Mods: HUD Fit (de-stretch / scale HUD), 4:3 Video, Hero Select Plus</title>
<meta name="description" content="Free Deadlock mods: HUD Fit de-stretches, scales and moves the HUD and shop for 4:3 stretched or any resolution; 4:3 Video adds a 4x3 aspect ratio option; Hero Select Plus adds hero search and class filters.">
<meta property="og:title" content="Deadlock Mods: HUD Fit, 4:3 Video, Hero Select Plus">
<meta property="og:description" content="De-stretch and scale the Deadlock HUD, add a 4x3 aspect ratio, find heroes faster. Free downloads.">
<meta property="og:image" content="https://greeb.github.io/mods/img/hudfit.jpg">
<link rel="icon" href="img/logo.png">
<script type="application/ld+json">{faq_ld}</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root {{ --bg:#0e0c0a; --panel:#17130f; --panel2:#1f1a14; --line:#2f271f; --gold:#d6ae62; --text:#f1e9db; --muted:#a3967f;
        --tomato:#d4573a; --head:"Rajdhani","Bahnschrift",system-ui,sans-serif }}
* {{ box-sizing:border-box }}
html {{ scroll-behavior:smooth; scroll-padding-top:72px }}
body {{ margin:0; background:var(--bg); color:var(--text); font:16px/1.65 "Inter","Segoe UI",system-ui,sans-serif }}
a {{ color:var(--gold) }}
.wrap {{ max-width:1120px; margin:0 auto; padding:0 20px }}

/* nav */
nav {{ position:sticky; top:0; z-index:10; background:#0e0c0acc; backdrop-filter:blur(10px); border-bottom:1px solid var(--line) }}
nav .wrap {{ display:flex; align-items:center; gap:24px; height:60px }}
.brand {{ display:flex; align-items:center; text-decoration:none }}
.brand img {{ width:40px; height:40px; display:block; transition:transform .2s }}
.brand:hover img {{ transform:rotate(-12deg) scale(1.06) }}
nav ul {{ display:flex; gap:4px; list-style:none; margin:0 0 0 auto; padding:0 }}
nav ul a {{ display:block; padding:6px 12px; border-radius:8px; color:var(--muted); text-decoration:none; font-weight:500; font-size:15px }}
nav ul a:hover {{ color:var(--text); background:var(--panel2) }}
@media (max-width:720px) {{ nav ul .opt {{ display:none }} }}

/* hero */
.hero {{ padding:72px 0 40px; text-align:center;
         background:radial-gradient(ellipse 60% 70% at 50% 0%, #3a2a1a55, transparent 70%) }}
.hero h1 {{ font-family:var(--head); font-weight:700; font-size:clamp(34px, 6vw, 58px); line-height:1.05; margin:0 0 14px; letter-spacing:.5px }}
.hero h1 em {{ font-style:normal; color:var(--gold) }}
.hero p {{ max-width:620px; margin:0 auto; color:var(--muted); font-size:18px }}
.chips {{ display:flex; flex-wrap:wrap; justify-content:center; gap:8px; margin-top:24px }}
.chips a {{ padding:7px 14px; border:1px solid var(--line); border-radius:99px; text-decoration:none; color:var(--text);
           font-size:14px; background:var(--panel) }}
.chips a:hover {{ border-color:var(--c) }}
.chips a i {{ display:inline-block; width:8px; height:8px; border-radius:50%; background:var(--c); margin-right:8px }}

/* mods */
.mod {{ display:grid; grid-template-columns:1.1fr 1fr; gap:40px; align-items:center; padding:48px 0; border-top:1px solid var(--line) }}
.mod.flip .media {{ order:2 }}
.media {{ position:relative; border-radius:16px; overflow:hidden; border:1px solid var(--line); box-shadow:0 20px 60px #0008 }}
.media img {{ width:100%; aspect-ratio:16/9; object-fit:cover; display:block; background:#000 }}
.media button {{ position:absolute; inset:0; border:0; background:none; cursor:zoom-in }}
/* screenshot as the mod's picture: dimmed with the name over it, full colour on hover */
.shotmedia img {{ transition:filter .35s, transform .5s }}
.shotmedia .over {{ position:absolute; inset:0; display:flex; flex-direction:column; justify-content:flex-end; padding:20px 22px;
                    background:linear-gradient(to top, #0e0c0ae6 0%, #0e0c0a66 45%, transparent 75%); transition:opacity .35s; pointer-events:none }}
.shotmedia .over b {{ font-family:var(--head); font-size:34px; line-height:1; color:var(--accent); text-shadow:0 2px 12px #000 }}
.shotmedia .over span {{ font-size:13px; color:var(--text); opacity:.8; margin-top:6px }}
@media (hover:hover) {{
  .shotmedia img {{ filter:grayscale(.7) brightness(.6) sepia(.25) }}
  .shotmedia:hover img {{ filter:none; transform:scale(1.03) }}
  .shotmedia:hover .over {{ opacity:0 }}
}}
.strip {{ grid-column:1 / -1; order:3; display:grid; grid-template-columns:repeat(auto-fill, minmax(150px, 1fr)); gap:10px; margin-top:4px }}
.strip button {{ padding:0; border:1px solid var(--line); border-radius:10px; overflow:hidden; background:#000; cursor:zoom-in }}
.strip img {{ width:100%; aspect-ratio:16/9; object-fit:cover; display:block; transition:transform .3s, filter .3s }}
@media (hover:hover) {{ .strip img {{ filter:saturate(.6) brightness(.8) }} .strip button:hover img {{ filter:none; transform:scale(1.05) }} }}
.strip button:hover {{ border-color:var(--accent) }}
.info h2 {{ font-family:var(--head); font-size:38px; margin:0; line-height:1.1 }}
.tag {{ color:var(--accent); font-weight:600; margin:6px 0 14px }}
.info ul {{ list-style:none; padding:0; margin:0 0 22px }}
.info li {{ position:relative; padding-left:22px; margin:6px 0; color:#d9cdb8 }}
.info li::before {{ content:""; position:absolute; left:2px; top:.62em; width:8px; height:8px; border-radius:2px;
                    background:var(--accent); transform:rotate(45deg) }}
.actions {{ display:flex; flex-wrap:wrap; gap:10px; align-items:center }}
.btn {{ display:inline-flex; align-items:center; gap:8px; padding:12px 20px; border-radius:10px; font-weight:600; text-decoration:none;
       color:#14110e; background:var(--accent); border:0; font-size:15px; font-family:inherit; cursor:pointer }}
.btn:hover {{ filter:brightness(1.1) }}
.btn svg {{ width:18px; height:18px }}
.ghost {{ background:none; color:var(--text); border:1px solid var(--line) }}
.ghost:hover {{ border-color:var(--accent); filter:none }}
.meta {{ font-size:13px; color:var(--muted); width:100% }}
@media (max-width:860px) {{ .mod {{ grid-template-columns:1fr; gap:22px; padding:36px 0 }} .mod.flip .media {{ order:0 }} }}

/* before / after slider */
.compare {{ padding:0 0 48px }}
.compare h3 {{ font-family:var(--head); font-size:26px; margin:0 0 4px }}
.compare p {{ color:var(--muted); margin:0 0 16px }}
.ba {{ position:relative; border-radius:16px; overflow:hidden; border:1px solid var(--line); box-shadow:0 20px 60px #0008;
       aspect-ratio:16/9; max-width:1080px; margin:0 auto; user-select:none; --pos:50% }}
.ba img {{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; display:block }}
.ba .after {{ clip-path:inset(0 0 0 var(--pos)) }}
.ba .bar {{ position:absolute; top:0; bottom:0; left:var(--pos); width:3px; margin-left:-1.5px; background:var(--gold); pointer-events:none }}
.ba .bar::after {{ content:"\\2194"; position:absolute; top:50%; left:50%; width:40px; height:40px; margin:-20px 0 0 -20px;
                  border-radius:50%; background:var(--gold); color:#14110e; display:grid; place-items:center; font-weight:700; font-size:20px }}
.ba input {{ position:absolute; inset:0; width:100%; height:100%; opacity:0; cursor:ew-resize; margin:0 }}
.ba .lbl {{ position:absolute; top:12px; padding:4px 12px; border-radius:99px; background:#0e0c0af0; border:1px solid var(--line); z-index:1; font-size:13px; font-weight:600; pointer-events:none }}
.ba .lbl.l {{ left:12px }} .ba .lbl.r {{ right:12px; color:var(--gold) }}

/* faq */
.faq {{ padding:56px 0 8px; border-top:1px solid var(--line) }}
.faq > h2 {{ font-family:var(--head); font-size:38px; margin:0 0 18px }}
.faq details {{ background:var(--panel); border:1px solid var(--line); border-radius:12px; margin:0 0 10px; padding:0 20px }}
.faq details[open] {{ border-color:#4a3c2c }}
.faq summary {{ cursor:pointer; padding:16px 0; font-weight:600; list-style:none; display:flex; justify-content:space-between; gap:16px }}
.faq summary::-webkit-details-marker {{ display:none }}
.faq summary::after {{ content:"+"; color:var(--gold); font-size:22px; line-height:1 }}
.faq details[open] summary::after {{ content:"\\2212" }}
.faq details p {{ margin:0 0 16px; color:#d9cdb8 }}

/* dialog */
dialog {{ width:min(1000px, calc(100vw - 32px)); max-height:calc(100vh - 32px); padding:0; border:1px solid var(--line);
          border-radius:16px; background:var(--panel); color:var(--text) }}
dialog::backdrop {{ background:#000c; backdrop-filter:blur(3px) }}
.dlg-head {{ position:sticky; top:0; z-index:1; display:flex; align-items:center; gap:12px; padding:12px 16px;
             background:var(--panel); border-bottom:1px solid var(--line) }}
.dlg-head h2 {{ margin:0; font-family:var(--head); font-size:26px; flex:1 }}
.dlg-head .btn {{ padding:8px 14px }}
.close {{ background:none; border:0; color:var(--muted); font-size:28px; line-height:1; cursor:pointer; padding:0 4px }}
.dlg-body {{ padding:16px }}
.shot {{ margin:0 }}
.shot img {{ width:100%; max-height:62vh; object-fit:contain; border-radius:10px; display:block; background:#000; cursor:zoom-in }}
.shot figcaption {{ color:var(--muted); font-size:14px; margin:6px 0 10px }}
.thumbs {{ display:flex; gap:8px; overflow-x:auto; padding-bottom:6px }}
.thumbs button {{ flex:0 0 auto; padding:0; border:2px solid transparent; border-radius:7px; background:none; cursor:pointer }}
.thumbs button[aria-current="true"] {{ border-color:var(--accent) }}
.thumbs img {{ width:120px; height:72px; object-fit:cover; border-radius:5px; display:block }}
.desc {{ font-size:15px; color:#d8ccb6; margin-top:8px }}
.desc h2 {{ font-size:19px; margin:18px 0 4px; color:var(--text) }}
.desc h3 {{ font-size:16px; margin:14px 0 4px; color:var(--text) }}
.desc ul {{ padding-left:20px; margin:4px 0 }}
.desc hr {{ border:0; border-top:1px solid var(--line) }}
.GreenColor {{ color:#8fd46a }} .RedColor {{ color:#ff7a68 }} .OrangeColor {{ color:#ffad5a }}

/* install */
.install {{ padding:56px 0 24px; border-top:1px solid var(--line) }}
.install > h2 {{ font-family:var(--head); font-size:38px; margin:0 0 6px }}
.install > p {{ color:var(--muted); margin:0 0 24px }}
.steps {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(260px, 1fr)); gap:16px }}
.step {{ background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:20px 22px }}
.step h3 {{ margin:0 0 8px; font-size:18px }}
.step h3 small {{ font-size:12px; font-weight:600; color:#14110e; background:var(--gold); padding:2px 8px; border-radius:99px;
                  margin-left:8px; vertical-align:middle }}
.step ol {{ padding-left:20px; margin:0; color:#d9cdb8; font-size:15px }}
.step li {{ margin:4px 0 }}
code {{ background:#0a0907; border:1px solid var(--line); padding:1px 6px; border-radius:5px; font-size:13px }}
.note {{ margin-top:16px; color:var(--muted); font-size:15px }}
footer {{ border-top:1px solid var(--line); margin-top:40px }}
footer .wrap {{ display:flex; flex-wrap:wrap; gap:12px; align-items:center; justify-content:space-between; padding:22px 20px 36px;
               color:var(--muted); font-size:14px }}
footer img {{ width:28px; height:28px; vertical-align:middle; margin-right:8px }}
</style>
</head>
<body>
<nav><div class="wrap">
  <a class="brand" href="#top" aria-label="Home"><img src="img/logo.png" alt="Logo"></a>
  <ul>
    {navlinks}
    <li><a href="#install">Install</a></li>
    <li class="opt"><a href="#faq">FAQ</a></li>
    <li class="opt"><a href="{repo}/issues">Report a bug</a></li>
  </ul>
</div></nav>

<header class="hero" id="top"><div class="wrap">
  <h1>Deadlock mods for <em>4:3</em>,<br>the HUD and hero select</h1>
  <p>De-stretch and scale the HUD and shop, add a 4x3 aspect ratio, and find heroes faster. Free, and they work together.</p>
  <div class="chips">{chips}</div>
</div></header>

<main class="wrap">
{cards}

<section class="install" id="install">
  <h2>Install</h2>
  <p>Download a mod's <code>.zip</code> above, then add it in your mod manager or by hand.</p>
  <div class="steps">
    <div class="step"><h3>Deadlock Mod Manager <small>easiest</small></h3><ol>
      <li>Open <a href="https://deadlockmods.app/">Deadlock Mod Manager</a> and choose <b>Add Local Mod</b>.</li>
      <li>Drop the zip in (don't unzip it), name it, add it, and turn it on.</li>
    </ol></div>
    <div class="step"><h3>Grimoire</h3><ol>
      <li>In <a href="https://grimoiremods.com/">Grimoire</a>, open <b>Installed</b> and choose <b>Import Local Mods</b>.</li>
      <li>Pick the zip and turn the mod on.</li>
    </ol></div>
    <div class="step"><h3>By hand</h3><ol>
      <li>Unzip it. It contains <code>pak01_dir.vpk</code>.</li>
      <li>Copy that file to <code>Deadlock/game/citadel/addons</code> and rename it to the next free number
          (<code>pak02_dir.vpk</code>, ...). The game stops loading at the first missing number.</li>
      <li>Mods must be enabled in <code>gameinfo.gi</code>. A mod manager does this for you.</li>
    </ol></div>
  </div>
  <p class="note"><b>Updating:</b> remove the old version in your mod manager, then add the new zip from this page.</p>
</section>

<section class="faq" id="faq">
  <h2>FAQ</h2>
{faq}
</section>
</main>

<footer><div class="wrap">
  <span><img src="img/logo.png" alt="">Made by dirtytomat0, with AI. Not affiliated with Valve.</span>
  <span>Questions or bugs: <a href="{repo}/issues">open an issue on GitHub</a></span>
</div></footer>
<script>
document.querySelectorAll(".ba").forEach(function (b) {{
  var r = b.querySelector("input");
  r.addEventListener("input", function () {{ b.style.setProperty("--pos", r.value + "%"); }});
}});
document.querySelectorAll("[data-open]").forEach(function (b) {{
  b.addEventListener("click", function () {{
    var d = document.getElementById(b.dataset.open);
    d.showModal();
    var t = d.querySelectorAll(".thumbs button")[b.dataset.shot || 0];
    if (t) t.click();
  }});
}});
document.querySelectorAll("dialog").forEach(function (d) {{
  d.addEventListener("click", function (e) {{ if (e.target === d) d.close(); }});   // click outside closes
  d.querySelector(".close").addEventListener("click", function () {{ d.close(); }});
  d.querySelectorAll(".thumbs button").forEach(function (t) {{
    t.addEventListener("click", function () {{
      var fig = d.querySelector(".shot");
      fig.querySelector("img").src = t.dataset.full;
      fig.querySelector("a").href = t.dataset.big;
      fig.querySelector("figcaption").textContent = t.dataset.caption;
      d.querySelectorAll(".thumbs button").forEach(function (o) {{ o.setAttribute("aria-current", o === t); }});
    }});
  }});
}});
</script>
</body>
</html>
"""

DOWNLOAD_ICON = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" '
                 'stroke-linejoin="round" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5M5 20h14"/></svg>')

CARD = """<section class="mod{flip}" id="{key}" style="--accent:{accent}">
  <div class="media{media_cls}"><img src="{media}" alt="{name}" loading="lazy">{media_over}<button data-open="dlg-{key}" aria-label="{name} details"></button></div>
  <div class="info">
    <h2>{name}</h2>
    <div class="tag">{tagline}</div>
    <ul>{points}</ul>
    <div class="actions">
      <a class="btn" href="downloads/{zip}" download>""" + DOWNLOAD_ICON + """Download v{version}</a>
      <button class="btn ghost" data-open="dlg-{key}">{more}</button>
      <div class="meta">{size} KB zip</div>
    </div>
  </div>
  {strip}
</section>
<dialog id="dlg-{key}" style="--accent:{accent}" aria-label="{name}">
  <div class="dlg-head"><h2>{name}</h2><a class="btn" href="downloads/{zip}" download>Download {version}</a>
    <button class="close" aria-label="Close">&times;</button></div>
  <div class="dlg-body">{gallery}<div class="desc">{details}</div></div>
</dialog>
{extra}"""

COMPARE = """<section class="compare" style="--accent:{accent}">
  <h3>Before and after</h3>
  <p>4:3 stretched on a 16:9 monitor, the same spot: the stock HUD, then de-stretched and resized with HUD Fit. Drag to compare.</p>
  <div class="ba">
    <img src="{before}" alt="Deadlock HUD stretched at 4:3, without HUD Fit">
    <img class="after" src="{after}" alt="Deadlock HUD de-stretched and resized with HUD Fit">
    <span class="lbl l">Before</span><span class="lbl r">With HUD Fit</span>
    <div class="bar"></div>
    <input type="range" min="0" max="100" value="50" aria-label="Before / after">
  </div>
</section>"""

# question, answer (plain text; also used for the search-engine FAQ data)
FAQ = [
    ("How do I de-stretch the HUD when playing Deadlock 4:3 stretched?",
     "Install HUD Fit, press Esc and choose HUD Fit, open the HUD tab and pick the 4:3 stretch preset. Then turn on "
     "De-stretch everything, or de-stretch only the elements you choose."),
    ("How do I make the Deadlock UI or shop smaller or bigger?",
     "In HUD Fit, use Scale all items in the HUD tab for the whole HUD. To resize one element, select it (for example "
     "Buy menu (shop) under Layers) and change Size %, or drag its corner handle."),
    ("How do I get a 4:3 resolution in Deadlock?",
     "Install 4:3 Video, then pick 4x3 under Settings, Video, Aspect Ratio. If the resolution you want is not listed, "
     "add it as a custom resolution in your graphics driver (AMD Adrenalin, NVIDIA Control Panel or CRU) first."),
    ("Do these mods work together?",
     "Yes. They change different game files. HUD Fit conflicts with other mods that replace base_hud or "
     "hud_escape_menu, and Hero Select Plus conflicts with other hero select mods."),
    ("A game update broke something. What now?",
     "Turn the mod off in your mod manager until an updated version is posted on this page."),
]


def faq_html():
    return "\n".join("  <details><summary>%s</summary><p>%s</p></details>" % (html.escape(q), html.escape(a))
                      for q, a in FAQ)


def faq_ld():
    import json
    data = {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                           for q, a in FAQ]}
    return json.dumps(data).replace("</", "<\\/")


def shot_base(m, src):
    """Output name of a screenshot: mod key + source file name, so reordering never mixes files up."""
    stem = re.sub(r"[^a-z0-9]+", "_", os.path.splitext(os.path.basename(src))[0].lower()).strip("_")
    stem = re.sub(r"^%s_" % re.escape(m["key"]), "", stem)
    return "%s_%s" % (m["key"], stem)


def shot_items(m):
    """(web, big, thumb, caption) per screenshot; makes the resized copies once."""
    d = os.path.join(DOCS, "img", "shots")
    os.makedirs(d, exist_ok=True)
    items = []
    for src, caption in m.get("shots") or []:
        base = shot_base(m, src)
        path = os.path.join(STEAM_SHOTS, src)
        stretch = None
        for suffix, width in (("", 1280), ("_big", 2560), ("_t", 240)):
            out = os.path.join(d, base + suffix + ".jpg")
            if not os.path.exists(out):
                if stretch is None:
                    stretch = bool(m.get("stretch43")) and is_43(path)
                jpg(path, out, min(width, 1920) if stretch else width, stretch)
        items.append(("img/shots/%s.jpg" % base, "img/shots/%s_big.jpg" % base, "img/shots/%s_t.jpg" % base, caption))
    return items


def strip_html(m):
    """Screenshot row under a mod; each opens the pop-up at that screenshot."""
    items = shot_items(m)
    if not items:
        return ""
    return '<div class="strip">%s</div>' % "".join(
        '<button data-open="dlg-%s" data-shot="%d" title="%s"><img src="%s" alt="%s" loading="lazy"></button>'
        % (m["key"], i, html.escape(c), t, html.escape(c)) for i, (f, b, t, c) in enumerate(items))


def gallery_html(m):
    """Screenshots in the pop-up: first one shown large, thumbnails to switch."""
    items = shot_items(m)
    if not items:
        return ""
    full, big, _, cap = items[0]
    thumbs = "".join(
        '<button data-full="%s" data-big="%s" data-caption="%s" aria-current="%s"><img src="%s" alt="" loading="lazy"></button>'
        % (f, b, html.escape(c), "true" if i == 0 else "false", t) for i, (f, b, t, c) in enumerate(items))
    return ('<figure class="shot"><a href="%s" target="_blank"><img src="%s" alt=""></a><figcaption>%s</figcaption></figure>'
            '<div class="thumbs">%s</div>' % (big, full, html.escape(cap), thumbs))


SITE = "https://greeb.github.io/mods/"


def badge_text(t):
    return t.replace("-", "--").replace("_", "__").replace(" ", "%20").replace(":", "%3A")


def update_readme(versions):
    """Fills the <!--dl:key--> markers in README.md with a download button for the current version."""
    path = os.path.join(HERE, "README.md")
    text = open(path, encoding="utf-8").read()
    for m in MODS:
        version, zipname = versions[m["key"]]
        label = "Download %s v%s" % (m["name"], version)
        badge = ("[![%s](https://img.shields.io/badge/%s-%s-%s?style=for-the-badge)](%sdownloads/%s)"
                 % (label, badge_text("Download"), badge_text("%s v%s" % (m["name"], version)),
                    m["accent"].lstrip("#"), SITE, zipname))
        text = re.sub(r"<!--dl:%s-->.*?<!--/dl-->" % m["key"], lambda _: "<!--dl:%s-->%s<!--/dl-->" % (m["key"], badge),
                      text, flags=re.S)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    os.makedirs(os.path.join(DOCS, "img"), exist_ok=True)
    os.makedirs(os.path.join(DOCS, "downloads"), exist_ok=True)
    shutil.copyfile(os.path.join(BRANDING, "out/avatar_transparent_256.png"), os.path.join(DOCS, "img/logo.png"))
    old_avatar = os.path.join(DOCS, "img/avatar.png")
    if os.path.exists(old_avatar):
        os.remove(old_avatar)
    cards, keep, versions = [], set(), {}
    for n, m in enumerate(MODS):
        version, zipname = latest_zip(m)
        versions[m["key"]] = (version, zipname)
        shutil.copyfile(os.path.join(m["dist"], zipname), os.path.join(DOCS, "downloads", zipname))
        keep.add(zipname)
        jpg(os.path.join(BRANDING, "out", m["key"] + ".png"), os.path.join(DOCS, "img", m["key"] + ".jpg"), 960)
        size = os.path.getsize(os.path.join(DOCS, "downloads", zipname)) // 1024 + 1
        points = "".join("<li>%s</li>" % html.escape(p) for p in m["points"])
        cards.append(CARD.format(flip=" flip" if n % 2 else "", accent=m["accent"], key=m["key"], name=html.escape(m["name"]),
                                 tagline=html.escape(m["tagline"]), version=version, size=size, points=points,
                                 zip=zipname, details=details_html(m["folder"]), gallery=gallery_html(m),
                                 more="Details &amp; screenshots" if m.get("shots") else "Details",
                                 media=shot_items(m)[0][0] if m.get("shots") else "img/%s.jpg" % m["key"],
                                 media_cls=" shotmedia" if m.get("shots") else "",
                                 media_over=('<div class="over"><b>%s</b><span>%d screenshots</span></div>'
                                             % (html.escape(m["name"]), len(m["shots"]))) if m.get("shots") else "",
                                 strip=strip_html(m),
                                 extra=COMPARE.format(accent=m["accent"],
                                                      before="img/shots/%s.jpg" % shot_base(m, m["compare"][0]),
                                                      after="img/shots/%s.jpg" % shot_base(m, m["compare"][1]))
                                 if m.get("compare") else ""))
        print("%-17s v%s  %s" % (m["name"], version, zipname))
    # old versions are dropped from the site (the git history keeps them)
    for f in os.listdir(os.path.join(DOCS, "downloads")):
        if f not in keep:
            os.remove(os.path.join(DOCS, "downloads", f))
    with open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8") as f:
        navlinks = "\n    ".join('<li class="opt"><a href="#%s">%s</a></li>' % (m["key"], html.escape(m["name"])) for m in MODS)
        chips = "".join('<a href="#%s" style="--c:%s"><i></i>%s</a>' % (m["key"], m["accent"], html.escape(m["name"])) for m in MODS)
        f.write(PAGE.format(cards="\n".join(cards), repo=REPO, navlinks=navlinks, chips=chips,
                            faq=faq_html(), faq_ld=faq_ld()))
    open(os.path.join(DOCS, ".nojekyll"), "w").close()
    update_readme(versions)
    used = {os.path.basename(p) for m in MODS for it in shot_items(m) for p in it[:3]}
    sd = os.path.join(DOCS, "img", "shots")
    for f in os.listdir(sd):
        if f not in used:
            os.remove(os.path.join(sd, f))
    print("wrote", os.path.join(DOCS, "index.html"))


if __name__ == "__main__":
    main()
