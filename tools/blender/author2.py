# Sunset Yard v4 - skate clip + pose library, hand-keyed on a dressed Quaternius character.
# Blender -b <dressed.blend> --python author2.py -- <out.glb>
#
# BOARD FRAME: board centred at the origin, NOSE = +X, deck top z = DECK, ground z = 0 (the SOLE
# of the shoe sits exactly on z = 0 / on the deck). Regular stance, left foot forward; the rider
# faces -Y (the toe edge). Animated control empties drive IK legs/arms and copy-rotation spine,
# then everything is baked to plain bone keys and the controls are thrown away.
#
# LIFTED POSES: Air_Tuck is authored with the deck 0.20 up, the grabs with it 0.47 up - the same
# lifts the game applies to the board (boardLift), so blending pose weights moves the feet exactly
# with the board. The game then only corrects the residual (pitch, roll, flip-free wobble).
import bpy, sys, math, json
from mathutils import Matrix, Vector, Quaternion

OUT = sys.argv[-1]
FPS = 30
DECK = 0.108
LIFT_TUCK, LIFT_GRAB = 0.30, 0.47
MELON_UP = 0.10      # the melon pulls the board 10cm higher, up to the hand
R = math.radians
sc = bpy.context.scene; sc.render.fps = FPS

arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
arm.animation_data_clear()
for a in list(bpy.data.actions): bpy.data.actions.remove(a)
PB = arm.pose.bones
MAP = dict(hips="pelvis", s1="spine_01", s2="spine_02", s3="spine_03", neck="neck_01", head="Head",
           thighL="thigh_l", shinL="calf_l", footL="foot_l", toeL="ball_l", thighR="thigh_r", shinR="calf_r", footR="foot_r", toeR="ball_r",
           uarmL="upperarm_l", farmL="lowerarm_l", handL="hand_l", uarmR="upperarm_r", farmR="lowerarm_r", handR="hand_r")
for pb in PB: pb.rotation_mode = 'QUATERNION'; pb.rotation_quaternion = (1,0,0,0); pb.location = (0,0,0)

# ---- measure the character: sole, ankle, ball pivot, leg length ----
shoe = bpy.data.objects.get("Shoe")
SOLE = min((shoe.matrix_world @ v.co).z for v in shoe.data.vertices) if shoe else 0.0
arm.location.z -= SOLE                      # shoe sole now sits on z = 0
bpy.context.view_layer.update()
W = lambda b, tail=False: arm.matrix_world @ (arm.data.bones[b].tail_local if tail else arm.data.bones[b].head_local)
ANK = W("foot_l").z
BALL = W("ball_l")
BH = abs(W("foot_l").y - BALL.y); BV = W("foot_l").z - BALL.z; BALLZ = BALL.z
LEG = (W("thigh_l") - W("calf_l")).length + (W("calf_l") - W("foot_l")).length
HIPOFF = W("thigh_l").z - W("pelvis").z
K = LEG / 0.83                               # poses were first tuned on a 0.83m leg
def PZ(z_old): return ANK + (z_old - 0.104) * K - HIPOFF * 0.3
print("MEASURE sole", round(SOLE,4), "ank", round(ANK,4), "BH", round(BH,3), "BV", round(BV,3), "leg", round(LEG,3))

rest = {b.name: arm.matrix_world @ b.matrix_local for b in arm.data.bones}
ARM = (W("upperarm_l") - W("lowerarm_l")).length + (W("lowerarm_l") - W("hand_l")).length
def ctrl(name, bone=None):
    c = bpy.data.objects.new("C_"+name, None); sc.collection.objects.link(c); c.rotation_mode = 'YXZ'
    o = None
    if bone:
        o = bpy.data.objects.new("O_"+name, None); sc.collection.objects.link(o)
        o.parent = c; o.matrix_parent_inverse = Matrix.Identity(4)
        o.matrix_basis = rest[bone].to_quaternion().to_matrix().to_4x4()
    return c, o
