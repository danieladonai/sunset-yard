# Sunset Yard - hand-keyed skate clips on the Quaternius mannequin (CC0).
# Run: Blender -b --python author.py -- <mannequin.glb> <out_dir>
# Board frame: board centred at origin, NOSE = +X, deck top z = DECK, ground z = 0.
# Regular stance: left foot front. The rider's toe side is -Y.
import bpy, sys, math
from mathutils import Matrix, Vector, Euler, Quaternion

SRC, OUT = sys.argv[-2], sys.argv[-1]
FPS = 30
DECK = 0.108          # deck top above ground (matches the game: DECK_Y0*BOARD_S + DECK_TOP)
ANK = 0.104           # ankle above sole, flat foot (measured on the mannequin)
R = math.radians

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
for o in list(bpy.data.objects):
    if o.name.startswith("Icosphere"): bpy.data.objects.remove(o)
arm = bpy.data.objects["Rig"]; me = bpy.data.objects["Mannequin"]
arm.animation_data_clear()
for a in list(bpy.data.actions): bpy.data.actions.remove(a)
sc = bpy.context.scene; sc.render.fps = FPS
PB = arm.pose.bones
for pb in PB: pb.rotation_mode = 'QUATERNION'; pb.rotation_quaternion = (1,0,0,0); pb.location = (0,0,0)
rest = {b.name: arm.matrix_world @ b.matrix_local for b in arm.data.bones}

def ctrl(name, bone=None):
    """animated control C (location + 'YXZ' euler delta) with child O = bone rest rotation"""
    c = bpy.data.objects.new("C_"+name, None); sc.collection.objects.link(c)
    c.rotation_mode = 'YXZ'
    o = None
    if bone:
        o = bpy.data.objects.new("O_"+name, None); sc.collection.objects.link(o)
        o.parent = c; o.matrix_parent_inverse = Matrix.Identity(4)
        o.matrix_basis = rest[bone].to_quaternion().to_matrix().to_4x4()
    return c, o

C = {}
for n, b in [("pelvis","DEF-hips"),("chest","DEF-spine.003"),("spine2","DEF-spine.002"),("spine1","DEF-spine.001"),
             ("head","DEF-head"),("neck","DEF-neck"),("footL","DEF-foot.L"),("footR","DEF-foot.R"),
             ("toeL","DEF-toe.L"),("toeR","DEF-toe.R")]:
    C[n] = ctrl(n, b)
for n in ["kneeL","kneeR","handL","handR","elbowL","elbowR"]:
    C[n] = ctrl(n)

def con(bone, typ, tgt, **kw):
    c = PB[bone].constraints.new(typ); c.target = tgt
    for k, v in kw.items(): setattr(c, k, v)
    return c
con("DEF-hips", 'COPY_TRANSFORMS', C["pelvis"][1])
con("DEF-spine.001", 'COPY_ROTATION', C["spine1"][1])
con("DEF-spine.002", 'COPY_ROTATION', C["spine2"][1])
con("DEF-spine.003", 'COPY_ROTATION', C["chest"][1])
con("DEF-neck", 'COPY_ROTATION', C["neck"][1])
con("DEF-head", 'COPY_ROTATION', C["head"][1])
ik = {}
for s in "LR":
    ik["leg"+s] = con("DEF-shin."+s, 'IK', C["foot"+s][0], chain_count=2, pole_target=C["knee"+s][0])
    con("DEF-foot."+s, 'COPY_ROTATION', C["foot"+s][1])
    con("DEF-toe."+s, 'COPY_ROTATION', C["toe"+s][1])
    ik["arm"+s] = con("DEF-forearm."+s, 'IK', C["hand"+s][0], chain_count=2, pole_target=C["elbow"+s][0])

