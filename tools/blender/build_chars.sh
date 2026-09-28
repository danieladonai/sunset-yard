#!/bin/bash
# Rebuild both characters: dress -> author clips -> glb
set -e
cd "$(dirname "$0")"
U="$PWD/ubc/Universal Base Characters[Standard]"; B=/Applications/Blender.app/Contents/MacOS/Blender
H="$U/Hairstyles/Rigged to Head Bone/glTF (Godot -Unreal)"; T="$U/Base Characters/Textures"; G="$U/Base Characters/Godot - UE"
$B -b --python dress.py -- "$G/Superhero_Male_FullBody.gltf" "$H/Hair_SimpleParted.gltf" "$T/T_Superhero_Male_Dark.png" "$PWD/out/rio.blend" rio 2>&1 | grep -E "DRESSED|Traceback|Error:" || true
$B -b --python dress.py -- "$G/Superhero_Female_FullBody.gltf" "$H/Hair_Buns.gltf" "$T/T_Superhero_Female_Light_BaseColor.png" "$PWD/out/nova.blend" nova 2>&1 | grep -E "DRESSED|Traceback|Error:" || true
for c in rio nova; do $B -b out/$c.blend --python author2.py -- "$PWD/out/$c.glb" 2>&1 | grep -E "EXPORTED|Traceback|Error:" || true; done