C = {}
for n, b in [("pelvis","hips"),("chest","s3"),("spine2","s2"),("spine1","s1"),("head","head"),("neck","neck"),
             ("footL","footL"),("footR","footR"),("toeL","toeL"),("toeR","toeR")]:
    C[n] = ctrl(n, MAP[b])
for n in ["kneeL","kneeR","handL","handR","elbowL","elbowR"]: C[n] = ctrl(n)
def con(bone, typ, tgt, **kw):
    c = PB[MAP[bone]].constraints.new(typ); c.target = tgt
    for k, v in kw.items(): setattr(c, k, v)
    return c
con("hips", 'COPY_TRANSFORMS', C["pelvis"][1])
for b, n in [("s1","spine1"),("s2","spine2"),("s3","chest"),("neck","neck"),("head","head")]: con(b, 'COPY_ROTATION', C[n][1])
ik = {}
for s in "LR":
    ik["leg"+s] = con("shin"+s, 'IK', C["foot"+s][0], chain_count=2, pole_target=C["knee"+s][0])
    con("foot"+s, 'COPY_ROTATION', C["foot"+s][1]); con("toe"+s, 'COPY_ROTATION', C["toe"+s][1])
    ik["arm"+s] = con("farm"+s, 'IK', C["hand"+s][0], chain_count=2, pole_target=C["elbow"+s][0])

# ---- relaxed hands: curl every finger toward the palm (axis found per bone) ----
FINGERS = [b.name for b in arm.data.bones if any(b.name.startswith(f) for f in ("index_","middle_","ring_","pinky_","thumb_")) and "leaf" not in b.name]
def curl_axes():
    ax = {}
    for n in FINGERS:
        pb = PB[n]; best = None
        for a, v in [("X",(1,0,0)),("X-",(-1,0,0)),("Z",(0,0,1)),("Z-",(0,0,-1))]:
            pb.rotation_quaternion = Quaternion(Vector(v), R(40)); bpy.context.view_layer.update()
            z = (arm.matrix_world @ pb.tail).z
            if best is None or z < best[0]: best = (z, v)
            pb.rotation_quaternion = (1,0,0,0)
        ax[n] = Vector(best[1])
    bpy.context.view_layer.update(); return ax
CURL = curl_axes()
def key_fingers(frames, amt=1.0):
    for n in FINGERS:
        deg = (22 if n.startswith("thumb") else (38 if "_01_" in n else 48)) * amt
        PB[n].rotation_quaternion = Quaternion(CURL[n], R(deg))
        for f in frames: PB[n].keyframe_insert("rotation_quaternion", frame=f)

# ---- keying helpers ----
def key(name, f, loc=None, rot=None):
    c = C[name][0]
    if loc is not None: c.location = loc; c.keyframe_insert("location", frame=f)
    if rot is not None: c.rotation_euler = [R(rot[1]), R(rot[2]), R(rot[0])]; c.keyframe_insert("rotation_euler", frame=f)   # (yaw, pitch, roll) deg
def fcurves_of(obj):
    act = obj.animation_data.action
    if hasattr(act, "fcurves"): return list(act.fcurves)
    return [c for ly in act.layers for st in ly.strips for bag in st.channelbags for c in bag.fcurves]
def fwd(yaw): return Vector((math.sin(R(yaw)), -math.cos(R(yaw)), 0))     # rest faces -Y; yaw turns CCW
def left(yaw): d = fwd(yaw); return Vector((-d.y, d.x, 0))                 # rider's left (rest: +X)
def knee_pole(foot, yaw, hip, reach=0.7, out=0.0, side=Vector()):
    return tuple((Vector(foot) + Vector(hip)) * 0.5 + fwd(yaw) * reach + side * out)

