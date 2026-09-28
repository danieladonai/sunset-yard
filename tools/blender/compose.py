import bpy, sys, os
L, Rr, OUT = sys.argv[-3], sys.argv[-2], sys.argv[-1]
sc = bpy.context.scene; sc.render.resolution_x, sc.render.resolution_y = 1280, 640; sc.render.fps = 30; sc.view_settings.view_transform = 'Standard'
sc.frame_start, sc.frame_end = 1, 96
se = sc.sequence_editor_create()
strips = se.strips if hasattr(se, "strips") else se.sequences
def seq(d, ch, offx, label):
    fs = sorted(f for f in os.listdir(d) if f.endswith('.png'))
    s = strips.new_image(label, os.path.join(d, fs[0]), channel=ch, frame_start=1, fit_method='ORIGINAL')
    for f in fs[1:]: s.elements.append(f)
    s.transform.offset_x = offx
    t = strips.new_effect(label+"_t", 'TEXT', channel=ch+2, frame_start=1, length=96) if 'length' in strips.new_effect.__doc__ else strips.new_effect(label+"_t", 'TEXT', channel=ch+2, frame_start=1, frame_end=97)
    t.text = label; t.font_size = 34; t.location = ((offx+640)/1280 + 0.0, 0.93); t.use_box = True; t.color = (1,1,1,1)
seq(L, 1, -320, "NOW - in game"); seq(Rr, 2, 320, "NEW - Blender, hand-keyed")
sc.render.image_settings.media_type = 'VIDEO'; sc.render.image_settings.file_format = 'FFMPEG'
sc.render.ffmpeg.format = 'MPEG4'; sc.render.ffmpeg.codec = 'H264'; sc.render.ffmpeg.constant_rate_factor = 'HIGH'
sc.render.filepath = OUT; bpy.ops.render.render(animation=True); print("OK")
