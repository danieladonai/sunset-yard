# Blender -b <char.blend> --python lookdev.py -- <out.png> [yawdeg]
import bpy, sys, math
from mathutils import Vector
OUT=sys.argv[-2]; YAW=float(sys.argv[-1])
sc=bpy.context.scene
bpy.ops.mesh.primitive_plane_add(size=20); g=bpy.context.object
gm=bpy.data.materials.new("g"); gm.use_nodes=True; gm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=(0.5,0.47,0.44,1); g.data.materials.append(gm)
bpy.ops.object.light_add(type='SUN', rotation=(math.radians(55),0,math.radians(-30))); bpy.context.object.data.energy=3.2
bpy.ops.object.light_add(type='SUN', rotation=(math.radians(70),0,math.radians(150))); bpy.context.object.data.energy=0.8
sc.world=bpy.data.worlds.new("w"); sc.world.use_nodes=True; sc.world.node_tree.nodes["Background"].inputs["Color"].default_value=(0.55,0.58,0.68,1)
r=3.6; a=math.radians(YAW); p=Vector((math.sin(a)*r,-math.cos(a)*r,1.1)); t=Vector((0,0,0.95))
bpy.ops.object.camera_add(location=p); c=bpy.context.object; c.rotation_euler=(t-p).to_track_quat('-Z','Y').to_euler(); c.data.lens=50; sc.camera=c
sc.render.engine='BLENDER_EEVEE'; sc.render.resolution_x=560; sc.render.resolution_y=700; sc.view_settings.view_transform='Standard'
sc.render.filepath=OUT; bpy.ops.render.render(write_still=True)
