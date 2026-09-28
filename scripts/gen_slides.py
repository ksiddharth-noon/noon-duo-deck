"""Writes the deck's slides (project/slides/*.html) and index (project/deck.json).

Images and fonts are referenced by their asset ids in the claude.ai Slides artifact (/_blob/<id>);
scripts/build_local.py maps them back to the files in screens/, refs/ and fonts/.
Run from the repo root: python3 scripts/gen_slides.py
"""
import os
os.chdir(os.path.join(os.path.dirname(__file__), ".."))
B = {
 'account-inner-portrait':'78c3a3e7dd910d183415fb6b236f6ef6','account-inner-split':'815829d899b4adc3be60897576d17ab0','account-inner':'ef7f5643f80957ef7b1fc49e548e2df4','account-outer':'a512a76f2874ed313640e75c6d45154e',
 'address-inner-portrait':'bbfdf81bb9ef5a750f2df4ccfbde425d','address-inner-split':'26635eb0c04da69c94d503df19d1a371','address-inner':'a5b3cbf1af3974b6b7291062108a6a0a','address-outer':'a2085a99c1193a6f042707e2d93d30e5','address-outer-before':'5ac182e975abd8c963407caff89e46ba',
 'cart-inner-portrait':'ddf2ee7cd1cd67253ce6b289d89f846e','cart-inner-split':'159807b146adf368cdcfb87b860b5dd5','cart-inner':'6bddb21bb9e61557f0a2624435630691','cart-outer':'7541774f98b83f113baabdbc67f54d07',
 'checkout-inner-portrait':'681ae0cc7026283120218bf9cf54b879','checkout-inner-split':'50d9242b0800b84385439b7f963c04ab','checkout-inner':'af78c9abe2369d968c53b610ea340db2','checkout-outer':'e2e2f11883d57e65adbec07ba08c45e7',
 'home-inner-portrait':'2f8c1b3b905da4dff8ae6d1a7af9aa86','home-inner-split':'e1444dd83d71385aad44fea9621e7031','home-inner':'054310589fa45c52bba7971ef69a6e8d','home-outer':'747a6ede8a44002ef42848ab38fa7c9e',
 'product-inner-portrait':'193f9f1b120c1fefcfbcb9ba6ecebff9','product-inner-split':'b29cc7144afb8e98aa60e0fa3233ab8b','product-inner':'45cac00e50dfdc064ec09132860384ea','product-outer':'8d70c4b0af2506b7cf61fd9121733fd3',
 'search-inner-portrait':'f4e90147b8bfd13bb4f486fcc4f73265','search-inner-split':'04b66caa0f11041ed69ac01d69cf4e46','search-inner':'8200972d1b9e1c4b13048021c1f79be3','search-outer':'d146b441b98ac7e81f9392e70b29bafc',
 'tracking-inner-portrait':'aa0a49a22e6b8451f3fcffdc2ee5394c','tracking-inner-split':'576b3f04890ed01e1b8e0d699774b0bd','tracking-inner':'1f6b4a3d832ef3050e99603ecf4df460','tracking-outer':'c50db9261ca61f831722d2a9660bdbfc',
}
import json
B.update({'ref-04':'0a69c7ff68a6c42903ed6bfbb7825ea6','ref-05':'ccee3dee513fe6fba949a0373846083b','ref-08':'1f25f9df42b91814366764a2ad27185d',
          'ref-09':'b36fec37a86c2ad7fef68df100e7f88f','ref-14':'fbc5b8a875c73ea7bf917d677f3de23f','ref-15':'706ebcb38635853b8eda27e8e99e4e32','ref-12':'4933d8fadc3d335e9d43636a07f01706'})
AR = {'outer':585/851,'inner':2160/1518,'inner-portrait':1518/2160,'inner-split':2160/1518,
      'ref-04':1654/879,'ref-05':1654/879,'ref-08':1654/879,'ref-09':1654/879,'ref-14':841/483,'ref-15':853/452,'ref-12':604/791,'outer-before':585/851}
