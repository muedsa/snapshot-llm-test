# B03 probe log — measured Snapshot DSL facts

Every row below is a real HTTP 200 from `https://open-snapshot.muedsa.com/snapshot`
whose PNG was opened with `read_image` and (where numbers are claimed) measured with
`scripts/measure.py` / inline PIL code. Request IDs match `../requests.jsonl`.

| probe | request | question | measured answer |
|---|---|---|---|
| probe-01 | B03-REQ-0001 | does `Transform matrix` rotate, and which way? | yes; `(cos,-sin, sin,cos)` rotates **clockwise** on screen; `backdrop`/`ImageFiltered`/`ClipRRect`/`Container clipBehavior`/`LINEAR,RADIAL,SWEEP` gradients/`Opacity` all render |
| probe-02 | B03-REQ-0002 | where does a rotated box land? | **first evidence that the shared helper is off**: rotated bars did not pass through their anchor |
| probe-03 | B03-REQ-0003 | is the child's top-left or its centre placed at (tx,ty)? | bounding boxes showed a consistent +w/2,+h/2 displacement |
| probe-04 | B03-REQ-0004 | hand-written matrices, no helper maths | **RULE PROVEN.** `m=R0 t=(400,200)` on a 200x14 box gives bbox x 400..599, y 200..213; `m=R90 t=(100,320)` gives x 100..113, y 120..319; `m=R180 t=(800,200)` gives x 600..799; `m=scale(3,2) t=(700,560)` on a 40x20 child gives x 700..819, y 560..599. So the child's **top-left corner** is mapped to `(tx,ty)` and the linear part is applied about that same point — there is **no** `w/2,h/2` pre-translate. Centre therefore lands on `Cx = tx + cos*w/2 - sin*h/2`, `Cy = ty + sin*w/2 + cos*h/2`. |
| probe-05/06/07 | B03-REQ-0005..0007 | independent confirmation | consistent; residual mismatches were traced to my own magenta/pink markers polluting the colour masks, not to the service |
| probe-08 | B03-REQ-0008/0009 | automated placement audit over 9 angles | after fixing masks: **all placements within 0.6px** of the predicted footprint (`sk.rect_at` now uses `tx = cx - c*w/2 + s*h/2`) |
| probe-09 | B03-REQ-0010/0011 | wrapping + line height | a `Text` in a 180px Container wraps; line box = 1.30em |
| probe-10 | B03-REQ-0012 | ink width of real strings | CJK 0.99em, mono 0.49em, proportional latin varies 0.18–0.98em |
| probe-11 | B03-REQ-0013..0017 | per-character advances | 107 glyphs measured -> `probe/char-advances.json`. **Also found the service limit**: height 6144 -> `400 RENDER_ERROR "Render height 6144 exceeds maximum 4096"` |
| probe-12 | B03-REQ-0018 | does the width model over-predict on real sentences? | yes, 1.002–1.033x — safe direction, no wrap |
| probe-13 | B03-REQ-0019/0020 | sentinel-based advance | mask design was wrong twice; kept as a documented failed approach |
| probe-14 | B03-REQ-0021..0027 | final per-glyph + per-string table | `probe/advances.json`; confirmed CJK ink 0.94em, mono ink 0.49em |

## Rules adopted for every B03 work

1. `Transform matrix` = column-major, `(m00,m01,0,0, m10,m11,0,0, 0,0,1,0, tx,ty,0,1)`;
   `m00=cos, m01=-sin, m10=sin, m11=cos`; the child's top-left lands exactly on `(tx,ty)`.
   Positive angle = clockwise.
2. Width model: CJK 1.00em, mono 0.60em, measured per-char table for latin, fallback
   0.60em. Always over-predicts on purpose.
3. Draw order = layer order: background -> geometry -> text.
4. `borderRadius` takes one number; four different corners need the four named attrs.
5. `padding`/`margin` use tuple syntax `"(v,h)"` or `"(l,t,r,b)"`.
6. Max render height 4096 px; tall sheets must be split into more requests.
7. `BackdropFilter` blurs everything composited so far — only sigma <= 1 is safe with
   live text on the same sheet.
8. `Column`/`Row` never contain `Positioned`; absolute layout uses one flat `Stack`.
