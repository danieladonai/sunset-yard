# Preview render: Blender -b out/skater_clips.blend --python render.py -- <action> <view> <loops> <out.mp4>
import bpy, sys, math
from mathutils import Vector
ACT, VIEW, LOOPS, OUT = sys.argv[-4], sys.argv[-3], int(sys.argv[-2]), sys.argv[-1]
sc = bpy.context.scene; arm = bpy.data.objects["Rig"]
ad = arm.animation_data
for t in list(ad.nla_tracks): ad.nla_tracks.remove(t)
act = bpy.data.actions[ACT]; ad.action = act
if hasattr(ad, "action_slot") and act.slots: ad.action_slot = act.slots[0]
L = int(act.frame_range[1] - act.frame_range[0])
sc.frame_start, sc.frame_end = 0, L*LOOPS - 1
for fc in (act.fcurves if hasattr(act, "fcurves") else [c for ly in act.layers for st in ly.strips for bag in st.channelbags for c in bag.fcurves]):
    fc.modifiers.new('CYCLES')

DECK = 0.108
def mat(name, rgb, rough=0.6):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    return m
# board: deck + kicks + trucks + wheels, nose = +X
def box(name, size, loc, m, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot); o = bpy.context.object; o.name = name
    o.scale = size; o.data.materials.append(m); bpy.ops.object.transform_apply(scale=True); return o
deckM = mat("deck", (0.03,0.025,0.06), 0.4); truckM = mat("truck", (0.6,0.62,0.66), 0.35); wheelM = mat("wheel", (0.9,0.85,0.75), 0.5)
box("deck", (0.74,0.21,0.012), (0,0,DECK-0.006), deckM)
for s in (-1,1):
    box("kick%d"%s, (0.13,0.20,0.012), (s*0.43,0,DECK+0.012), deckM, (0, -s*0.33, 0))
    box("truck%d"%s, (0.06,0.17,0.035), (s*0.31,0,0.065), truckM)
    for w in (-1,1):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.027, depth=0.032, location=(s*0.31, w*0.095, 0.027), rotation=(math.pi/2,0,0))
        bpy.context.object.data.materials.append(wheelM)
# ground: concrete checker that SCROLLS backwards at the push ground speed (0.04 m/frame)
bpy.ops.mesh.primitive_plane_add(size=40, location=(0,0,0)); g = bpy.context.object
gm = bpy.data.materials.new("ground"); gm.use_nodes = True; nt = gm.node_tree
tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping"); ck = nt.nodes.new("ShaderNodeTexChecker")
ck.inputs["Scale"].default_value = 40; ck.inputs["Color1"].default_value = (0.55,0.52,0.48,1); ck.inputs["Color2"].default_value = (0.45,0.42,0.39,1)
nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], ck.inputs["Vector"])
nt.links.new(ck.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"])
g.data.materials.append(gm)
speed = 0.04 if ACT == "Push_Loop" else 0.0
loc = mp.inputs["Location"]
loc.default_value = (0,0,0); loc.keyframe_insert("default_value", frame=0)
loc.default_value = (speed*sc.frame_end,0,0); loc.keyframe_insert("default_value", frame=sc.frame_end)
for fc in gm.node_tree.animation_data.action.fcurves if hasattr(gm.node_tree.animation_data.action,"fcurves") else []:
    for k in fc.keyframe_points: k.interpolation = 'LINEAR'
try:
    act2 = gm.node_tree.animation_data.action
    for ly in act2.layers:
        for st in ly.strips:
            for bag in st.channelbags:
                for fc in bag.fcurves:
                    for k in fc.keyframe_points: k.interpolation = 'LINEAR'
except Exception: pass
# figure material
me = bpy.data.objects["Mannequin"]
fm = mat("fig", (0.85,0.45,0.25), 0.55); me.data.materials.clear(); me.data.materials.append(fm)
# light + world
bpy.ops.object.light_add(type='SUN', rotation=(math.radians(50), math.radians(10), math.radians(-35))); bpy.context.object.data.energy = 3.5
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.55,0.6,0.7,1); sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.8
# camera
cams = {"side": ((0.05,-3.6,0.85), (0,0,0.62)), "front": ((3.4,-1.2,1.0), (0,0,0.6)), "back": ((-3.0,-1.8,1.3), (0,0,0.6))}
p, tgt = cams[VIEW]
bpy.ops.object.camera_add(location=p); cam = bpy.context.object; sc.camera = cam
d = Vector(tgt) - Vector(p); cam.rotation_euler = d.to_track_quat('-Z','Y').to_euler(); cam.data.lens = 45
sc.render.engine = 'BLENDER_EEVEE' if 'BLENDER_EEVEE' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE_NEXT'
sc.render.resolution_x = 640; sc.render.resolution_y = 640; sc.render.fps = 30
sc.render.image_settings.media_type = 'VIDEO'; sc.render.image_settings.file_format = 'FFMPEG'
sc.render.ffmpeg.format = 'MPEG4'; sc.render.ffmpeg.codec = 'H264'; sc.render.ffmpeg.constant_rate_factor = 'HIGH'
sc.render.filepath = OUT
bpy.ops.render.render(animation=True)
print("RENDERED", OUT)
