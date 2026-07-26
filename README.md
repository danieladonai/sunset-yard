# Sunset Yard

An original, browser-playable arcade skateboarding game — chain one long trick
combo (ollie → spin/flip → grind → manual) before the 2-minute run ends. Built
with Claude Code. Fully original: no real brands, skaters, licensed music, or
copied level layouts.

Two versions live in this repo:

| File | What it is |
|------|-----------|
| `sunset-yard.html` | 2D side-view combo skater (pure Canvas, zero dependencies). |
| `sunset-yard-3d.html` | 3D low-poly skatepark (Three.js from CDN), third-person. |

Both are single self-contained files — open in a browser or host as static files.
The 3D version loads Three.js from a CDN, so it needs network access.

## Controls
Same mapping on desktop keys and on-screen mobile buttons:

- **Steer / spin** — ← / → (arrows steer on the ground, spin in the air)
- **Ollie** — Space
- **Flip** — J  ·  **Grab** — K
- **Manual** — S (hold on landing to link the combo across flat ground)

Roll into a kicker to launch, land on a rail to grind, and **finish your flips
before you land or you bail.** The multiplier climbs while the combo is alive and
banks a beat after you settle; a bail loses it. Collect the five S-K-A-T-E letters.

## Tuning
Feel constants live in the `T = { ... }` object near the top of each file
(pop height, gravity, roll speed, spin/flip rate, landing tolerance, balance
decay, score curve). Tweak those first.

## Running / hosting
`sunset-yard.html` (2D) is fully standalone — just open it.

`sunset-yard-3d.html` loads Three.js r160 from a local `sunset-yard-vendor/`
folder (same-origin = fast, reliable, offline). That folder is gitignored;
regenerate it once with:

```
npm install three@0.160.0
mkdir -p sunset-yard-vendor/addons
cp node_modules/three/build/three.module.js sunset-yard-vendor/three.module.js
cp -r node_modules/three/examples/jsm/* sunset-yard-vendor/addons/
```

Then serve the folder over HTTP (ES modules need http/https, not `file://`).

## Status
Early arcade builds. The 3D build went through a multi-agent screenshot-critic
"glow-up" pass (see `PROMPT.md`) — much richer than the first cut, but still
arcade, not AAA. `tools/shot.js` is the headless screenshot harness used by that
loop.

🤖 Built with [Claude Code](https://claude.com/claude-code)
