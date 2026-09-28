# Concatenate PNG sequences into one mp4: Blender -b --python seq2mp4.py -- <out.mp4> <dir1[:from:to]> <dir2...>
import bpy, sys, os
args = sys.argv[sys.argv.index("--")+1:]
OUT, DIRS = args[0], args[1:]
sc = bpy.context.scene; sc.render.fps = 30; sc.view_settings.view_transform = 'Standard'
se = sc.sequence_editor_create(); strips = se.strips if hasattr(se, "strips") else se.sequences
start = 1; W = H = None
for i, spec in enumerate(DIRS):
    d, *rng = spec.split(":")
    fs = sorted(f for f in os.listdir(d) if f.endswith(".png"))
    if rng: fs = fs[int(rng[0]):int(rng[1])]
    s = strips.new_image("s%d" % i, os.path.join(d, fs[0]), channel=1, frame_start=start, fit_method='FIT')
    for f in fs[1:]: s.elements.append(f)
    if W is None:
        img = bpy.data.images.load(os.path.join(d, fs[0])); W, H = img.size
    start += len(fs)
sc.frame_start, sc.frame_end = 1, start - 1
sc.render.resolution_x, sc.render.resolution_y = W, H
sc.render.image_settings.media_type = 'VIDEO'; sc.render.image_settings.file_format = 'FFMPEG'
sc.render.ffmpeg.format = 'MPEG4'; sc.render.ffmpeg.codec = 'H264'; sc.render.ffmpeg.constant_rate_factor = 'HIGH'
sc.render.filepath = OUT; bpy.ops.render.render(animation=True); print("OK", OUT, start - 1)
