# Dress a Quaternius Universal Base Character for Sunset Yard.
# Blender -b --python dress.py -- <body.gltf> <hair.gltf> <skinTexture.png|-> <out.blend> <style>
# Clothing is built as SHELLS of the body's own surface (duplicated faces pushed out
# along the normal, given a hem with Solidify), so every garment carries the body's
# skin weights and bends exactly with it. Materials are named Shirt / Pants / Shoe /
# Sole so the game can recolour them per character.
import bpy, sys, bmesh, math
from mathutils import Vector

BODY, HAIR, SKIN, OUT, STYLE = sys.argv[-5:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=BODY)
for o in list(bpy.data.objects):
    if o.name.startswith("Icosphere"): bpy.data.objects.remove(o)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
body = [o for o in bpy.data.objects if o.type == 'MESH' and o.name.lower().startswith("superhero")][0]
body.name = "Body"

# optional alternate skin texture (light/dark)
if SKIN != "-":
    img = bpy.data.images.load(SKIN)
    for n in body.data.materials[0].node_tree.nodes:
        if n.type == 'TEX_IMAGE' and ('Dark' in n.image.name or 'Ligh' in n.image.name or 'BaseColor' in n.image.name):
            n.image = img

# hair: import, then re-bind to OUR armature
before = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=HAIR)
for o in set(bpy.data.objects) - before:
    if o.type == 'MESH' and not o.name.startswith("Icosphere"):
        mw = o.matrix_world.copy(); o.parent = arm; o.matrix_world = mw
        for m in o.modifiers:
            if m.type == 'ARMATURE': m.object = arm
        o.name = "Hair"
for o in set(bpy.data.objects) - before:
    if o.type != 'MESH' or o.name.startswith("Icosphere"):
        bpy.data.objects.remove(o)

S = {
  # style: shirt colour, pants colour, shoe colour, sole colour, sleeve ('tee'|'long'), pants fit, shirt fit
  "nova": dict(shirt=(0.03, 0.26, 0.28), pants=(0.035, 0.045, 0.11), shoe=(0.80, 0.76, 0.66), sole=(0.12, 0.10, 0.10), sleeve="tee", pfit=0.020, sfit=0.032),
  "rio":  dict(shirt=(0.46, 0.25, 0.03), pants=(0.05, 0.055, 0.045), shoe=(0.30, 0.05, 0.04), sole=(0.85, 0.82, 0.76), sleeve="tee", pfit=0.020, sfit=0.030),
}[STYLE]

def mat(name, rgb, rough=0.85, sheen=0.4):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    if "Sheen Weight" in b.inputs: b.inputs["Sheen Weight"].default_value = sheen
    return m
M = dict(Shirt=mat("Shirt", S["shirt"]), Pants=mat("Pants", S["pants"]), Shoe=mat("Shoe", S["shoe"], 0.6, 0.1), Sole=mat("Sole", S["sole"], 0.7, 0))

me = body.data
gname = {g.index: g.name for g in body.vertex_groups}
def dom(v):
    best, bw = None, -1
    for g in v.groups:
        if g.weight > bw: best, bw = gname.get(g.group), g.weight
    return best or ""

# arm span measured on the rig: sleeves end at a fraction of the upper arm / forearm
B = arm.data.bones
ua0 = abs((arm.matrix_world @ B["upperarm_l"].head_local).x); ua1 = abs((arm.matrix_world @ B["upperarm_l"].tail_local).x)
fa1 = abs((arm.matrix_world @ B["lowerarm_l"].tail_local).x)
pel = (arm.matrix_world @ B["pelvis"].head_local).z
ank = (arm.matrix_world @ B["foot_l"].head_local).z
sleeve_end = ua0 + (ua1 - ua0) * 0.62 if S["sleeve"] == "tee" else fa1 - 0.03
waist = pel + 0.085

