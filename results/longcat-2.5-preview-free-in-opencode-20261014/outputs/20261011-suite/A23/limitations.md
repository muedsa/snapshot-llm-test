# A23 Limitations

- SVG: Not natively supported by Snapshot DSL. Use PNG frames instead.
- CMYK: Not supported by Snapshot DSL. Requires external conversion.
- GIF: Not natively supported. Use 6 PNG frames with timing.json.
- Animation: No native animation support. Frames are separate PNGs.
