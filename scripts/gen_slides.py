"""Writes the deck's slides (project/slides/*.html) and index (project/deck.json).

Images and fonts are referenced by their asset ids in the claude.ai Slides artifact (/_blob/<id>);
scripts/build_local.py maps them back to the files in screens/, refs/ and fonts/.
Run from the repo root: python3 scripts/gen_slides.py
"""
import os
os.chdir(os.path.join(os.path.dirname(__file__), ".."))
B = {
 'account-inner-portrait':'78c3a3e7dd910d183415fb6b236f6ef6','account-inner-split':'ce3687a8ca24e3a84694332bc03d67f3','account-inner':'ef7f5643f80957ef7b1fc49e548e2df4','account-outer':'a512a76f2874ed313640e75c6d45154e',
 'address-inner-portrait':'bbfdf81bb9ef5a750f2df4ccfbde425d','address-inner-split':'d071056473f3f5a72a5e306b63040243','address-inner':'a5b3cbf1af3974b6b7291062108a6a0a','address-outer':'a2085a99c1193a6f042707e2d93d30e5','address-outer-before':'5ac182e975abd8c963407caff89e46ba',
 'cart-inner-portrait':'ddf2ee7cd1cd67253ce6b289d89f846e','cart-inner-split':'cd2d966ad96eaae8090174adb92729a2','cart-inner':'6bddb21bb9e61557f0a2624435630691','cart-outer':'7541774f98b83f113baabdbc67f54d07',
 'checkout-inner-portrait':'681ae0cc7026283120218bf9cf54b879','checkout-inner-split':'50d9242b0800b84385439b7f963c04ab','checkout-inner':'af78c9abe2369d968c53b610ea340db2','checkout-outer':'e2e2f11883d57e65adbec07ba08c45e7',
 'home-inner-portrait':'2f8c1b3b905da4dff8ae6d1a7af9aa86','home-inner-split':'42c4e3dea2c10d6f36f9ef6ced00e72e','home-inner':'054310589fa45c52bba7971ef69a6e8d','home-outer':'747a6ede8a44002ef42848ab38fa7c9e',
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
# One typeface: Geist for all text (600 for emphasis, 500 for the rest), Geist Pixel for titles and numbers.
# Geist ships as two bundled static faces, each its own family at its true weight, so nothing is
# synthesised and nothing depends on Google Fonts loading.
SB, MD = "font-family:'Geist SemiBold', Arial, sans-serif; font-weight:400", "font-family:'Geist Medium', Arial, sans-serif; font-weight:400"
PX = "font-family:'Geist Pixel Square', 'Courier New', monospace; font-weight:400"

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
    # Flow chip + counter: one right-aligned row, so the chip hugs its text with fixed padding
    # and always sits 16px from the counter. Arrows get two spaces a side, as in the template.
    chip = chip.replace('  →  ', '&#160; → &#160;')
    return (f'<p style="position:absolute; left:96px; top:72px; width:1100px; {SB}; font-size:18px; letter-spacing:1.44px; text-transform:uppercase; color:#6b6b6b; white-space:nowrap">{eyebrow}</p>'
            f'<h2 style="position:absolute; left:96px; top:108px; width:1240px; {PX}; font-size:{tsize}px; font-weight:400; line-height:1.1; letter-spacing:-1.04px; color:#111111; white-space:nowrap">{title}</h2>'
            f'<div style="position:absolute; left:824px; top:121px; width:1000px; height:44px; display:flex; flex-direction:row; justify-content:end; align-items:center; gap:16px">'
            f'<p style="border:1px solid #d9d9d2; border-radius:100px; padding:9px 20px; {MD}; font-size:18px; line-height:24px; color:#3a3a3a; white-space:nowrap">{chip}</p>'
            f'<p style="{MD}; font-size:18px; line-height:24px; color:#9a9a94; white-space:nowrap">@@N@@ / @@TOTAL@@</p></div>')

def panel(left, width, label, inner, top=205, height=811, direction='row', gap=24):
    return (f'<div style="position:absolute; left:{left}px; top:{top}px; width:{width}px; height:{height}px; background:{PANEL}; border-radius:28px; padding:24px; display:flex; flex-direction:column; gap:16px; overflow:hidden">'
            f'<p style="{SB}; font-size:14px; letter-spacing:1.4px; text-transform:uppercase; color:#8a8a84; white-space:nowrap">{label}</p>'
            f'<div style="flex:1; display:flex; flex-direction:{direction}; justify-content:center; align-items:center; gap:{gap}px">{inner}</div></div>')

def cap(img, text):
    return (f'<div style="display:flex; flex-direction:column; align-items:center; gap:16px">{img}'
            f'<p style="{MD}; font-size:18px; color:#6b6b6b; text-align:center">{text}</p></div>')

def sec(id, body, notes, bg=BG):
    return (f'<section id="{id}" data-transition="fade" style="background:{bg}; {MD}; color:#111111; padding:96px">\n{body}\n<aside>{notes}</aside>\n</section>\n')

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
def add(id, body, notes, **kw): slides[id] = sec(id, body, notes, **kw); order.append(id)
L, W1, W2, X2 = 96, 580, 1108, 96+580+40   # narrow panel, wide panel, wide panel's left

# Section intro, after Apple's "Design principles" title card: black, left-aligned, no header chrome.
add('intro', '<div style="position:absolute; left:96px; top:474px; width:1400px; display:flex; flex-direction:column; gap:18px">'
    f'<p style="{MD}; font-size:60px; line-height:1.25; letter-spacing:-0.6px; color:#86868b">Design principles</p>'
    f'<h2 style="{SB}; font-size:76px; line-height:1.25; letter-spacing:-1.2px; color:#f5f5f7">Adapting noon for iPhone Duo</h2></div>',
    "Opening title. The deck runs in three acts: the context of a foldable phone, the problem Sentinel found in today's app, and the redesign that solves it.", bg='#000000')

add('cover', header(0, 'Solution  ·  noon on iPhone Duo', 'noon, unfolded.', '8 screens  →  4 layouts  →  32 designs', 96)
    + panel(L, 1728, 'Our screens  ·  Home, folded and open', S('home','outer',650,'noon home on the folded cover screen') + S('home','inner',650,'noon home on the open inner screen'), top=254, height=762, gap=40),
    'noon on a foldable: the cover screen when folded, the full inner display when open. Every screen comes from the iPhone Duo Figma file.')

row = ''.join(cap(S('home',k,350,a), c) for k,c,a in [('outer','Folded','Home folded'),('inner','Open','Home open in landscape'),('inner-portrait','Open, portrait','Home open in portrait'),('inner-split','Split view','Home in split view')])
# ── Status quo: the Sentinel audit of today's noon iOS build on iPhone Duo ──────────────────────
# Source: Sentinel responsive build audit, build 2026.1-21692, 2026-09-25, iPhone Duo simulator,
# iOS 27.1 beta. Scores are 1–5 per screen, 5 = no issues; bands follow the report (≥4.5, 3.5–4.5, <3.5).
AUDIT = 'Sentinel audit  ·  build 2026.1-21692  ·  25 Sep 2026'
POSES = ['Closed', 'Open portrait', 'Open landscape', 'Half fold portrait', 'Half fold landscape']
HEAT = [('Homepage', [4.8, 4.7, 4.4, 4.3, 4.6], 4.56), ('Search', [5.0, 4.8, 4.3, 4.8, 4.1], 4.60),
        ('PLP', [4.7, 4.5, 4.1, 4.0, 4.0], 4.26), ('PDP', [4.2, 3.5, 3.3, 3.5, 3.4], 3.58),
        ('Cart', [3.3, 4.3, 2.3, 3.3, 2.3], 3.10), ('Checkout', [4.0, 4.7, 4.4, 4.5, 4.0], 4.32),
        ('Account', [4.0, 3.7, 3.3, 3.7, 3.3], 3.60), ('Order confirmation', [4.5, 4.7, 2.7, 4.2, 3.0], 3.82),
        ('Order listing', [3.8, 4.0, 3.6, 4.0, 3.4], 3.76), ('Order details', [4.0, 4.8, 3.7, 4.7, 3.7], 4.18),
        ('Wishlist', [None, 4.8, 5.0, 4.5, 5.0], 4.83)]
COLMEAN = [4.23, 4.41, 3.74, 4.14, 3.71]
BAND = {'good': ('#d9efe0', '#0f5132'), 'mid': ('#fbeec4', '#6b4e00'), 'low': ('#f8d8d4', '#8a1c14'), 'na': ('#e2e1db', '#55554f')}
def band(v): return 'na' if v is None else 'good' if v >= 4.5 else 'mid' if v >= 3.5 else 'low'
def cell(v, strong=False, digits=1):
    bg, fg = BAND[band(v)]; txt = 'Crash' if v is None else f'{v:.{digits}f}'
    return (f'<p style="background:{bg}; border-radius:8px; padding:9px 0px; {SB if strong else MD}; font-size:18px; line-height:22px; '
            f'color:{fg}; text-align:center; font-variant-numeric:tabular-nums">{txt}</p>')
def lab(t, align='left'): return f'<p style="{SB}; font-size:14px; line-height:18px; letter-spacing:1px; text-transform:uppercase; color:#8a8a84; text-align:{align}">{t}</p>'
grid = ['<div style="width:1060px; display:grid; grid-template-columns:190px repeat(5, 1fr) 112px; gap:6px; align-items:center">', lab('Flow')]
grid += [lab(p, 'center') for p in POSES] + [lab('Row mean', 'center')]
for name, vals, mean in HEAT:
    grid.append(f'<p style="{MD}; font-size:18px; line-height:22px; color:#3a3a3a">{name}</p>')
    grid += [cell(v) for v in vals] + [cell(mean, True, 2)]
grid.append(f'<p style="{SB}; font-size:18px; line-height:22px; color:#111111">Column mean</p>')
grid += [cell(v, True, 2) for v in COLMEAN] + ['<p style="font-size:18px"> </p>', '</div>']
legend = ('<div style="display:flex; flex-direction:row; gap:20px; align-items:center">'
          + ''.join(f'<p style="background:{BAND[k][0]}; border-radius:100px; padding:4px 12px; {MD}; font-size:16px; line-height:20px; color:{BAND[k][1]}">{t}</p>'
                    for k, t in [('good','4.5 and up'),('mid','3.5 to 4.5'),('low','Below 3.5'),('na','Crash, not scored')]) + '</div>')
def stat(big, text):
    return (f'<div style="display:flex; flex-direction:column; gap:6px">'
            f'<p style="{PX}; font-size:64px; line-height:1.05; letter-spacing:-1px; color:#111111">{big}</p>'
            f'<p style="{MD}; font-size:20px; line-height:1.4; color:#6b6b6b">{text}</p></div>')
stats = ('<div style="width:500px; display:flex; flex-direction:column; gap:36px">'
         + stat('4.04 / 5', 'Mean score across the 54 screens that could be scored')
         + stat('19 of 54', 'Screens scoring below 4.0')
         + stat('3.71', 'Half fold landscape, the weakest fold state. Open portrait is the strongest at 4.41')
         + stat('1 crash', 'Folding the device closed on Wishlist crashes the app, in 2 of 2 runs')
         + '</div>')
add('status', header(0, 'Problem  ·  Sentinel audit', "Where noon's iOS app stands today", '11 flows  →  5 fold states  →  55 screens')
    + panel(L, W1, 'Key numbers  ·  build 2026.1-21692, 25 Sep 2026', stats, direction='column')
    + panel(X2, W2, 'Score by flow and fold state  ·  5 = no issues', ''.join(grid) + legend, direction='column', gap=20),
    "Sentinel audited today's noon iOS build, 2026.1-21692, on the iPhone Duo simulator (iOS 27.1 beta) on 25 Sep 2026: "
    "11 flows in 5 fold states. Mean 4.04 out of 5 across 54 scored screens; 19 score below 4.0. Wishlist could not be scored "
    "closed because folding the device crashes the app. Cart is the weakest flow (3.10 mean, 2.3 in both landscape poses), and the "
    "two landscape states are the weakest fold states.")

# Show, don't tell: each finding is the audit's own screenshot, with the problem outlined.
# Box coordinates are in the screenshot's pixels (1000 wide portrait, 1400 wide landscape).
HI = '#ff5b1f'
EV = {  # key: (asset id, width, height)
    'crash':    ('5c4d1c7af2d1e0db1be9e181b76b5d62', 1000, 1374),
    'ol-c':     ('992ee423df9dfe817aa71701a4a08d0f', 1000, 1393),
    'co-hl':    ('c02fff29f372c30099db20ffb4dbef3a', 1400, 1017),
    'plp-op':   ('33e5ec85544b65a204b8dbb276ff9a05', 1000, 1376),
    'ol-ol':    ('a61c605fe5c11abaf978a74cf6143087', 1400, 1017),
    'cart-ol':  ('a75f399840b0903b12b46b20ea63f6e8', 1400, 1017),
}
def evid(key, w, boxes, caption, meta, dashed=False):
    blob, iw, ih = EV[key]; k = w / iw; h = round(ih * k)
    pins = ''.join(f'<div style="position:absolute; left:{round(x0*k)-5}px; top:{round(y0*k)-5}px; width:{round((x1-x0)*k)+10}px; height:{round((y1-y0)*k)+10}px; '
                   f'border:3px {"dashed" if dashed else "solid"} {HI}; border-radius:12px; background:rgba(255,91,31,0.07)"></div>' for x0, y0, x1, y1 in boxes)
    return (f'<div style="width:{w}px; display:flex; flex-direction:column; gap:22px">'
            f'<div style="position:relative; width:{w}px; height:{h}px; flex:none">'
            f'<img src="/_blob/{blob}" alt="{caption}" style="position:absolute; left:0px; top:0px; width:{w}px; height:{h}px; object-fit:contain">{pins}</div>'
            f'<div style="display:flex; flex-direction:column; gap:8px">'
            f'<p style="{SB}; font-size:22px; line-height:1.3; color:#111111">{caption}</p>'
            f'<p style="{MD}; font-size:16px; line-height:1.4; color:#8a8a84">{meta}</p></div></div>')
add('evidence-1', header(0, 'Problem  ·  Top findings, 1 of 2', 'What breaks on the fold today', 'Crash  →  Wrong rail  →  Hinge')
    + panel(96, 440, 'Wishlist  ·  fold closed', evid('crash', 392, [(92, 122, 230, 294)], 'Fold the phone closed on Wishlist and noon quits to the home screen.', 'Crash  ·  reproduced 2 of 2  ·  the only critical finding'))
    + panel(576, 440, 'Order listing  ·  closed', evid('ol-c', 392, [(802, 796, 902, 1346)], 'The landscape tab rail shows on the closed screen, over the cards.', '3.8 / 5  ·  same rail on 6 screens'))
    + panel(1056, 768, 'Checkout  ·  half fold, landscape', evid('co-hl', 720, [(682, 56, 718, 962)], 'The crease runs through the Checkout title, the free-shipping banner and the product name.', '4.0 / 5  ·  content on the hinge on 5 screens')),
    "Straight from the Sentinel audit screenshots. Wishlist: folding closed crashes the app because the list changes from 4 to 2 columns "
    "while mounted; fix by keying the list on its column count. Order listing: the landscape tab rail is drawn in the closed portrait "
    "pose; show it only in landscape. Checkout: content straddles the hinge, and the audit notes the price is cut too; use hinge-aware "
    "layout so titles and prices stay in one pane.")
add('evidence-2', header(0, 'Problem  ·  Top findings, 2 of 2', 'What breaks on the fold today', 'Covered content  →  Empty space  →  Broken layout')
    + panel(96, 360, 'Product listing  ·  open portrait', evid('plp-op', 312, [(356, 1082, 644, 1172)], 'Sort and Filter sit on top of a product’s title and price.', '4.5 / 5  ·  on 4 listing screens'))
    + panel(496, 644, 'Order listing  ·  open landscape', evid('ol-ol', 596, [(560, 386, 1244, 506), (560, 604, 1244, 720)], 'One column stretched across the wide screen leaves most of each card empty.', '3.6 / 5  ·  stretched single columns on 10 screens', dashed=True))
    + panel(1180, 644, 'Cart  ·  open landscape', evid('cart-ol', 596, [(56, 250, 1346, 328)], 'A dark band cuts across the cart and hides the payment summary heading.', '2.3 / 5, tied lowest  ·  the audit asks to confirm the band is app UI, not simulator chrome')),
    "Product listing: the floating Sort and Filter bar covers a card's title and price; dock it where it never overlaps the grid. "
    "Order listing: cards stay one column at full width, leaving the right of every card blank; the open layouts in this deck use two "
    "columns instead. Cart in open landscape scores 2.3, tied for the lowest in the audit; the dark band may be simulator chrome, which "
    "Sentinel asks to confirm. Not pictured: the Search all orders field is 18pt tall, under the 44pt minimum touch target.")

W3 = (1728 - 2*40) // 3   # three equal panels

def title_card(id, eyebrow, title, notes):
    """Black act divider in the style of the opening title card."""
    add(id, '<div style="position:absolute; left:96px; top:474px; width:1600px; display:flex; flex-direction:column; gap:18px">'
        f'<p style="{MD}; font-size:60px; line-height:1.25; letter-spacing:-0.6px; color:#86868b">{eyebrow}</p>'
        f'<h2 style="{SB}; font-size:76px; line-height:1.25; letter-spacing:-1.2px; color:#f5f5f7">{title}</h2></div>', notes, bg='#000000')

# ── Act 1 · Context: one screen of today's app in each fold state the audit tests ────────────────
EV.update({
    'hp-c':  ('a76e8e0e9d9a5b8ccdbf3c0d89484b37', 1000, 1393), 'hp-op': ('0834969f7fbd8e640d9ea0e9eeb458de', 1000, 1376),
    'hp-ol': ('8cd18bee6e0422d6c69b5978a883aedb', 1400, 1017), 'hp-hp': ('9ec634b926245a6c85a7308fb53387de', 1000, 1376),
    'hp-hl': ('2bc20e78958d31b709c784c4dab32605', 1400, 1017), 'od-ol': ('27d668aefa51b17dcebb22f571456954', 1400, 1017),
})
def plain(key, h, alt):
    blob, iw, ih = EV[key]; w = round(iw * h / ih)
    return f'<img src="/_blob/{blob}" alt="{alt}" style="width:{w}px; height:{h}px; object-fit:contain">', w
def posed(key, h, pose, note):
    img, w = plain(key, h, f"Today's noon home screen, {pose.lower()}")
    return (f'<div style="width:{w}px; display:flex; flex-direction:column; gap:18px">{img}'
            f'<div style="display:flex; flex-direction:column; gap:6px"><p style="{SB}; font-size:20px; line-height:1.3; color:#111111">{pose}</p>'
            f'<p style="{MD}; font-size:16px; line-height:1.4; color:#8a8a84">{note}</p></div></div>')
add('context', header(0, 'Context  ·  iPhone Duo', 'One app, five fold states', 'Closed  →  Open  →  Half fold')
    + panel(L, 1728, "Today's noon home  ·  in each fold state the audit tests",
            posed('hp-c', 330, 'Closed', 'The cover screen, phone-sized') + posed('hp-op', 330, 'Open portrait', 'The inner screen, upright')
            + posed('hp-ol', 330, 'Open landscape', 'The inner screen, turned wide') + posed('hp-hp', 330, 'Half fold portrait', 'Half open, hinge across the middle')
            + posed('hp-hl', 330, 'Half fold landscape', 'Stood like a book, hinge down the middle'), gap=12),
    "iPhone Duo folds shut to a phone-sized cover screen and opens to a near-square inner screen, used upright or wide, flat or half "
    "folded. Every screen of an app has to work in all five of these states. These are today's noon home screen in each, from the "
    "Sentinel audit; home is one of the strongest flows, at 4.56 out of 5.")

title_card('act-problem', 'The problem', "Today's app wasn't built for the fold",
           "Act two. Sentinel audited today's noon iOS build in all five fold states. The next three slides are what it found.")
title_card('act-solution', 'The solution', 'Designed for every posture',
           "Act three. The redesign: five layout principles taken from Apple's foldable guidance, the audit's worst screens before and "
           "after, and then all eight screens in every layout.")

# ── Act 3 · Before and after: the audit's screenshot beside the redesigned screen ──────────────
def tag(text, good):
    bg, fg = BAND['good' if good else 'low']
    return (f'<p style="position:absolute; left:12px; top:12px; background:{bg}; border-radius:100px; padding:5px 12px; {SB}; '
            f'font-size:15px; line-height:18px; color:{fg}; white-space:nowrap; box-shadow:0 2px 8px rgba(0,0,0,0.10)">{text}</p>')
def tagged(inner, w, h, text, good):
    return f'<div style="position:relative; width:{w}px; height:{h}px; flex:none">{inner}{tag(text, good)}</div>'
def before(key, h, score, alt):
    img, w = plain(key, h, alt)
    return tagged(img, w, h, f'Before&#160;·&#160;{score} / 5', False), w
def after(sid, kind, h, alt):
    bw, bh = BEZEL[kind][1:3]; w = round(bw * h / bh)
    return tagged(S(sid, kind, h, alt), w, h, 'After&#160;·&#160;redesign', True), w
def caption(text): return f'<p style="{SB}; font-size:21px; line-height:1.35; color:#111111">{text}</p>'
def pair_v(bkey, score, sid, kind, text, alt_b, alt_a, h=305):
    b, _ = before(bkey, h, score, alt_b); a, w = after(sid, kind, h, alt_a)
    return f'<div style="width:{w}px; display:flex; flex-direction:column; gap:18px">{b}{a}{caption(text)}</div>'
def pair_h(bkey, score, sid, kind, text, alt_b, alt_a, h=530):
    b, wb = before(bkey, h, score, alt_b); a, wa = after(sid, kind, h, alt_a)
    return (f'<div style="display:flex; flex-direction:column; gap:22px"><div style="display:flex; flex-direction:row; gap:24px">{b}{a}</div>'
            f'<div style="width:{wb + wa + 24}px">{caption(text)}</div></div>')
add('ba-1', header(0, 'Solution  ·  Before and after, 1 of 2', 'The worst screens, redesigned', 'Audit build  →  Redesign')
    + panel(L, W3, 'Cart  ·  open landscape', pair_v('cart-ol', '2.3', 'cart', 'inner', 'Items on the left; the payment summary stays in view on the right.', 'Cart today, a dark band over the payment summary', 'Redesigned cart, items and payment summary in two columns'))
    + panel(L+W3+40, W3, 'Order details  ·  open landscape', pair_v('od-ol', '3.7', 'tracking', 'inner', 'Tracking and the order summary fill the screen, not one narrow column.', 'Order details today, mostly empty screen', 'Redesigned order tracking across the full screen'))
    + panel(L+2*(W3+40), W3, 'Checkout  ·  landscape', pair_v('co-hl', '4.0', 'checkout', 'inner', 'Two columns split at the hinge, so no line of text crosses the crease.', 'Checkout today, content across the hinge', 'Redesigned checkout in two columns')),
    "Before: the Sentinel audit screenshots of today's build. After: the redesigned screens from the iPhone Duo Figma file. Cart goes "
    "from a broken single column to items beside the payment summary. Order details stops leaving most of the screen empty. Checkout's "
    "two columns meet at the hinge, so text no longer runs across the crease; the before is half folded, the after is the open "
    "landscape layout it folds from.")
add('ba-2', header(0, 'Solution  ·  Before and after, 2 of 2', 'The worst screens, redesigned', 'Audit build  →  Redesign')
    + panel(L, 844, 'Product listing  ·  open portrait', pair_h('plp-op', '4.5', 'search', 'inner-portrait', 'Sort and filters sit in the header row, above the grid, instead of floating over a product.', 'Product listing today, Sort and Filter over a card', 'Redesigned search results, filters in the header'))
    + panel(L+844+40, 844, 'Order listing  ·  closed', pair_h('ol-c', '3.8', 'tracking', 'outer', 'Controls live in the side column, so nothing sits on top of the cards.', 'Order listing today, the landscape rail over the cards', 'Redesigned order tracking cover, controls in the side column')),
    "Product listing: today the Sort and Filter bar floats over a card; in the redesign sort and filters are chips in the header. "
    "Order listing closed: today a landscape tab rail is drawn over the cards; in the redesign the controls sit in the side column and "
    "the content stops short of it.")

# ── Close · next steps ─────────────────────────────────────────────────────────────────────────────
def step(n, title, text):
    return (f'<div style="width:492px; display:flex; flex-direction:column; gap:14px">'
            f'<p style="{PX}; font-size:64px; line-height:1; color:#111111">{n:02d}</p>'
            f'<p style="{SB}; font-size:28px; line-height:1.3; color:#111111">{title}</p>'
            f'<p style="{MD}; font-size:20px; line-height:1.45; color:#6b6b6b">{text}</p></div>')
add('next', header(0, 'Next steps', 'From findings to a fold-ready noon', 'Fix  →  Build  →  Re-audit')
    + panel(L, W3, 'Engineering  ·  blocks release', step(1, 'Fix the Wishlist crash', 'Key the Wishlist list on its column count so folding closed no longer crashes the app. It is the only critical finding.'))
    + panel(L+W3+40, W3, 'Design and engineering', step(2, 'Build the new layouts', 'Side-column controls, two-column open layouts and sheets that keep status at the top, across all eight screens.'))
    + panel(L+2*(W3+40), W3, 'Sentinel', step(3, 'Audit the new build', 'Re-run the audit in the same five fold states and compare with today: 4.04 out of 5, with 19 of 54 screens below 4.0.')),
    "Three steps. The crash is an engineering fix and blocks release on its own. The layouts in this deck then need building. Finally, "
    "re-run Sentinel on the new build in the same five fold states, so the result can be compared directly with today's 4.04.")

add('postures', header(6, 'Principle  ·  Postures', 'Four postures, one app', 'Folded  →  Open  →  Portrait  →  Split')
    + panel(L, 1728, 'Our screens  ·  Home in every layout', row),
    'Each screen ships in four layouts: the folded cover, open in landscape, open in portrait, and split view beside a second app.')

add('edge', header(7, 'Principle  ·  Side controls', 'Controls move to the edge', 'Camera  →  Status bar  →  App controls')
    + panel(L, W1, 'Our screen  ·  Home, folded', S('home','outer',700,'noon home on the cover screen, with status and tab bar in a column on the right edge'))
    + panel(X2, W2, 'Reference  ·  Apple foldable guidance', R('09',657,'Apple Mail: Live Activities, status bar and app controls stacked on the trailing edge') + R('08',657,'Apple Mail: layout margin and horizontal safe area inset'), direction='column', gap=16),
    "Apple's foldable guidance turns the top and bottom bars into one column on the trailing edge: camera, then status, then the app's controls. noon's cover screens follow it; content keeps the full height.")

add('split', header(8, 'Principle  ·  Split view', 'Split view, controls on the outer edge', 'noon  →  Divider  →  Second app')
    + panel(L, W2, 'Our screen  ·  Home in split view', S('home','inner-split',700,'noon home in split view beside a placeholder app'))
    + panel(L+W2+40, W1, 'Reference  ·  Apple foldable guidance', R('15',532,'Diagram: each app keeps its controls on its outer edge') + R('04',532,'Apple Maps and Messages side by side in split view'), direction='column', gap=16),
    'In split view each app keeps its controls on its outer edge, and only the right-hand app carries the status bar. noon is the left app; the right one is a placeholder.')

add('overlay', header(9, 'Principle  ·  Overlay', 'Sheets float over the page', 'Home  →  Address sheet')
    + panel(L, W2, 'Our screen  ·  Address, open', S('address','inner',700,'noon address picker floating as a sheet over home'))
    + panel(L+W2+40, W1, 'Reference  ·  Apple foldable guidance', R('14',532,'Diagram: primary view floating over the secondary view') + R('05',532,'Apple Notes: a primary card over the rest of the screen'), direction='column', gap=16),
    "On the open screen, noon's address picker is a sheet over home rather than a new page, matching Apple's overlay arrangement.")

W3 = (1728 - 2*40) // 3   # three equal panels
add('sheet', header(10, 'Principle  ·  Sheets on the cover', 'Sheets move status to the top', 'Sheet opens  →  Status moves up  →  Close in the sheet')
    + panel(L, W3, 'Before  ·  Status in the side column', S('address','outer-before',640,'Address sheet on the cover screen, time still in the side column under the camera'))
    + panel(L+W3+40, W3, 'After  ·  Status pill at the top', S('address','outer',640,'Address sheet on the cover screen, time and Wi-Fi in a pill beside the camera and a close button in the sheet'))
    + panel(L+2*(W3+40), W3, 'Reference  ·  Apple share sheet', R('12',480,'Apple share sheet on the folded cover screen, with the status pill beside the camera')),
    "When a sheet covers the cover screen, the side column is hidden, so status moves into a glass pill beside the camera and the sheet carries its own close button — Apple's share-sheet pattern, now applied to noon's address picker.")

n = 11
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
SCREEN_SLIDES = [f'{sid}-{ab}' for sid, *_ in SCREENS for ab in 'ab']
order = (['intro', 'context', 'act-problem', 'status', 'evidence-1', 'evidence-2',
          'act-solution', 'cover', 'postures', 'edge', 'split', 'overlay', 'sheet', 'ba-1', 'ba-2']
         + SCREEN_SLIDES + ['next', 'close'])
assert sorted(order) == sorted(slides), set(order) ^ set(slides)
for i, k in enumerate(order, 1):
    open(f'project/slides/{k}.html', 'w').write(slides[k].replace('@@N@@', f'{i:02d}').replace('@@TOTAL@@', str(len(order))))
json.dump({"v":4,"createdOnFiles":{"v":1,"at":"2026-09-27T19:43:48Z"},"title":"noon on iPhone Duo","order":order,
 "sections":{"context":{"description":"A foldable phone, and the five fold states every screen has to handle","start":"intro"},
             "problem":{"description":"What the Sentinel audit found in today's noon iOS build on iPhone Duo","start":"act-problem"},
             "solution":{"description":"The redesign: layout principles, before and after, and every screen in every layout","start":"act-solution"},
             "next":{"description":"What happens next, and all eight screens together","start":"next"}},
 "faces":{"geist-medium":{"family":"Geist Medium","src":"/_blob/1e63a3c1537b28b5ce76a1919b6233d1"},
          "geist-semibold":{"family":"Geist SemiBold","src":"/_blob/e2bff1cac75a16fb23b2560722f0bfe2"},
          "geist-pixel-square":{"family":"Geist Pixel Square","src":"/_blob/8aaabb5db122379a9f093cee0c782cc9"}},
 "designSystems":[]}, open('project/deck.json','w'), indent=1)
print(order)