def pose(f, P):
    """key a full-body pose at frame f from a compact description (see POSES)"""
    pel = Vector(P["pel"]); py, pp, pr = P.get("prot", (20, 8, 0))
    key("pelvis", f, tuple(pel), (py, pp, pr))
    cy, cp, cr = P.get("chest", (py+12, pp+4, pr))
    key("spine1", f, None, (py+(cy-py)*0.33, pp+(cp-pp)*0.33, pr+(cr-pr)*0.33))
    key("spine2", f, None, (py+(cy-py)*0.66, pp+(cp-pp)*0.66, pr+(cr-pr)*0.66))
    key("chest", f, None, (cy, cp, cr))
    hy, hp = P.get("head", (cy+45, 4))
    key("neck", f, None, ((cy+hy)/2, (cp+hp)/2, cr*0.5)); key("head", f, None, (hy, hp, 0))
    for s in "LR":
        x, y, z, yaw, pit = P["f"+s]
        key("foot"+s, f, (x, y, z), (yaw, pit, 0))
        key("toe"+s, f, None, (yaw, P.get("toe"+s, pit), 0))
        key("knee"+s, f, knee_pole((x,y,z), yaw + P.get("kneeYaw"+s, 0), tuple(pel), 0.7))
    sc.frame_set(f); bpy.context.view_layer.update()
    for s in "LR":
        sh = arm.matrix_world @ PB[MAP["uarm"+s]].head
        sd = left(cy) * (1 if s == "L" else -1); fd = fwd(cy)
        a = P.get("a"+s, (0.35, 0.9, 0.12, 0.93))            # (out, down, forward, reach as a fraction of the arm)
        if isinstance(a, tuple) and len(a) == 4:
            d = (sd * a[0] + Vector((0, 0, -a[1])) + fd * a[2]).normalized()
            hx = sh + d * ARM * a[3]
        else: hx = Vector(a)                                   # absolute target (grabs)
        key("hand"+s, f, tuple(hx))
        # elbow bends back and a little out, the way a relaxed arm hangs
        key("elbow"+s, f, tuple((sh + hx) * 0.5 - fd * 0.45 + sd * 0.20 + Vector((0, 0, -0.05)) + Vector(P.get("elb"+s, (0,0,0)))))

def calibrate_poles():
    dg = bpy.context.evaluated_depsgraph_get()
    for nm, jb, pole in [("legL","shinL","kneeL"),("legR","shinR","kneeR"),("armL","farmL","elbowL"),("armR","farmR","elbowR")]:
        best = None
        for a in range(-180, 180, 5):
            ik[nm].pole_angle = R(a); dg.update()
            j = arm.matrix_world @ PB[MAP[jb]].head
            d = (j - C[pole][0].matrix_world.translation).length
            if best is None or d < best[0]: best = (d, a)
        ik[nm].pole_angle = R(best[1])

# ------------------------------------------------------------------ the rider's body in board space
ZD = DECK + ANK                              # ankle height with the foot flat on the deck
def ctr(yaw): return (0.0, 0.0)
def arms_relaxed(pel, cy, spread=0.30, fwdL=0.06, fwdR=0.04, dz=-0.05, up=0.0):
    p = Vector(pel); l = left(cy); fd = fwd(cy)
    return (tuple(p + l*spread + fd*fwdL + Vector((0,0,dz+up))), tuple(p - l*spread + fd*fwdR + Vector((0,0,dz-0.02+up))))

STANCE_L = (0.20, 0.050, ZD, 30, 0)          # front foot over the front bolts, angled toward the nose
STANCE_R = (-0.235, 0.055, ZD, 4, 0)         # back foot across the tail bolts

def P_idle(ph=0.0):
    pel = (-0.02, 0.03 + 0.008*math.sin(ph+0.7), PZ(0.925 + 0.010*math.sin(ph)))
    return dict(pel=pel, prot=(22, 8, 0), chest=(34, 12 + 1.5*math.sin(ph), 0), head=(80, 6), fL=STANCE_L, fR=STANCE_R, aL=(0.30, 0.95, 0.15, 0.92), aR=(0.30, 0.95, 0.05, 0.92))
def P_crouch():
    pel = (-0.03, 0.06, PZ(0.74))
    return dict(pel=pel, prot=(20, 26, 0), chest=(30, 40, 0), head=(78, -18), fL=STANCE_L, fR=STANCE_R, aL=(0.45, 0.60, 0.55, 0.90), aR=(0.45, 0.70, 0.25, 0.90))
