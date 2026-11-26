"""Cuts a simulator screen recording into a short, light web clip.
Usage: python3 tools/make_clip.py <raw.mov> <name> <start-end> [<start-end> ...]
Keeps only the listed spans (seconds), joins them, scales to 540 wide,
encodes H.264 without audio with a keyframe every second and at every
span start (so tapping a step seeks instantly), and writes site/video/<name>.mp4 plus a poster
image. Prints where each span starts in the finished clip, which the page
uses to light up the matching step. Run from Portfolio/."""
import subprocess, sys, os, json

raw, name, *spans = sys.argv[1:]
spans = [tuple(map(float, s.split('-'))) for s in spans]
os.makedirs('site/video', exist_ok=True)
parts, starts, t = [], [], 0.0
for i, (a, b) in enumerate(spans):
    parts.append(f'[0:v]trim=start={a}:end={b},setpts=PTS-STARTPTS[v{i}]')
    starts.append(round(t, 2)); t += b - a
graph = ';'.join(parts) + ';' + ''.join(f'[v{i}]' for i in range(len(spans))) + f'concat=n={len(spans)}:v=1:a=0,fps=30,scale=540:-2[out]'
out = f'site/video/{name}.mp4'
keys = sorted(set(starts) | {float(k) for k in range(int(t) + 1)})
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-filter_complex', graph, '-map', '[out]',
                '-c:v', 'libx264', '-preset', 'slow', '-crf', '28', '-force_key_frames', ','.join(map(str, keys)), '-sc_threshold', '0', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-an', out], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(min(1.0, t / 4)), '-i', out, '-frames:v', '1', '-q:v', '4', f'site/video/{name}-poster.jpg'], check=True)
# The page uses a WebP poster: about half the size of the JPEG.
from PIL import Image
Image.open(f'site/video/{name}-poster.jpg').convert('RGB').save(f'site/video/{name}-poster.webp', 'WEBP', quality=74, method=6)
print(json.dumps({'file': out, 'seconds': round(t, 2), 'kb': os.path.getsize(out) // 1024, 'span_starts': starts}))