# ---------------------------------------------------------------- keying helpers
def key(name, f, loc=None, rot=None, interp='BEZIER'):
    c = C[name][0]
    if loc is not None: c.location = loc; c.keyframe_insert("location", frame=f)
    if rot is not None: c.rotation_euler = [R(rot[1]), R(rot[2]), R(rot[0])]; c.keyframe_insert("rotation_euler", frame=f)  # rot=(yaw,pitch,roll) deg
    return c

def set_interp(name, frames, mode):
    ad = C[name][0].animation_data
    if not ad: return
    for fc in ad.action.fcurves if hasattr(ad.action,'fcurves') else []:
        for kp in fc.keyframe_points:
            if int(round(kp.co.x)) in frames: kp.interpolation = mode

def fcurves_of(obj):
    act = obj.animation_data.action
    if hasattr(act, "fcurves"): return list(act.fcurves)
    out = []   # Blender 5 layered actions
    for layer in act.layers:
        for strip in layer.strips:
            for bag in strip.channelbags: out += list(bag.fcurves)
    return out

def wrap_cyclic(frame_len):
    """make every control loop seamlessly: cyclic modifier on all curves"""
    for n, (c, o) in C.items():
        if not c.animation_data: continue
        for fc in fcurves_of(c):
            m = fc.modifiers.new('CYCLES')
    return

def leg_pole(foot_loc, yaw_deg, hip_loc, fwd=0.6):
    """knee pole: in front of the knee, along where the toes point"""
    d = Vector((math.sin(R(yaw_deg)), -math.cos(R(yaw_deg)), 0))   # rest foot points -Y; yaw rotates CCW
    mid = (Vector(foot_loc) + Vector(hip_loc)) * 0.5
    return tuple(mid + d * fwd)

def body_dir(yaw):  # where the body faces (rest faces -Y)
    return Vector((math.sin(R(yaw)), -math.cos(R(yaw)), 0))

# ---------------------------------------------------------------- CLIPS
def clip_ride(L=60):
    """relaxed riding stance: feet across the bolts, knees soft, a slow breath/sway"""
    for f in range(0, L+1, 10):
        ph = 2*math.pi*f/L
        pz = 0.925 + 0.010*math.sin(ph)
        py = 0.02 + 0.008*math.sin(ph+0.7)
        hip = (-0.02, py, pz)
        key("pelvis", f, hip, (22, 8, 0))
        key("spine1", f, None, (26, 9, 0)); key("spine2", f, None, (30, 11, 0))
        key("chest", f, None, (34, 12+1.5*math.sin(ph), 0))
        key("neck", f, None, (62, 8, 0)); key("head", f, None, (80, 6, 0))
        fl = (0.19, 0.005, DECK+ANK); fr = (-0.24, 0.0, DECK+ANK)
        key("footL", f, fl, (32, 0, 0)); key("footR", f, fr, (4, 0, 0))
        key("toeL", f, None, (32, 0, 0)); key("toeR", f, None, (4, 0, 0))
        key("kneeL", f, leg_pole(fl, 32, hip)); key("kneeR", f, leg_pole(fr, 4, hip))
        # arms relaxed, a little out from the body for balance
        bd = body_dir(34); rt = Vector((-bd.y, bd.x, 0))  # rider's left
        hl = Vector(hip) + rt*0.30 + bd*0.06 + Vector((0,0,-0.05+0.01*math.sin(ph+1)))
        hr = Vector(hip) - rt*0.30 + bd*0.04 + Vector((0,0,-0.07+0.01*math.sin(ph+2)))
        key("handL", f, tuple(hl)); key("handR", f, tuple(hr))
        key("elbowL", f, tuple(Vector(hip)+rt*0.5-bd*0.3+Vector((0,0,0.3))))
        key("elbowR", f, tuple(Vector(hip)-rt*0.5-bd*0.3+Vector((0,0,0.3))))
    return L