def P_pop():
    # back leg snaps straight on the tail, front foot drags up toward the nose, arms rise
    pel = (-0.05, 0.03, PZ(0.95))
    return dict(pel=pel, prot=(24, 10, -4), chest=(34, 14, -4), head=(80, 6),
                fL=(0.33, 0.045, ZD + 0.05, 42, -18), fR=(-0.33, 0.055, ZD, 4, 10), toeL=0, toeR=0, aL=(0.62, 0.62, 0.34, 0.90), aR=(0.62, 0.66, -0.06, 0.90))
def P_tuck():
    z = ZD + LIFT_TUCK; pel = (-0.02, 0.06, PZ(0.88))
    return dict(pel=pel, prot=(20, 30, 0), chest=(30, 34, 0), head=(76, -18),
                fL=(0.20, 0.045, z, 30, 0), fR=(-0.23, 0.05, z, 4, 0), aL=(0.60, 0.66, 0.36, 0.88), aR=(0.60, 0.70, -0.02, 0.88))
def P_flip():
    # feet off the board over the flip: front foot flicked out toward the nose/heel side, back foot up
    z = ZD + LIFT_TUCK + 0.10; pel = (-0.02, 0.05, PZ(0.92))
    return dict(pel=pel, prot=(20, 18, 0), chest=(30, 20, 0), head=(72, -14),
                fL=(0.30, 0.10, z + 0.02, 36, -12), fR=(-0.26, 0.04, z - 0.03, 6, 6), aL=(0.66, 0.58, 0.32, 0.90), aR=(0.66, 0.62, -0.06, 0.90))
def P_grab(kind):
    z = ZD + LIFT_GRAB; pel = (-0.02, 0.07, PZ(0.93))
    if kind == "indy":     # back hand, toe edge, between the feet
        hl, _ = arms_relaxed(pel, 30, spread=0.52, fwdL=0.10, dz=0.30)
        hr = (-0.03, -0.12, DECK + LIFT_GRAB + 0.02)
        pel = (-0.02, 0.06, PZ(0.79))
        return dict(pel=pel, prot=(20, 52, -10), chest=(22, 88, -18), head=(66, -52),
                    fL=(0.20, 0.045, z, 30, 0), fR=(-0.23, 0.05, z, 4, 0), aL=(0.90, 0.10, 0.20, 0.95), aR=(-0.03, -0.12, DECK + LIFT_GRAB + 0.02), elbR=(0, 0, 0.1))
    else:                  # melon: front hand reaches behind the front leg to the heel edge
        _, hr = arms_relaxed(pel, 30, spread=0.52, fwdR=0.0, dz=0.32)
        hl = (0.06, 0.15, DECK + LIFT_GRAB + 0.02)
        pel = (-0.02, 0.14, PZ(0.79))
        return dict(pel=pel, prot=(26, 50, 16), chest=(44, 84, 30), head=(80, -50),
                    fL=(0.20, 0.045, z + MELON_UP, 30, 0), fR=(-0.23, 0.05, z + MELON_UP, 4, 0), aL=(0.03, 0.10, DECK + LIFT_GRAB + MELON_UP + 0.03), aR=(0.90, 0.10, -0.10, 0.95), elbL=(0, 0.1, 0.15))
def P_carve(side):
    # toe side (-Y) : knees forward, hips drop over the toe edge. heel side (+Y): sit back over the heels
    s = -1 if side == "toe" else 1
    pel = (-0.02, 0.03 + s*0.10, PZ(0.86 if side == "toe" else 0.84))
    return dict(pel=pel, prot=(22, 14 if side == "toe" else 4, s*10), chest=(34, 20 if side == "toe" else 6, s*14), head=(80, 4),
                fL=STANCE_L, fR=STANCE_R, aL=(0.60, 0.70, 0.20, 0.93), aR=(0.60, 0.75, 0.00, 0.93))
