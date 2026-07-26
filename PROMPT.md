# Generation prompt & notes

## The prompt (for a Claude 5-gen model, ask for a single self-contained file)

> Build an original arcade skateboarding game in one self-contained file that runs
> in a modern browser on desktop AND mobile. Capture the feel of early-2000s combo
> skaters: a ~2-minute run where you chain tricks into one long, escalating combo.
> Invent everything — no real skater names/likenesses, no real brands, no licensed
> music, no copied real-world level layouts. Call it "Sunset Yard".
>
> The player must be able to EXPRESS (you design the controls, physics, and trick
> set; make it feel good, don't ask me to spec bindings): charge/release pop for
> air; rotate/flip/grab airborne; grind rails and ride manuals on flat; and LINK all
> of it into one combo with a rising multiplier that holds until they land or bail.
>
> The spec is this rubric — build toward it and self-check before finishing:
> 1. Ollies feel poppy, air controllable. 2. A good run chains grind → land → manual
> → ollie → spin into one escalating combo; if tricks don't LINK it fails. 3. Bails
> feel fair (bad angle / unfinished flip). 4. A new player understands it in ~15s,
> no tutorial. 5. It's replayable. 6. Full combo loop works by touch on a phone.
> 7. Smooth (~60fps) on a mid-range phone.
>
> Expose the feel as named tuning constants at the top of the file. Make the
> ambiguous feel calls yourself toward the rubric and note them in a DESIGN NOTES
> block. Deliver the playable file plus a 3-line "how to feel it".

## Pushing the visual quality (the "make it look AAA" route)

The single prompt above yields a solid arcade build, not a AAA look. The known
technique for the latter (per Matt Shumer's "Claude-of-Duty", Three.js, all
procedural) is orchestration, not one prompt:

- Fan out builder sub-agents by subsystem (rendering/materials, park geometry,
  skater + animation, physics/controls, combo/scoring, audio, mobile UX), each
  owning a directory via an ARCHITECTURE.md contract.
- Add a **screenshot + image-diff harness** (headless browser renders the scene,
  captures frames) so a **harsh visual-critic agent** can actually SEE the output
  and score it — without that, agents code blind and the look barely improves.
- `/loop` each subsystem until the critic is satisfied. Note from that project:
  sequential single-owner passes beat parallel fan-out for tightly-coupled systems.

This is expensive (many agent-hours / millions of tokens) and still may not reach
AAA — the reference scored ~5/10 against real Call of Duty.
