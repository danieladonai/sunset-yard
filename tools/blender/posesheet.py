# Blender -b <char_anim.blend> --python posesheet.py -- <outdir> <yawdeg> [names]
import bpy, sys, math
from mathutils import Vector
OUT, YAW, NAMES = sys.argv[-3], float(sys.argv[-2]), sys.argv[-1]
sc=bpy.context.scene; arm=[o for o in bpy.data.objects if o.type=='ARMATURE'][0]
ad=arm.animation_data
for t in list(ad.nla_tracks): ad.nla_tracks.remove(t)
DECK=0.108
def mat(n,rgb,r=0.6):
    m=bpy.data.materials.new(n); m.use_nodes=True; b=m.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value=(*rgb,1); b.inputs["Roughness"].default_value=r; return m
dm=mat("deck",(0.03,0.025,0.06),0.4); tm=mat("truck",(0.6,0.62,0.66),0.35); wm=mat("wheel",(0.9,0.85,0.75))
board=bpy.data.objects.new("Board",None); sc.collection.objects.link(board)
def box(size,loc,m,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc,rotation=rot); o=bpy.context.object; o.scale=size; o.data.materials.append(m); o.parent=board; return o
box((0.74,0.21,0.012),(0,0,DECK-0.006),dm)
for s in (-1,1):
    box((0.13,0.20,0.012),(s*0.43,0,DECK+0.012),dm,(0,-s*0.33,0)); box((0.06,0.17,0.035),(s*0.31,0,0.065),tm)
    for w in (-1,1):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.027,depth=0.032,location=(s*0.31,w*0.095,0.027),rotation=(math.pi/2,0,0)); o=bpy.context.object; o.data.materials.append(wm); o.parent=board
bpy.ops.mesh.primitive_plane_add(size=30); g=bpy.context.object; g.data.materials.append(mat("g",(0.5,0.47,0.44),0.9))
bpy.ops.object.light_add(type='SUN', rotation=(math.radians(55),0,math.radians(-30))); bpy.context.object.data.energy=3.0
bpy.ops.object.light_add(type='SUN', rotation=(math.radians(70),0,math.radians(150))); bpy.context.object.data.energy=0.7
sc.world=bpy.data.worlds.new("w"); sc.world.use_nodes=True; sc.world.node_tree.nodes["Background"].inputs["Color"].default_value=(0.55,0.58,0.68,1)
r=3.3; a=math.radians(YAW); p=Vector((math.sin(a)*r,-math.cos(a)*r,1.3)); t=Vector((0,0,0.75))
bpy.ops.object.camera_add(location=p); c=bpy.context.object; c.rotation_euler=(t-p).to_track_quat('-Z','Y').to_euler(); c.data.lens=45; sc.camera=c
sc.render.engine='BLENDER_EEVEE'; sc.render.resolution_x=420; sc.render.resolution_y=520; sc.view_settings.view_transform='Standard'
LIFT={"Air_Tuck":0.30,"Air_Flip":0.30,"Grab_Indy":0.47,"Grab_Melon":0.57}
for act in bpy.data.actions:
    if NAMES!="all" and act.name not in NAMES.split(","): continue
    ad.action=act
    if hasattr(ad,"action_slot") and act.slots: ad.action_slot=act.slots[0]
    board.location.z=LIFT.get(act.name,0); board.hide_render = act.name=="Bail"
    for ch in board.children: ch.hide_render = act.name=="Bail"
    fr=[0] if act.frame_range[1]<3 else [0, int(act.frame_range[1]*0.45)]
    for f in fr:
        sc.frame_set(f); sc.render.filepath=f"{OUT}/{act.name}_{f:02d}.png"; bpy.ops.render.render(write_still=True)