def P_manual():
    # weight over the back truck, front leg long, arms wide
    pel = (-0.13, 0.03, PZ(0.90))
    return dict(pel=pel, prot=(24, 4, 0), chest=(36, 8, 0), head=(80, 8), fL=(0.21, 0.045, ZD, 34, 0), fR=(-0.25, 0.055, ZD, 4, 0), aL=(0.74, 0.52, 0.18, 0.92), aR=(0.74, 0.56, -0.08, 0.92))
def P_grind():
    pel = (-0.02, 0.04, PZ(0.86))
    return dict(pel=pel, prot=(22, 16, 0), chest=(32, 20, 0), head=(84, 0), fL=STANCE_L, fR=STANCE_R, aL=(0.78, 0.48, 0.22, 0.92), aR=(0.78, 0.52, -0.04, 0.92))
def P_bail():
    # slammed onto the concrete: sat down hard on the heel side, hands back, legs out toward the toe edge
    pel = (0.0, 0.22, 0.13)
    return dict(pel=pel, prot=(16, -34, 0), chest=(16, -20, 0), head=(20, 22),
                fL=(0.26, -0.42, ANK + 0.03, 20, -30), fR=(-0.14, -0.48, ANK + 0.02, -8, -35), toeL=-30, toeR=-35,
                aL=(0.22, 0.46, 0.05), aR=(-0.20, 0.48, 0.05), kneeYawL=0, kneeYawR=0)

def P_brake():
    # foot brake: front foot turned to the nose, back foot off the tail and dragging flat on the
    # toe side behind the front truck, weight sat down on the front leg
    pel = (0.04, -0.06, PZ(0.86))
    return dict(pel=pel, prot=(74, 20, 0), chest=(84, 22, -2), head=(90, 2),
                fL=(0.20, 0.03, ZD, 78, 0), fR=(-0.12, -0.20, ANK + 0.004, 84, -6), toeR=-6,
                aL=(0.55, 0.75, 0.25, 0.93), aR=(0.55, 0.75, 0.05, 0.93), kneeYawR=10)
def clip_slam():
    """0.9s one-shot: board shoots out, you fall back, hands catch, butt lands, rock, settle"""
    fl, fr = (0.22, 0.02, ZD, 30, -10), (-0.22, 0.03, ZD, 4, -6)
    S = [
     (0,  dict(pel=(0.0, 0.02, PZ(0.90)), prot=(22, -4, 0), chest=(30, -10, 0), head=(76, 0),
               fL=fl, fR=fr, aL=(0.7, 0.1, 0.45, 0.95), aR=(0.7, 0.15, 0.3, 0.95))),
     (6,  dict(pel=(0.0, 0.10, PZ(0.66)), prot=(20, -22, 0), chest=(24, -30, 0), head=(50, 22),
               fL=(0.25, -0.20, ANK + 0.08, 25, -25), fR=(-0.16, -0.18, ANK + 0.14, 0, -22), toeL=-25, toeR=-22,
               aL=(0.30, 0.40, 0.30), aR=(-0.24, 0.42, 0.30))),
     (11, dict(pel=(0.0, 0.22, 0.12), prot=(16, -34, 0), chest=(16, -40, 0), head=(24, 32),
               fL=(0.27, -0.44, ANK + 0.02, 20, -35), fR=(-0.13, -0.40, ANK + 0.16, -8, -20), toeL=-35, toeR=-20,
               aL=(0.26, 0.50, 0.035), aR=(-0.22, 0.50, 0.035))),
     (16, dict(pel=(0.0, 0.20, 0.15), prot=(16, -26, 0), chest=(16, -22, 0), head=(20, 20),
               fL=(0.27, -0.45, ANK + 0.02, 20, -35), fR=(-0.13, -0.38, ANK + 0.20, -8, -14), toeL=-35, toeR=-14,
               aL=(0.26, 0.48, 0.035), aR=(-0.22, 0.48, 0.035))),
     (26, dict(pel=(0.0, 0.21, 0.13), prot=(16, -30, 0), chest=(16, -28, 0), head=(20, 30),
               fL=(0.27, -0.46, ANK + 0.02, 20, -35), fR=(-0.13, -0.40, ANK + 0.18, -8, -16), toeL=-35, toeR=-16,
               aL=(0.26, 0.49, 0.035), aR=(-0.22, 0.49, 0.035))),
    ]
    for f, P in S: pose(f, P)
    return 26
