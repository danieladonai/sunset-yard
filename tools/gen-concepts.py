#!/usr/bin/env python3
"""Generate Sunset Yard concept art + textures via the capped Gemini wrapper."""
import os, sys, shutil, pathlib

sys.path.insert(0, "/root/.openclaw/workspace/google")
from gemini_image import generate

OUT = pathlib.Path("/root/Code/sunset-yard/tools/concepts")
OUT.mkdir(parents=True, exist_ok=True)

STYLE = ("Concept art for an original 3D browser skateboarding video game called "
         "'Sunset Yard'. Dusk/sunset skatepark mood: warm concrete tones, purple-orange "
         "gradient sky, retro arcade vibe. 100% original design — no real brand logos, "
         "no real skater likenesses, no copyrighted characters, no text or watermarks.")

CHAR = ("Full-body original skater character standing on a skateboard, 3/4 view, "
        "whole body and board fully in frame, clean plain light background. ")

JOBS = [
    ("concept-street.png", STYLE + CHAR +
     "Grounded 90s/2000s street skater style: backwards baseball cap, plain graphic tee, "
     "baggy jeans, chunky skate shoes. Realistic-leaning stylized illustration."),
    ("concept-synthwave.png", STYLE + CHAR +
     "Neon synthwave/vaporwave skater: glowing neon accents in purple, magenta and orange "
     "matching a sunset palette, retro-futuristic jacket, gridline glow highlights, "
     "stylized 80s retrowave illustration."),
    ("concept-lowpoly.png", STYLE + CHAR +
     "Chunky stylized low-poly mascot skater rendered as faceted low-polygon 3D art, bold "
     "flat colors, big friendly proportions, minimal facial detail, looks like an in-game "
     "low-poly 3D character model render."),
    ("concept-modern.png", STYLE + CHAR +
     "Sleek modern minimalist skater: clean fitted streetwear in muted tones with one warm "
     "sunset-orange accent, simple flat-shaded contemporary vector-style illustration."),
    ("texture-deck.png", STYLE +
     "Flat top-down skateboard DECK GRAPHIC texture map, square image, the elongated deck "
     "shape centered on a plain background: bold original abstract sunset design — purple "
     "to orange gradient, sun circle, palm/skyline silhouettes, retro arcade geometry. "
     "Flat 2D game-ready art, no perspective, no shadows."),
    ("texture-outfit.png", STYLE +
     "Simple character OUTFIT texture sheet for wrapping a low-poly humanoid game model, "
     "square flat 2D layout: unwrapped UV-style panels for a hoodie/tee (front and back), "
     "sleeves, and jeans legs, flat bold colors in a sunset palette, clearly separated "
     "pieces on a neutral background, no perspective, no shading."),
]

def run(batch):
    names = [n for n, _ in batch]
    paths = generate([p for _, p in batch], out_dir=str(OUT))
    for src, name in zip(paths, names):
        shutil.move(src, OUT / name)
        print("saved", OUT / name)

run(JOBS[:4])
run(JOBS[4:])