BG, PANEL = '#fafaf7', '#f1f1ec'
SB, MD = "font-family:'Noontree SemiBold', Arial, sans-serif", "font-family:'Noontree Medium', Arial, sans-serif"
PX, GE = "font-family:'Geist Pixel Square', 'Courier New', monospace", "font-family:'Geist', Arial, sans-serif"
TOTAL = 23

def shot(key, h, alt, w=None):
    src = B[key]; w = w or round(h*AR[key.split('-',1)[1] if not key.startswith('ref') else key])
    return f'<img src="/_blob/{src}" alt="{alt}" style="width:{w}px; height:{h}px; object-fit:cover; border-radius:22px; box-shadow:0 8px 24px rgba(0,0,0,0.08)">'
# The real iPhone Duo "Star White" device frames from the Figma file, screen area transparent.
# (frame w, h) · (screen x, y, w, h) inside it · the screen opening's corner radii TL TR BR BL,
# measured from the frame's alpha — all in Figma points. The cover's hinge side is nearly square.
BEZEL = {
    'outer':          ('977ab621c418bae5eed81026fb0458de', 524, 730, 29, 26, 466, 678, (11, 60, 60, 11)),
    'outer-before':   ('977ab621c418bae5eed81026fb0458de', 524, 730, 29, 26, 466, 678, (11, 60, 60, 11)),
    'inner':          ('6f06750c6a86ab1359dcb905c184116c', 963, 700, 36, 37, 890, 626, (53, 52, 52, 53)),
    'inner-split':    ('6f06750c6a86ab1359dcb905c184116c', 963, 700, 36, 37, 890, 626, (53, 52, 52, 53)),
    'inner-portrait': ('7a16c39abfc8418ae3908984520b4b49', 700, 963, 37, 36, 626, 890, (53, 53, 52, 52)),
}
def S(sid, kind, h, alt):
    """A screen inside its device frame; h is the height of the whole device."""
    bez, bw, bh, ox, oy, fw, fh, radii = BEZEL[kind]; k = h / bh
    px = lambda v: f'{round(v*k)}px'
    rad = ' '.join(px(r) for r in radii)
    return (f'<div style="position:relative; width:{px(bw)}; height:{h}px; flex:none">'
            f'<img src="/_blob/{B[sid+"-"+kind]}" alt="{alt}" style="position:absolute; left:{px(ox)}; top:{px(oy)}; width:{px(fw)}; height:{px(fh)}; object-fit:cover; border-radius:{rad}">'
            f'<img src="/_blob/{bez}" alt="" style="position:absolute; left:0px; top:0px; width:{px(bw)}; height:{h}px; object-fit:contain"></div>')

def R(n, w, alt): return shot(f'ref-{n}', round(w/AR[f"ref-{n}"]), alt, w)

def header(n, eyebrow, title, chip, tsize=52):
    cw = round(len(chip)*8.2) + 44
    return (f'<p style="position:absolute; left:96px; top:72px; width:1100px; {SB}; font-size:18px; font-weight:400; letter-spacing:1.44px; text-transform:uppercase; color:#6b6b6b; white-space:nowrap">{eyebrow}</p>'
            f'<h2 style="position:absolute; left:96px; top:108px; width:1240px; {PX}; font-size:{tsize}px; font-weight:400; line-height:1.1; letter-spacing:-1.04px; color:#111111; white-space:nowrap">{title}</h2>'
            f'<p style="position:absolute; left:{1757-cw}px; top:121px; width:{cw}px; height:44px; border:1px solid #d9d9d2; border-radius:100px; padding:10px 20px; {GE}; font-size:18px; font-weight:500; line-height:1.3; color:#3a3a3a; white-space:nowrap">{chip}</p>'
            f'<p style="position:absolute; left:1764px; top:132px; width:60px; {MD}; font-size:18px; color:#9a9a94; text-align:right; white-space:nowrap">{n:02d} / {TOTAL}</p>')

def panel(left, width, label, inner, top=205, height=811, direction='row', gap=24):
    return (f'<div style="position:absolute; left:{left}px; top:{top}px; width:{width}px; height:{height}px; background:{PANEL}; border-radius:28px; padding:24px; display:flex; flex-direction:column; gap:16px; overflow:hidden">'
            f'<p style="{SB}; font-size:14px; letter-spacing:1.4px; text-transform:uppercase; color:#8a8a84; white-space:nowrap">{label}</p>'
            f'<div style="flex:1; display:flex; flex-direction:{direction}; justify-content:center; align-items:center; gap:{gap}px">{inner}</div></div>')

