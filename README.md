# Sunset Yard

An original 3D browser skateboarding game — and a record of building it end-to-end
with a fleet of AI models orchestrating each other (design, code, generate art,
critique their own rendered output, and verify on a real device), with a human only
steering.

**▶ Play:** `sunset-yard-3d.html` &nbsp;·&nbsp; **📖 The build story:** `sunset-yard-buildlog.html`

Everything here is original — no cloned game IP, no third-party art.

## What's in here
| File | What it is |
|------|-----------|
| `sunset-yard-3d.html` | The game — Three.js 3D low-poly skatepark, character select, combos, mobile + desktop. |
| `sunset-yard.html` | The earlier 2D canvas version (fully standalone). |
| `sunset-yard-buildlog.html` | The case study: the journey, the models, the numbers, the honest limits. |
| `sunset-yard-concepts.html` / `sunset-yard-before-after.html` | Art concepts and character-style comparisons. |
| `sunset-yard-assets/` | Generated art (character concepts, roster, textures) + screenshots. |
| `tools/` | The headless screenshot harness and image-generation driver used during the build. |
| `PROMPT.md` | The generation prompt + notes on the multi-agent technique. |

## Controls
Same on keyboard and on-screen mobile buttons:
- **Steer / spin** — ← / → &nbsp;·&nbsp; **Ollie** — Space &nbsp;·&nbsp; **Flip** — J &nbsp;·&nbsp; **Grab** — K &nbsp;·&nbsp; **Manual** — S
- Roll into a kicker to launch, land on a rail to grind, hold manual to link the combo. Collect the S-K-A-T-E letters.

## Running it
The 2D file is standalone — just open it. The 3D file loads Three.js r160 from a local
`sunset-yard-vendor/` folder (kept out of git). Regenerate it once:

```
npm install three@0.160.0
mkdir -p sunset-yard-vendor/addons
cp node_modules/three/build/three.module.js sunset-yard-vendor/three.module.js
cp -r node_modules/three/examples/jsm/* sunset-yard-vendor/addons/
```

Then serve the folder over HTTP (ES modules need http/https, not `file://`).

## How it was built (short version)
- **2D → 3D → a multi-agent visual "glow-up"** (47 agents, ~2.7M tokens, agents rendering the
  game headless and a harsh critic panel scoring the screenshots on repeat) → **AI-generated
  characters** → **real-browser QA** → collision → character restyle.
- **Models, matched to the job:** frontier judgment on one tier, well-specified builds on a
  cheaper tier, browser QA + repo plumbing on a third, and all the art on an image model.
- Full story, numbers, and honest limits in `sunset-yard-buildlog.html`.

## Tuning
Feel constants live in the `T = { … }` object near the top of each game file (pop height,
gravity, speed, spin/flip rate, landing tolerance, balance decay, score curve).
