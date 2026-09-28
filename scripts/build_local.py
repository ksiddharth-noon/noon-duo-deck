"""Builds index.html from project/ — a standalone deck with local screens, refs and fonts.
Run from anywhere: python3 scripts/build_local.py
"""
import sys, re, json, os
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
d = out = root
g = open(f'{d}/scripts/gen_slides.py').read()
B = eval(re.search(r'B = (\{.*?\n\})', g, re.S).group(1))
local = {v: f'screens/{k}.webp' for k, v in B.items()}
refs = {'0a69c7ff68a6c42903ed6bfbb7825ea6':'04-split-view-maps-and-messages','ccee3dee513fe6fba949a0373846083b':'05-notes-overlay-left-controls',
        '1f25f9df42b91814366764a2ad27185d':'08-layout-margin-and-safe-area-inset','b36fec37a86c2ad7fef68df100e7f88f':'09-live-activities-status-bar-app-controls',
        'fbc5b8a875c73ea7bf917d677f3de23f':'14-overlay-arrangement-diagram','706ebcb38635853b8eda27e8e99e4e32':'15-split-view-controls-diagram','4933d8fadc3d335e9d43636a07f01706':'12-share-sheet-folded'}
local.update({k: f'refs/{v}.png' for k, v in refs.items()})
local.update({'977ab621c418bae5eed81026fb0458de':'bezels/outer.webp','6f06750c6a86ab1359dcb905c184116c':'bezels/inner.webp','7a16c39abfc8418ae3908984520b4b49':'bezels/portrait.webp'})
deck = json.load(open(f'{d}/project/deck.json'))
secs = '\n'.join(re.sub(r'/_blob/([0-9a-f]{32})', lambda m: local[m.group(1)], open(f'{d}/project/slides/{s}.html').read().strip()) for s in deck['order'])
fontfile = {'Noontree SemiBold':'Noontree-SemiBold','Noontree Medium':'Noontree-Medium','Geist Pixel Square':'GeistPixel-Square'}
faces = ''.join(f'@font-face{{font-family:"{f}";src:url(fonts/{w}.woff2) format("woff2");font-display:block}}\n' for f, w in fontfile.items())
old = open(f'{out}/index.html').read()
head, rest = old.split('<div id="stage">', 1)
tail = rest[rest.index('<div id="grid">'):]
head = re.sub(r'@font-face[^\n]*\n', '', head)
head = re.sub(r'<link rel="stylesheet"[^>]*>\n', '', head)
head = head.replace('<style>\n', f'<link rel="stylesheet" href="{deck["faces"]["geist"]["href"]}">\n<style>\n' + faces, 1)
head = re.sub(r"html,body\{[^}]*\}", "html,body{height:100%;background:#e9e8e3;overflow:hidden;font-family:'Noontree Medium',Arial,sans-serif}", head)
head = head.replace('#grid{position:fixed;inset:0;background:#111', '#grid{position:fixed;inset:0;background:#e9e8e3')
head = head.replace('.tile:hover{outline-color:#feee00}', '.tile:hover{outline-color:#111}').replace('Noontree,sans-serif', "'Noontree Medium',sans-serif")
open(f'{out}/index.html','w').write(head + '<div id="stage">\n' + secs + '\n</div>\n' + tail)
print(secs.count('<section'), 'slides; unresolved blobs:', secs.count('/_blob/'))