def cap(img, text):
    return (f'<div style="display:flex; flex-direction:column; align-items:center; gap:16px">{img}'
            f'<p style="{MD}; font-size:18px; color:#6b6b6b; text-align:center">{text}</p></div>')

def sec(id, body, notes):
    return (f'<section id="{id}" data-transition="fade" style="background:{BG}; {MD}; color:#111111; padding:96px">\n{body}\n<aside>{notes}</aside>\n</section>\n')

SCREENS = [
 ('home','Home',"Folded, it's the noon you know. Open, offers and categories fill the display."),
 ('search','Search','Two results to a row when folded. Four when open.'),
 ('product','Product','Open, the gallery and buy box sit together, so price and delivery never scroll away.'),
 ('cart','Cart','Items on the left. Coupons and the payment summary stay in view on the right.'),
 ('checkout','Checkout','Delivery, receiver and payment in two columns, with Place Order always in reach.'),
 ('address','Address','The address picker floats over home as a sheet instead of a new screen.'),
 ('tracking','Order tracking','The delivery timeline sits beside the order summary.'),
 ('account','Account','The account menu on the left, your orders on the right.'),
]
slides, order = {}, []
def add(id, body, notes): slides[id] = sec(id, body, notes); order.append(id)
L, W1, W2, X2 = 96, 580, 1108, 96+580+40   # narrow panel, wide panel, wide panel's left

add('cover', header(1, 'noon  ·  iPhone Duo', 'noon, unfolded.', '8 screens  →  4 layouts  →  32 designs', 96)
    + panel(L, 1728, 'Our screens  ·  Home, folded and open', S('home','outer',650,'noon home on the folded cover screen') + S('home','inner',650,'noon home on the open inner screen'), top=254, height=762, gap=40),
    'noon on a foldable: the cover screen when folded, the full inner display when open. Every screen comes from the iPhone Duo Figma file.')

row = ''.join(cap(S('home',k,350,a), c) for k,c,a in [('outer','Folded','Home folded'),('inner','Open','Home open in landscape'),('inner-portrait','Open, portrait','Home open in portrait'),('inner-split','Split view','Home in split view')])
add('postures', header(2, 'Principle  ·  Postures', 'Four postures, one app', 'Folded  →  Open  →  Portrait  →  Split')
    + panel(L, 1728, 'Our screens  ·  Home in every layout', row),
    'Each screen ships in four layouts: the folded cover, open in landscape, open in portrait, and split view beside a second app.')

add('edge', header(3, 'Principle  ·  Side controls', 'Controls move to the edge', 'Camera  →  Status bar  →  App controls')
    + panel(L, W1, 'Our screen  ·  Home, folded', S('home','outer',700,'noon home on the cover screen, with status and tab bar in a column on the right edge'))
    + panel(X2, W2, 'Reference  ·  Apple foldable guidance', R('09',657,'Apple Mail: Live Activities, status bar and app controls stacked on the trailing edge') + R('08',657,'Apple Mail: layout margin and horizontal safe area inset'), direction='column', gap=16),
    "Apple's foldable guidance turns the top and bottom bars into one column on the trailing edge: camera, then status, then the app's controls. noon's cover screens follow it; content keeps the full height.")

add('split', header(4, 'Principle  ·  Split view', 'Split view, controls on the outer edge', 'noon  →  Divider  →  Second app')
    + panel(L, W2, 'Our screen  ·  Home in split view', S('home','inner-split',700,'noon home in split view beside a placeholder app'))
    + panel(L+W2+40, W1, 'Reference  ·  Apple foldable guidance', R('15',532,'Diagram: each app keeps its controls on its outer edge') + R('04',532,'Apple Maps and Messages side by side in split view'), direction='column', gap=16),
    'In split view each app keeps its controls on its outer edge, and only the right-hand app carries the status bar. noon is the left app; the right one is a placeholder.')