neck_z = (arm.matrix_world @ B["neck_01"].head_local).z + 0.015
HEM = dict(shirt_bottom=waist - 0.035, pants_top=waist + 0.03, pants_hem=ank + 0.045, shoe_top=ank + 0.075)
def region(p, d):
    """which garments cover this point (a point can sit in two: the tee overlaps the waistband)"""
    out = set()
    if (d.startswith(("spine_", "clavicle_", "pelvis", "upperarm_")) or (d == "neck_01" and p.z < neck_z)) and p.z > HEM["shirt_bottom"] - 0.03 and abs(p.x) < sleeve_end + 0.03:
        if not (d.startswith("thigh_")): out.add("Shirt")
    if d.startswith(("thigh_", "calf_", "pelvis", "foot_")) and p.z < HEM["pants_top"] + 0.03 and p.z > HEM["pants_hem"] - 0.03: out.add("Pants")
    if (d.startswith(("foot_", "ball_", "calf_"))) and p.z < HEM["shoe_top"] + 0.03: out.add("Shoe")
    return out
vreg = [region(body.matrix_world @ v.co, dom(v)) for v in me.vertices]
def cls(v): return None

vc = [None for v in me.vertices]

def shell(kind, push, hem, extra=None):
    """duplicate the faces of one garment and push them out along the normal"""
    bpy.ops.object.select_all(action='DESELECT')
    o = body.copy(); o.data = body.data.copy(); o.name = kind; bpy.context.collection.objects.link(o)
    bm = bmesh.new(); bm.from_mesh(o.data)
    bm.verts.ensure_lookup_table()
    kill = [f for f in bm.faces if not all(kind in vreg[v.index] for v in f.verts)]
    bmesh.ops.delete(bm, geom=kill, context='FACES')
    loose = [v for v in bm.verts if not v.link_faces]; bmesh.ops.delete(bm, geom=loose, context='VERTS')
    # the body is split along its UV seams: weld them, or the garment is loose panels that drift apart
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.002)
    bm.normal_update()
    # soften the anatomy under the cloth (no abs through a tee), then push out
    base = {v.index: v.co.copy() for v in bm.verts}
    for it in range(SMOOTH.get(kind, 4)):
        bmesh.ops.smooth_vert(bm, verts=[v for v in bm.verts if not v.is_boundary], factor=0.6, use_axis_x=True, use_axis_y=True, use_axis_z=True)
    bm.normal_update()
    for v in bm.verts:
        v.co += v.normal * push
        if extra: extra(v)
    # clean straight hems: cut on planes and drop what is beyond them
    for (co, no) in CUTS.get(kind, []):
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=co, plane_no=no, clear_outer=True)
    bm.to_mesh(o.data); bm.free()
    o.data.materials.clear(); o.data.materials.append(M[kind if kind != "Shoe" else "Shoe"])
    for p in o.data.polygons: p.use_smooth = True
    # hem thickness
    bpy.context.view_layer.objects.active = o; o.select_set(True)
    sol = o.modifiers.new("hem", 'SOLIDIFY'); sol.thickness = hem; sol.offset = -1; sol.use_rim = True
    bpy.ops.object.modifier_move_to_index(modifier="hem", index=0)
    bpy.ops.object.modifier_apply(modifier="hem")
    return o

SMOOTH = dict(Shirt=10, Pants=9, Shoe=18)
CUTS = dict(
  Shirt=[((0,0,HEM["shirt_bottom"]), (0,0,-1)), ((sleeve_end,0,0), (1,0,0)), ((-sleeve_end,0,0), (-1,0,0))],
  Pants=[((0,0,HEM["pants_top"]), (0,0,1)), ((0,0,HEM["pants_hem"]), (0,0,-1))],
  Shoe=[((0,0,HEM["shoe_top"]), (0,0,1))])
knee_z = (arm.matrix_world @ B["calf_l"].head_local).z
thigh_x = abs((arm.matrix_world @ B["thigh_l"].head_local).x)
chest_z = (arm.matrix_world @ B["spine_03"].head_local).z
def baggy_pants(v):
    # straight-leg skate fit: below mid-thigh the leg widens toward the hem instead of hugging the calf
    p = v.co; top = knee_z + 0.18
    if p.z < top:
        u = min(1.0, (top - p.z) / (top - HEM["pants_hem"]))
        ax = Vector((thigh_x * (1 if p.x > 0 else -1) * (1 - 0.25*u), 0.03, p.z))
        d = Vector((p.x - ax.x, p.y - ax.y, 0))
        if d.length > 1e-4: p += d.normalized() * (0.030 * u ** 0.8)