clip_slam.anim = True
POSES = [("Slam", clip_slam), ("Brake", P_brake), ("Crouch", P_crouch), ("Pop", P_pop), ("Air_Tuck", P_tuck), ("Air_Flip", P_flip),
         ("Grab_Indy", lambda: P_grab("indy")), ("Grab_Melon", lambda: P_grab("melon")),
         ("Carve_Toe", lambda: P_carve("toe")), ("Carve_Heel", lambda: P_carve("heel")),
         ("Manual", P_manual), ("Grind", P_grind), ("Bail", P_bail)]

def clip_idle(L=60):
    for f in range(0, L+1, 10): pose(f, P_idle(2*math.pi*f/L))
    return L

PUSH_STRIDE, PUSH_PLANT = 0.56, 14
def clip_push(L=32):
    v = PUSH_STRIDE / PUSH_PLANT; x0 = 0.15; fy = -0.19
    bk = []
    for f in range(0, PUSH_PLANT+1):
        lift = max(0, (f-8)/6); th = R(38*lift*lift)
        ball = (x0 + BH) - v*f
        bk.append((f, ball - (BH*math.cos(th) - BV*math.sin(th)), BALLZ + BH*math.sin(th) + BV*math.cos(th), 88, math.degrees(th)))
    k = K
    bk += [(17, x0 - v*PUSH_PLANT - 0.10, ANK + 0.12*k, 86, 34), (21, -0.30, ANK + 0.135*k, 84, 14),
           (25, -0.04, ANK + 0.10*k, 86, 2), (29, 0.15, ANK + 0.04*k, 88, -2), (31, 0.165, ANK + 0.008, 88, 0), (32, x0, ANK, 88, 0)]
    pel = {0:(0.08,-0.07,PZ(0.83)), 7:(0.07,-0.075,PZ(0.80)), 14:(0.04,-0.08,PZ(0.785)), 19:(0.07,-0.07,PZ(0.82)), 26:(0.095,-0.065,PZ(0.85)), 32:(0.08,-0.07,PZ(0.83))}
    ptch = {0:30, 7:34, 14:40, 19:33, 26:26, 32:30}
    fl = (0.20, 0.03, ZD)
    for f, x, z, yaw, pit in bk:
        key("footR", f, (x, fy, z), (yaw, pit, 0)); key("toeR", f, None, (yaw, 0 if f <= PUSH_PLANT else pit*0.4, 0))
    for f in sorted(pel):
        key("pelvis", f, pel[f], (78, ptch[f], 0))
        key("spine1", f, None, (82, ptch[f]+3, 0)); key("spine2", f, None, (86, ptch[f]+6, 0))
        key("chest", f, None, (90, ptch[f]+6, -3)); key("neck", f, None, (90, ptch[f]-8, 0)); key("head", f, None, (90, 4, 0))
    for f in (0, 32): key("footL", f, fl, (78, 0, 0)); key("toeL", f, None, (78, 0, 0))
    for f in sorted(set([b[0] for b in bk] + list(pel))):
        sc.frame_set(f); hip = tuple(C["pelvis"][0].location)
        key("kneeL", f, knee_pole(fl, 78, hip, 0.8)); key("kneeR", f, knee_pole(tuple(C["footR"][0].location), 88, hip, 0.8))
    for f in range(0, L+1, 4):
        s = math.cos(2*math.pi*(f - 14)/L); sc.frame_set(f); hip = Vector(C["pelvis"][0].location)
        key("handR", f, tuple(hip + Vector((0.10 + 0.26*s, -0.30, 0.06 + 0.12*s))))
        key("handL", f, tuple(hip + Vector((0.02 - 0.26*s, 0.28, 0.00 - 0.02*s))))
        key("elbowR", f, tuple(hip + Vector((-0.4, -0.7, 0.4)))); key("elbowL", f, tuple(hip + Vector((-0.4, 0.7, 0.4))))
    for fc in fcurves_of(C["footR"][0]):
        if fc.data_path == "location" and fc.array_index == 0:
            for kp in fc.keyframe_points:
                if kp.co.x <= PUSH_PLANT: kp.interpolation = 'LINEAR'
    return L