add('overlay', header(5, 'Principle  ·  Overlay', 'Sheets float over the page', 'Home  →  Address sheet')
    + panel(L, W2, 'Our screen  ·  Address, open', S('address','inner',700,'noon address picker floating as a sheet over home'))
    + panel(L+W2+40, W1, 'Reference  ·  Apple foldable guidance', R('14',532,'Diagram: primary view floating over the secondary view') + R('05',532,'Apple Notes: a primary card over the rest of the screen'), direction='column', gap=16),
    "On the open screen, noon's address picker is a sheet over home rather than a new page, matching Apple's overlay arrangement.")

W3 = (1728 - 2*40) // 3   # three equal panels
add('sheet', header(6, 'Principle  ·  Sheets on the cover', 'Sheets move status to the top', 'Sheet opens  →  Status moves up  →  Close in the sheet')
    + panel(L, W3, 'Before  ·  Status in the side column', S('address','outer-before',640,'Address sheet on the cover screen, time still in the side column under the camera'))
    + panel(L+W3+40, W3, 'After  ·  Status pill at the top', S('address','outer',640,'Address sheet on the cover screen, time and Wi-Fi in a pill beside the camera and a close button in the sheet'))
    + panel(L+2*(W3+40), W3, 'Reference  ·  Apple share sheet', R('12',480,'Apple share sheet on the folded cover screen, with the status pill beside the camera')),
    "When a sheet covers the cover screen, the side column is hidden, so status moves into a glass pill beside the camera and the sheet carries its own close button — Apple's share-sheet pattern, now applied to noon's address picker.")

n = 7
for i, (sid, name, sub) in enumerate(SCREENS, 1):
    add(f'{sid}-a', header(n, f'{i:02d}  ·  {name}', f'{name}, folded and open', 'Cover screen  →  Inner screen')
        + panel(L, W1, 'Folded  ·  Cover screen', S(sid,'outer',700,f'{name}, folded'))
        + panel(X2, W2, 'Open  ·  Inner screen', S(sid,'inner',700,f'{name}, open in landscape')),
        f'{name}. {sub}'); n += 1
    add(f'{sid}-b', header(n, f'{i:02d}  ·  {name}', f'{name}, portrait and split view', 'Portrait  →  Split view')
        + panel(L, W1, 'Open  ·  Portrait', S(sid,'inner-portrait',700,f'{name}, open in portrait'))
        + panel(X2, W2, 'Split view  ·  Beside a second app', S(sid,'inner-split',700,f'{name} in split view beside a placeholder app')),
        f'{name} turned upright, and in split view with noon on the left and a second app on the right.'); n += 1

row = ''.join(cap(S(sid,'outer',273,f'{name}, folded'), name) for sid, name, _ in SCREENS)
add('close', header(n, 'Summary', 'Eight screens, every posture', '8 screens  →  4 layouts  →  32 designs')
    + panel(L, 1728, 'Our screens  ·  Every cover screen', row, gap=16),
    'All eight cover screens together. Each also has open landscape, portrait and split-view layouts.')
assert len(order) == TOTAL, len(order)

for k, v in slides.items(): open(f'project/slides/{k}.html','w').write(v)
json.dump({"v":4,"createdOnFiles":{"v":1,"at":"2026-09-27T19:43:48Z"},"title":"noon on iPhone Duo","order":order,
 "sections":{"intro":{"description":"noon on a foldable, and the layout principles it follows","start":"cover"},
             "screens":{"description":"Each of the eight screens in all four layouts","start":"home-a"},
             "close":{"description":"All eight screens together","start":"close"}},
 "faces":{"noontree-semibold":{"family":"Noontree SemiBold","src":"/_blob/a38b57215c536fa0e03d07a5daec7ee3"},
          "noontree-medium":{"family":"Noontree Medium","src":"/_blob/a25edd3639fbce9f53f835ce69a85ff3"},
          "geist-pixel-square":{"family":"Geist Pixel Square","src":"/_blob/8aaabb5db122379a9f093cee0c782cc9"},
          "geist":{"family":"Geist","href":"https://fonts.googleapis.com/css2?family=Geist:wght@500&display=swap"}},
 "designSystems":[]}, open('project/deck.json','w'), indent=1)
print(order)
