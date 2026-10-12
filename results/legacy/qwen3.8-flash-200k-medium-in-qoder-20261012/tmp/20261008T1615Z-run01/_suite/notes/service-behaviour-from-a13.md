# Service behaviour notes first measured in A13 (reuse these, don't re-probe)

All entries were produced by real requests archived under
`tmp/20261008T1615Z-run01/A13/` (`probes/`, `requests/`, `preview/requests/`) and
`tmp/20261008T1615Z-run01/_suite/requests.jsonl`.

## 1. `borderRadius` must be >= the border width

`Container` with `border="W SOLID #RRGGBB"` and `borderRadius="R"` where `R < W` returns
**HTTP 500 `{"code":"INTERNAL_ERROR","message":"Snapshot rendering failed"}`** — a 114-byte
body with no diagnostic, no position, nothing to grep.

Boundary measured on 10 probes (p01-p10): 1.58<1.7 fail, 1.0<1.7 fail, 1.6<1.7 fail,
1.9<2.0 fail; `R == W` and `R > W` return 200.

**Defence:** clamp at emit time — `radius = max(radius, stroke)` (see
`tmp/20261008T1615Z-run01/A13/plan_a13.py: frame()`). Any generator that computes a radius
from a ratio and a stroke from another ratio can cross this line silently at small canvas
sizes; A13 hit it at 32x32 (stroke 1.7, radius 1.58).

## 2. `Stack.clipBehavior` is not the Flutter enum you expect

`clipBehavior="CLIP"` -> **HTTP 400 PARSE_ERROR**, and the message is helpful:
`Attr [clipBehavior] value is invalid: No enum constant com.muedsa.snapshot.rendering.ClipBehavior.CLIP`.
Docs (`tmp/20261008T1615Z-run01/_suite/docs/clip-rect.html.txt`, fetched as
`shared-cliprect-20261009T011244Z`) also state that a non-`NONE` `clipBehavior` needs a
`decoration` to derive the clip path from.

**Recipe that works for a rectangular crop:**

```
<Positioned left="0" top="0" width="W" height="H">
  <ClipRect><Stack alignment="TOP_LEFT" clipBehavior="NONE"> ... </Stack></ClipRect>
</Positioned>
```

`ClipRect` takes no width/height — it clips to its own layout bounds, which the outer
`Positioned` supplies, and it accepts a single child, hence the inner `Stack`. Coordinates
of children stay in the canvas space of the enclosing `Stack`, so negative offsets simply
get cut. Used in the A13 poster to stop decorative hairlines above the headline.

## 3. Identical DSL bodies are served from cache

Re-posting a byte-identical body returns 200 with
`server-timing: cache;desc=hit, total;dur=1.8` instead of `render;dur=...`. The PNG bytes are
the same. Record this in `iterations.jsonl` when a "re-render" is really a cache hit — it is
not evidence of a new render of changed content, only of the same content.

## 4. `render.py --out` is a file path, not a directory

Passing a directory makes the tool write `<run-root>/<task>.png` and archive the request under
`<run-root>/requests/` instead of `<run-root>/<task>/requests/`. The request itself succeeds,
so the mistake is invisible except in the path. A13's `A13-v03-banner-20261009T010600Z` is
archived in the wrong directory for exactly this reason and is left in place as evidence.