def boxy_tee(v):
    # a tee hangs straight down from the chest: fill the waist in toward the chest's width
    p = v.co
    if HEM["shirt_bottom"] < p.z < chest_z and abs(p.x) < sleeve_end * 0.6:
        u = 1 - (p.z - HEM["shirt_bottom"]) / (chest_z - HEM["shirt_bottom"])
        d = Vector((p.x, p.y - 0.01, 0))
        if d.length > 1e-4: p += d.normalized() * (0.028 * u)
shirt = shell("Shirt", S["sfit"], 0.006, boxy_tee)
# a tee hangs from the shoulders: move hip/thigh influence onto the lower spine so the hem
# follows the torso instead of flaring off it when the hips and chest bend apart
vg = {g.name: g for g in shirt.vertex_groups}
tgt = vg.get("spine_01") or shirt.vertex_groups.new(name="spine_01")
for v in shirt.data.vertices:
    moved = 0.0
    for g in list(v.groups):
        n = shirt.vertex_groups[g.group].name
        if n == "pelvis" or n.startswith("thigh_"):
            moved += g.weight * (0.75 if n == "pelvis" else 1.0)
            shirt.vertex_groups[g.group].add([v.index], g.weight * (0.25 if n == "pelvis" else 0.0), "REPLACE")
    if moved > 0: tgt.add([v.index], moved, "ADD")
pants = shell("Pants", S["pfit"], 0.006, baggy_pants)
# shoes: chunkier than the bare foot, flat sole
def shoe_shape(v):
    p = v.co
    if p.z < 0.02: p.z = min(p.z, -0.004)         # flatten + thicken the sole down to the ground
shoe = shell("Shoe", 0.026, 0.008, shoe_shape)
# sole material on the lowest band: cut a clean line first so the sole edge is straight
sbm = bmesh.new(); sbm.from_mesh(shoe.data)
bmesh.ops.bisect_plane(sbm, geom=sbm.verts[:]+sbm.edges[:]+sbm.faces[:], plane_co=(0,0,0.022), plane_no=(0,0,1))
sbm.to_mesh(shoe.data); sbm.free()
shoe.data.materials.append(M["Sole"])
for poly in shoe.data.polygons:
    zc = sum((shoe.matrix_world @ shoe.data.vertices[i].co).z for i in poly.vertices) / len(poly.vertices)
    if zc < 0.022: poly.material_index = 1

# hide the bare body where it is fully covered, so nothing pokes through the cloth
bm = bmesh.new(); bm.from_mesh(me)
d_of = [dom(v) for v in me.vertices]
def inside(i):
    p = body.matrix_world @ me.vertices[i].co; r = vreg[i]
    if "Shirt" in r and p.z > HEM["shirt_bottom"] + 0.05 and abs(p.x) < sleeve_end - 0.05 and p.z < neck_z - 0.04 and not d_of[i].startswith(("upperarm_", "clavicle_")) and abs(p.x) < ua0 - 0.02: return True   # keep skin under sleeves + armpits
    if "Pants" in r and HEM["pants_hem"] - 0.02 < p.z < HEM["pants_top"] - 0.03: return True   # the shoe covers below the hem
    if "Shoe" in r and p.z < HEM["shoe_top"] - 0.005: return True
    if d_of[i].startswith(("calf_", "foot_", "ball_")) and p.z < HEM["shoe_top"]: return True
    return False
cover = [f for f in bm.faces if all(inside(v.index) for v in f.verts)]
bmesh.ops.delete(bm, geom=cover, context='FACES'); bm.to_mesh(me); bm.free()

print("DRESSED", STYLE, {o.name: len(o.data.vertices) for o in (shirt, pants, shoe)}, "hidden", len(cover))
bpy.ops.wm.save_as_mainfile(filepath=OUT)
