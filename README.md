# noon on iPhone Duo — deck

A 23-slide deck of noon's eight foldable screens (Home, Search, Product, Cart, Checkout, Address,
Order tracking, Account), each in four layouts: folded cover, open landscape, open portrait and
split view. Styled after the *Design X Engineering* slide template in Figma
(`LnvGQLmFhfU4tfm8WamCZe`, node `21:3`), set in Noontree with Geist Pixel titles.

Live: **https://noon-duo-deck.vercel.app**

## Viewing

`index.html` is self-contained; serve the folder with any static server and open it.

```sh
python3 -m http.server 3014
```

← → or click to move · **G** grid of all slides · **F** fullscreen · `#n` in the URL opens slide *n*.

## Editing

The slides are generated, not hand-written:

1. `scripts/gen_slides.py` writes `project/slides/*.html` and `project/deck.json` — copy, layout
   and slide order live here.
2. `scripts/build_local.py` turns `project/` into `index.html`, swapping asset ids for the local
   files in `screens/`, `refs/` and `fonts/`.

```sh
python3 scripts/gen_slides.py && python3 scripts/build_local.py
```

`project/` is also the source for the claude.ai Slides version of the deck, which is why images are
referenced by asset id there.

## Deploying

```sh
vercel deploy --prod --yes
```

Hand out `noon-duo-deck.vercel.app`; the scope-suffixed URLs the CLI prints sit behind Vercel's login.

## Sources and rights

- `screens/` — noon designs exported from the *iPhone Duo* Figma file (`fnAUgyDjXX9sPmi9SPnI7h`),
  via the [duo-fold-preview](https://github.com/ksiddharth-noon/duo-fold-preview) repo.
- `refs/` — frames from Apple's foldable design guidance, cropped for reference. Apple's material;
  internal reference only.
- `fonts/` — Noontree (noon's typeface) and Geist Pixel.

Keep this repository private.
