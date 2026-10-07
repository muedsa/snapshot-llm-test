# Pure Snapshot DSL helpers

`dsl.cjs` constructs strings and performs no rendering, HTTP requests, filesystem writes, or suite-state edits. It uses only Snapshot parser tags and attributes documented in the shared cache. No SVG, canvas, raster helper asset, or drawing library is involved.

```js
const {Canvas} = require('../_suite/dsl.cjs');
const c = new Canvas(1280, 720, {background:'#F5F7FC'});
c.card(48, 48, 600, 220, '#FFFFFF', {radius:20, border:'1 SOLID #DCE3EB'});
c.text(72, 70, 552, 64, 'Snapshot / 中文 & <special>', 34, '#172033', {bold:true});
c.text(72, 145, 552, 80, 'Exact whitespace\n  is preserved.', 22, '#526174');
c.line(48, 340, 630, 420, '#326CE5', 4);
c.circle(48, 340, 8, '#326CE5');
c.arrow(700, 300, 1100, 470, '#326CE5', 4, {headLength:22, headWidth:10});
const fullDsl = c.toString(); // Save this string as a .snapshot and send to the real service.
```

- `new Canvas(w,h,{background,font,type,clipBehavior,debug})`: exact outer `Container` width and height, with an expanding `Stack`. Default font is the actually available `Inter,Noto Sans CJK SC`; type is PNG; background is white.
- `rect(x,y,w,h,color,options)`, `card(...)`: use positioned `Container`. `radius` maps to `borderRadius`, `shadow` maps to `boxShadow`; documented decoration attributes pass through. Card defaults to radius 16. `child` can contain one complete DSL widget. `opacity` wraps the widget in documented `Opacity`.
- `circle(cx,cy,r,color,options)`: a square `Container` with documented `shape="CIRCLE"`. `oval(x,y,w,h,color,{opacity})` uses `ClipOval` around a filled container.
- `text(x,y,w,h,text,size=20,color,options)`: positioned `Text` containing `Raw` and CDATA. Newlines, leading/trailing spaces, `<`, `>`, `&`, quotes, and CDATA terminators are preserved literally. `bold`, `italic`, `font`, `align`, `lineHeight` map to actual documented attributes; documented Text attributes pass through. Alignment values include START, END, LEFT, RIGHT, CENTER, JUSTIFY. Font comma lists have no extra leading space.
- `line(x1,y1,x2,y2,color,width,{roundCaps,opacity})`: actual straight rotated filled rectangle, rotated with the documented 16-number column-major `Transform.matrix`. Origin is `(0,0)`; a half-thickness translation puts its centreline exactly on the specified endpoints. Painted bounds may be larger than its unrotated layout bounds. Default is butt caps; optional round caps add real DSL circles. Zero-length butt lines add nothing.
- `polyline(points,color,width,{closed,...})`: repeated straight DSL segments. `arrow(...)` uses three straight segments, optionally `double`; `headLength` is longitudinal length, `headWidth` is the half-width at its rear.
- `table(x,y,columnWidths,rowHeights,rows,options)`: actual positioned cells and Text widgets. `rowHeights` is one number or per-row numbers; `rows` is a 2D array. Row 0 defaults to a header. Options include padding, size, fill, alternateFill, headerFill, color, headerColor, borderColor, borderWidth, aligns, textOptions, header.
- `add(widget)` adds a direct Stack child, `at(x,y,w,h,widget)` wraps a Positioned child. `toString()` returns a full `<Snapshot>` tree.
- Exports also include `tag`, `attrs`, `cdata`, `matrix2d`, `position`, and `DEFAULT_FONT` for additional documented DSL construction.

The outer Stack deliberately keeps its documented default clipping behavior `HARD_EDGE`. Shapes, diagonal lines, transform paint, shadows, or text outside the canvas can be clipped. Explicitly pass `clipBehavior:'NONE'` only when overflow is intentional; the final image still has the chosen canvas extent. Text height is a layout box rather than a promise that all text fits: inspect actual service images and adjust font size, width, position or content as needed. No automatic measurement or font-fit claims are made. Attribute serialization uses literal quotes because entities are not decoded by this parser; an attribute containing both quote delimiters is rejected rather than silently corrupted. Put general user content in text/CDATA.

Sources read for this implementation: `shared-doc-000001-response.txt` (real service guide), `shared-doc-000004-readable.txt` (actual registered parser tag/attribute reference), `shared-doc-000006-readable.txt` (OpenAPI), `shared-fonts-000001-response.txt` (actual service font list). These are reused shared documents; this helper did not create any new HTTP request. Real rendering and visual verification remain the responsibility of each task. This helper does not claim service validation.
