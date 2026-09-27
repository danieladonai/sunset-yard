# Sunset Yard v3 - the Opus 5.5 gauntlet

Branch `v3-opus-5.5-gauntlet`. Every pass is one commit on the same file (`sunset-yard-3d.html`), so the
diff per pass is readable: `git log --oneline main..v3-opus-5.5-gauntlet`.

**Baseline** = the live `/sunset-yard/play/` build (Aug 2), which was newer than GitHub `main`. Commit 1 on the
branch syncs the repo to it, so every later diff is pure v3 work.

## The three versions
| | What it is | File |
|---|---|---|
| v1 (live) | Multi-agent glow-up build, Aug 2026 | `sunset-yard-3d.html` on `main` |
| v2 (Sep 25) | Opus 4.6 Cowork gauntlet. It could not find v1, so it **rebuilt from screenshots** - a different, smaller game (79KB, three r128). Not diffable against v1. | `versions/sunset-yard-v2-opus-4.6-rebuild.html` |
| v3 (Sep 27) | Opus 5.5 gauntlet **on the real v1 code** | `sunset-yard-3d.html` on this branch |

## Passes
1. **Transition physics** - quarters, spine & 4.2m vert wall were solid walls; now rideable (slope gravity,
   coping launch, drop-ins, bonks). Air keeps its own momentum. Fair, explained bails. Charged ollie.
   Fixed a live-build exploit: rail end-cap re-grab looped every frame and banked free points.
2. **Tricks you choose** - flips by direction + stacking, held grabs, grind picked by lock-on angle,
   visible balance meter, repeat-trick decay, manual opens a combo, reverts.
3. **Skater realism** - root causes, not restyling: emissive/metal material (rider ignored the sun),
   legs IK-locked straight, pelvis height never reached the model, backwards air tuck, skin-coloured outfits.
4. **Progression** - saved bests, 13-goal ladder, run stats, named gaps, solid stairs/ledges.
5. **Sound + review fixes** - noise-synth audio bed; 8 bugs from an adversarial review agent (incl. a
   manual-tap exploit worth millions/run), each reproduced headless before fixing.
6. **Board, menu, landing reads, mobile** - real-scale board, fixed a graphic plane stuck through the deck
   (also live), in-engine roster cards, PERFECT/SKETCHY landings.

## Verify it yourself
```
python3 -m http.server 8765          # from the repo root; needs sunset-yard-vendor/ (see README)
cd tools/v3 && npm i && node harness.js phys     # every ramp, spins, bails, gaps
node harness.js smoke                              # 20s scripted run: fps + page errors
```

## Honest limits
- The character mesh is still the Meshy-generated low-poly model; the hip area crumples under a wide
  stance (skinning limit of the asset). A better base mesh is the next real step for realism.
- Audio was verified to run, not listened to.
- Tuned by harness + screenshots, not by a human playing on a phone - give it a real run on iPhone.