PUSH_STRIDE = 0.56    # back foot travel while planted (board-frame metres)
PUSH_PLANT = 14       # frames the foot is on the ground
def clip_push(L=32):
    """push loop, regular stance: front foot turned to the nose, back foot plants on the
    toe side beside the front truck, drives back with the ground, peels heel-first-off,
    swings forward. Planted foot moves back LINEARLY at stride/plant (ground speed)."""
    v = PUSH_STRIDE/PUSH_PLANT
    x0 = 0.15
    # back foot (R): (frame, x, z, yaw, pitch)
    bk = []
    BH, BV = 0.149, 0.089                     # ankle -> ball of foot, horizontal / vertical (rest)
    for f in range(0, PUSH_PLANT+1, 1):
        lift = max(0, (f-8)/6)                  # heel peels in the last part of the plant
        th = R(38*lift*lift)
        ball = (x0 + BH) - v*f                   # the ball of the foot rides the ground
        bk.append((f, ball - (BH*math.cos(th) - BV*math.sin(th)), 0.015 + BH*math.sin(th) + BV*math.cos(th), 88, math.degrees(th)))
    bk += [(17, x0 - v*PUSH_PLANT - 0.10, 0.22, 86, 34),
           (21, -0.30, 0.235, 84, 14),
           (25, -0.04, 0.20, 86, 2),
           (29, 0.15, 0.14, 88, -2),
           (31, 0.165, 0.112, 88, 0),
           (32, x0, ANK, 88, 0)]
    fy = -0.19
    for f, x, z, yaw, pit in bk:
        key("footR", f, (x, fy, z), (yaw, pit, 0))
        key("toeR", f, None, (yaw, 0 if f <= PUSH_PLANT else pit*0.4, 0))   # toes flat while the ball is down
    # pelvis: sinks as the leg reaches back, rises on the swing; drifts over the front foot
    pel = {0:(0.07,-0.07,0.875), 7:(0.06,-0.075,0.855), 14:(0.03,-0.08,0.845), 19:(0.06,-0.07,0.87), 26:(0.085,-0.065,0.89), 32:(0.07,-0.07,0.875)}
    ptch = {0:24, 7:28, 14:32, 19:27, 26:21, 32:24}
    for f in sorted(pel):
        key("pelvis", f, pel[f], (78, ptch[f], 0))
        key("spine1", f, None, (82, ptch[f]+3, 0)); key("spine2", f, None, (86, ptch[f]+6, 0))
        key("chest", f, None, (90, ptch[f]+6, -3))
        key("neck", f, None, (90, ptch[f]-8, 0)); key("head", f, None, (90, 4, 0))   # eyes up the path
    fl = (0.20, -0.005, DECK+ANK)
    for f in (0, 32):
        key("footL", f, fl, (78, 0, 0)); key("toeL", f, None, (78, 0, 0))
    # knee poles follow the toes; back knee stays forward-ish through the swing
    for f in sorted(set([b[0] for b in bk] + list(pel))):
        sc.frame_set(f)
        hip = tuple(C["pelvis"][0].location)
        key("kneeL", f, leg_pole(fl, 78, hip, 0.8))
        key("kneeR", f, leg_pole(tuple(C["footR"][0].location), 88, hip, 0.8))
    # arms counter-swing the pushing leg (right arm forward as right leg drives back)
    for f in range(0, L+1, 4):
        s = math.cos(2*math.pi*(f - 14)/L)       # +1 at full extension (f=14)
        sc.frame_set(f); hip = Vector(C["pelvis"][0].location)
        key("handR", f, tuple(hip + Vector((0.16 + 0.22*s, -0.27, 0.10 + 0.08*s))))
        key("handL", f, tuple(hip + Vector((0.08 - 0.16*s, 0.22, 0.06 - 0.03*s))))
        key("elbowR", f, tuple(hip + Vector((-0.4, -0.7, 0.4))))
        key("elbowL", f, tuple(hip + Vector((-0.4, 0.7, 0.4))))
    # the plant is linear (the foot moves with the ground), everything else eases
    for fc in fcurves_of(C["footR"][0]):
        if fc.data_path == "location" and fc.array_index == 0:
            for kp in fc.keyframe_points:
                if kp.co.x <= PUSH_PLANT: kp.interpolation = 'LINEAR'
    return L