# ------------------------------------------------------------------ build, bake, export
def build(name, L_or_fn, cyclic):
    for n, (c, o) in C.items(): c.animation_data_clear()
    for n in FINGERS: PB[n].keyframe_delete if False else None
    if callable(L_or_fn) and (cyclic or getattr(L_or_fn, "anim", False)): L = L_or_fn()
    else: L = 1; P = L_or_fn(); pose(0, P); pose(1, P)
    if cyclic:
        for n, (c, o) in C.items():
            if c.animation_data:
                for fc in fcurves_of(c): fc.modifiers.new('CYCLES')
    key_fingers([0, L])
    sc.frame_set(0); calibrate_poles()
    bpy.context.view_layer.objects.active = arm; arm.select_set(True)
    bpy.ops.object.mode_set(mode='POSE'); bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.nla.bake(frame_start=0, frame_end=L, only_selected=True, visual_keying=True, clear_constraints=False,
                     use_current_action=False, bake_types={'POSE'})
    bpy.ops.object.mode_set(mode='OBJECT')
    act = arm.animation_data.action; act.name = name; act.use_fake_user = True
    # contact check on the baked clip
    for pb in PB:
        for c in pb.constraints: c.mute = True
    rep = []
    sc.frame_set(0)
    for s_ in "LR":
        tgt = C["hand"+s_][0].matrix_world.translation
        got = arm.matrix_world @ PB[MAP["hand"+s_]].head
        if (tgt-got).length > 0.06: print("REACH", name, s_, "miss", round((tgt-got).length,3))
    for f in range(0, L+1):
        sc.frame_set(f)
        rep.append([round((arm.matrix_world @ PB[MAP["foot"+s]].head).z, 3) for s in "LR"] + [round((arm.matrix_world @ PB[MAP["foot"+s]].head).x, 3) for s in "LR"])
    for pb in PB:
        for c in pb.constraints: c.mute = False
    arm.animation_data.action = None
    for pb in PB: pb.rotation_quaternion = (1,0,0,0); pb.location = (0,0,0)
    return rep

report = {}
report["Ride_Idle"] = build("Ride_Idle", clip_idle, True)
report["Push_Loop"] = build("Push_Loop", clip_push, True)
for name, fn in POSES: report[name] = build(name, fn, False)[:1]

for pb in PB:
    for c in list(pb.constraints): pb.constraints.remove(c)
for n, (c, o) in C.items():
    if o: bpy.data.objects.remove(o)
    bpy.data.objects.remove(c)
KEEP = set(["Ride_Idle", "Push_Loop"] + [n for n, _ in POSES])
for a in list(bpy.data.actions):
    if a.name not in KEEP: bpy.data.actions.remove(a)
ad = arm.animation_data or arm.animation_data_create()
ad.action = None
for a in bpy.data.actions:
    tr = ad.nla_tracks.new(); tr.name = a.name; tr.strips.new(a.name, 0, a)
meta = dict(DECK=DECK, ANK=ANK, SOLE=SOLE, LIFT_TUCK=LIFT_TUCK, LIFT_GRAB=LIFT_GRAB, PUSH_STRIDE=PUSH_STRIDE, PUSH_PLANT=PUSH_PLANT, FPS=FPS, report=report)
json.dump(meta, open(OUT.replace(".glb", ".json"), "w"))
bpy.ops.wm.save_as_mainfile(filepath=OUT.replace(".glb", "_anim.blend"))
# phone-sized textures
for img in bpy.data.images:
    if img.size[0] > 1024: img.scale(1024, 1024)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', export_animation_mode='ACTIONS', export_force_sampling=True,
                          export_frame_step=1, export_image_format='JPEG', export_jpeg_quality=85, export_yup=True)
print("EXPORTED", OUT, "measure", round(ANK,3), round(SOLE,3))
