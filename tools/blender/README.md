# Blender skate clips (v4 prototype)

Hand-keyed skate animation on the Quaternius Universal Animation Library mannequin (CC0,
https://quaternius.com/packs/universalanimationlibrary.html - free "Standard" pack, mirrored on OpenGameArt).

- `author.py` - builds the clips with IK/constraint controls, then bakes to plain keyframes.
  `Blender -b --python author.py -- <AnimationLibrary_Godot_Standard.glb> <out_dir>`
  Writes `skater_clips.glb` (actions: Ride_Idle, Push_Loop), `skater_clips.blend`, `contacts.json`.
- `render.py` / `render_stills.py` - preview video / stills with a scrolling ground.
- `compose.py` - side-by-side video (old in-game capture vs new).
- `../v3/capture_push.js` - captures the current in-game push as a PNG sequence.

Board frame: board centred at origin, nose +X, deck top z=0.108 (matches the game). Regular stance.
Push_Loop: 32 frames @30fps; the planted foot moves back 0.04 m/frame (1.2 m/s) - scale playback by board speed.