# ---------------------------------------------------------------- pole calibration
def calibrate_poles():
    sc.frame_set(0); dg = bpy.context.evaluated_depsgraph_get()
    for nm, knee_bone, pole in [("legL","DEF-shin.L","kneeL"),("legR","DEF-shin.R","kneeR"),
                                ("armL","DEF-forearm.L","elbowL"),("armR","DEF-forearm.R","elbowR")]:
        best = None
        for a in range(-180, 180, 5):
            ik[nm].pole_angle = R(a); dg.update()
            j = arm.matrix_world @ arm.pose.bones[knee_bone].head
            d = (j - C[pole][0].matrix_world.translation).length
            if best is None or d < best[0]: best = (d, a)
        ik[nm].pole_angle = R(best[1]); print("POLE", nm, best[1])

# ---------------------------------------------------------------- bake + export
def build(name, fn):
    for n,(c,o) in C.items(): c.animation_data_clear()
    L = fn()
    wrap_cyclic(L)
    calibrate_poles()
    sc.frame_start, sc.frame_end = 0, L
    bpy.context.view_layer.objects.active = arm; arm.select_set(True)
    bpy.ops.object.mode_set(mode='POSE'); bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.nla.bake(frame_start=0, frame_end=L, only_selected=True, visual_keying=True,
                     clear_constraints=False, use_current_action=False, bake_types={'POSE'})
    bpy.ops.object.mode_set(mode='OBJECT')
    act = arm.animation_data.action; act.name = name; act.use_fake_user = True
    # contact report: sole height of each foot per frame (checks planted foot + deck contact)
    rep = []
    for f in range(0, L+1):
        sc.frame_set(f)
        # evaluate the baked pose only
        for s in "LR":
            pass
    return L

# measure planted-foot drift on the baked clip (with constraints muted)
def contact_report(L, name):
    for pb in PB:
        for c in pb.constraints: c.mute = True
    out = []
    for f in range(0, L+1):
        sc.frame_set(f)
        a = [arm.matrix_world @ PB["DEF-foot."+s].head for s in "LR"]
        t = [arm.matrix_world @ PB["DEF-toe."+s].tail for s in "LR"]
        out.append((f, a, t))
    for pb in PB:
        for c in pb.constraints: c.mute = False
    return out

import json
results = {}
for name, fn in [("Ride_Idle", clip_ride), ("Push_Loop", clip_push)]:
    L = build(name, fn)
    rep = contact_report(L, name)
    results[name] = [{"f":f, "ankL":[round(v,3) for v in a[0]], "ankR":[round(v,3) for v in a[1]], "toeR":[round(v,3) for v in t[1]], "toeL":[round(v,3) for v in t[0]]} for f,a,t in rep]
    arm.animation_data.action = None
    for pb in PB: pb.rotation_quaternion=(1,0,0,0); pb.location=(0,0,0)

# strip controls and constraints, keep both actions as NLA tracks for export
for pb in PB:
    for c in list(pb.constraints): pb.constraints.remove(c)
for n,(c,o) in C.items():
    if o: bpy.data.objects.remove(o)
    bpy.data.objects.remove(c)
ad = arm.animation_data or arm.animation_data_create()
for a in bpy.data.actions:
    if a.name in ("Ride_Idle","Push_Loop"):
        tr = ad.nla_tracks.new(); tr.name = a.name; tr.strips.new(a.name, 0, a)
bpy.ops.wm.save_as_mainfile(filepath=OUT + "/skater_clips.blend")
bpy.ops.export_scene.gltf(filepath=OUT + "/skater_clips.glb", export_format='GLB',
                          export_animation_mode='ACTIONS', export_force_sampling=True, export_frame_step=1)
json.dump(results, open(OUT + "/contacts.json","w"))
print("DONE")
