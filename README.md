# Deadlock mods: HUD Fit, 4:3 Video, Hero Select Plus

**Download page: https://greeb.github.io/mods/**

Free Deadlock mods by dirtytomat0:

- **HUD Fit** de-stretches, scales and moves the HUD, including the shop.
- **4:3 Video** adds a 4x3 aspect ratio option to the video settings.
- **Hero Select Plus** adds names, classes, search and filters to the hero select screen.

They work on their own or together.

AI was used to make these mods. For bugs and questions, open an issue in this repo.

## HUD Fit: de-stretch, resize and move the Deadlock HUD

HUD Fit is an in-game HUD editor for Deadlock. It is made for **4:3 stretched** players, but it
works at any resolution (16:9, 16:10, 5:4, 21:9). Playing stretched makes the HUD look wide and
blurry, and HUD Fit makes it look right again. You can also make the UI bigger or smaller, or
move pieces of it out of the way.

Open it in game with **Esc → HUD Fit** (under Settings). Explore NYC or a sandbox / Hero Testing
match is the best place to use it.

### Features

- **De-stretch the HUD for 4:3 stretched:** fix chosen elements or the whole HUD, with presets
  for 4:3, 5:4 and 16:10.
- **Scale the UI:** make the whole HUD bigger or smaller (UI scale / HUD size) and every element
  stays at its screen edge. Each element can also be resized on its own.
- **Scale and de-stretch the shop (buy menu)**, so it fits a 4:3 screen or a smaller UI.
- **Move any of 23 HUD elements:** health bar, abilities, items & souls, weapon / spirit /
  vitality, minimap, top bar, crosshair & ammo, kill feed, chat, buy menu, interact prompts,
  buffs & debuffs, aura effects, hints, announcements, effect messages, respawn timer, damage
  meter, movement speed, ability resource, testing tools and stat details.
- **Live editor on the real HUD:** click an element and drag it. Drag the corner handle to
  resize it.
- **Snapping** to screen edges, the centre and other elements. W A S D nudges an element
  (hold Shift for 10 px) and + / − changes its size.
- **Center buttons** put the crosshair or any other element exactly in the middle of the screen.
- **Layers panel:** show or hide each element, lock it, or reset it with one click.
- **Fixes the health bar disappearing at 4:3.** The stock layout only fits 16:9 and wider.
- **Test tab:** one-click sandbox situations so you can arrange the real UI: damage, low
  health, death / respawn timer, level up, souls, buffs, enemy bot, trooper wave and DPS meter.
- **Layouts:** Default, Clean, and up to 20 named layouts. Export or import a layout code to
  share it.
- **Filters** with a strength slider: Monochrome, Sepia, Neon, Ice, Ghost, Focus and Muted.
- **Saved on your PC:** your layout comes back after a restart, and nothing is uploaded.

## 4:3 Video: 4x3 aspect ratio option for Deadlock

This mod adds a **4x3** choice to **Settings → Video → Aspect Ratio**, next to 16:9, 16:10 and
21:9. Pick it and the resolution list shows the 4:3 resolutions your graphics driver offers,
for example 1600x1200, 1440x1080 or 1280x960.

- It never replaces the settings screen. Older 4:3 mods ship a whole copy of that screen, which
  hides every newer setting.
- It remembers your choice: 4x3 stays selected when you reopen the settings.
- You want 1920x1440 or another resolution that isn't listed? Add it as a custom resolution
  first, in AMD Adrenalin, the NVIDIA Control Panel or CRU.
- It is made to be used with HUD Fit, which de-stretches the HUD when you play 4:3 stretched.

## Hero Select Plus: learn the Deadlock heroes faster

Hero Select Plus makes the hero select screen easier to read, especially for new players.

- Hero names are always visible on every card.
- Every card shows the hero's class, colour coded: Marksman, Assassin, Mystic or Brawler.
- A **search box** finds heroes by name, class, tag, weapon type or difficulty. Several words
  narrow it down, for example "brawler tank".
- Class filter buttons, plus a **Beginner** button for the heroes the game recommends to new
  players.
- Hovering a hero shows its class, difficulty, weapon type, a one-line role and a playstyle
  summary.

## Install

1. Download the zip from https://greeb.github.io/mods/
2. In **Deadlock Mod Manager**, choose **Add Local Mod** and drop in the zip.
   - Manual install: copy `pak01_dir.vpk` from the zip into `Deadlock/game/citadel/addons` and
     rename it to the next free number (`pak02_dir.vpk`, `pak03_dir.vpk`, ...).
3. After a big game update, if something looks wrong, disable the mod until an updated version
   is posted on the page.

## Building the page

The page is generated. `python3 build_site.py` copies the latest release zips, thumbnails and
screenshots (listed per mod in `build_site.py`) into `docs/`, which GitHub Pages serves.
