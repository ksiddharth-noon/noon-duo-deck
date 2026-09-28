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
local.update({'a76e8e0e9d9a5b8ccdbf3c0d89484b37':'sentinel/homepage-closed.webp','0834969f7fbd8e640d9ea0e9eeb458de':'sentinel/homepage-open-portrait.webp','8cd18bee6e0422d6c69b5978a883aedb':'sentinel/homepage-open-landscape.webp','9ec634b926245a6c85a7308fb53387de':'sentinel/homepage-halffold-portrait.webp','2bc20e78958d31b709c784c4dab32605':'sentinel/homepage-halffold-landscape.webp','27d668aefa51b17dcebb22f571456954':'sentinel/orderdetails-open-landscape.webp'})
local.update({'9826d37a87b31067be73f9beb24156ed':'sentinel/wishlist-fold-closed-crash.webp','992ee423df9dfe817aa71701a4a08d0f':'sentinel/orderlisting-closed.webp','c02fff29f372c30099db20ffb4dbef3a':'sentinel/checkout-halffold-landscape.webp','33e5ec85544b65a204b8dbb276ff9a05':'sentinel/plp-open-portrait.webp','a61c605fe5c11abaf978a74cf6143087':'sentinel/orderlisting-open-landscape.webp','a75f399840b0903b12b46b20ea63f6e8':'sentinel/cart-open-landscape.webp'})
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
