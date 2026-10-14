from pathlib import Path

# Brand colors
PRIMARY = "#3B82F6"
SECONDARY = "#10B981"
ACCENT = "#F59E0B"
DARK = "#1E293B"

# Icon geometry (centered at 256,256 in 512x512)
# Layered rectangles concept - "information overlay"
def gen_icon(color_mode="color"):
    c1 = PRIMARY if color_mode == "color" else "#000000"
    c2 = SECONDARY if color_mode == "color" else "#000000"
    c3 = ACCENT if color_mode == "color" else "#000000"
    
    dsl = f'''<Snapshot type="png" width="512" height="512" background="transparent">
  <Column mainAxisSize="MAX" height="512" width="512">
    <Container width="512" height="512">
      <Stack>
        <Positioned left="156" top="156" width="200" height="200">
          <Container color="{c1}" borderRadius="16"/>
        </Positioned>
        <Positioned left="196" top="196" width="200" height="200">
          <Container color="{c2}" borderRadius="16"/>
        </Positioned>
        <Positioned left="236" top="236" width="200" height="200">
          <Container color="{c3}" borderRadius="16"/>
        </Positioned>
      </Stack>
    </Container>
  </Column>
</Snapshot>'''
    return dsl

# Banner
def gen_banner():
    dsl = f'''<Snapshot type="png" width="1200" height="400" background="{DARK}">
  <Column mainAxisSize="MAX" height="400" width="1200">
    <Container height="400" width="1200">
      <Row mainAxisAlignment="SPACE_BETWEEN" crossAxisAlignment="CENTER">
        <Container width="200" height="200">
          <Stack>
            <Positioned left="50" top="50" width="100" height="100">
              <Container color="{PRIMARY}" borderRadius="8"/>
            </Positioned>
            <Positioned left="70" top="70" width="100" height="100">
              <Container color="{SECONDARY}" borderRadius="8"/>
            </Positioned>
            <Positioned left="90" top="90" width="100" height="100">
              <Container color="{ACCENT}" borderRadius="8"/>
            </Positioned>
          </Stack>
        </Container>
        <Column crossAxisAlignment="START">
          <Text text="叠光 Layerlight" color="#FFFFFF" fontSize="48" fontStyle="BOLD"/>
          <Text text="把复杂信息，组织成清晰画面" color="#CBD5E1" fontSize="24"/>
        </Column>
      </Row>
    </Container>
  </Column>
</Snapshot>'''
    return dsl

# Poster
def gen_poster():
    dsl = f'''<Snapshot type="png" width="1080" height="1350" background="{DARK}">
  <Column mainAxisSize="MAX" height="1350" width="1080">
    <Container height="200" width="1080" padding="(40,40)">
      <Text text="叠光 Layerlight" color="#FFFFFF" fontSize="64" fontStyle="BOLD"/>
      <Text text="把复杂信息，组织成清晰画面" color="#CBD5E1" fontSize="32"/>
    </Container>
    <Container height="400" width="1080">
      <Stack>
        <Positioned left="340" top="100" width="200" height="200">
          <Container color="{PRIMARY}" borderRadius="16"/>
        </Positioned>
        <Positioned left="390" top="150" width="200" height="200">
          <Container color="{SECONDARY}" borderRadius="16"/>
        </Positioned>
        <Positioned left="440" top="200" width="200" height="200">
          <Container color="{ACCENT}" borderRadius="16"/>
        </Positioned>
      </Stack>
    </Container>
    <Container height="200" width="1080" padding="(40,40)">
      <Text text="2026.11.07 · ONLINE" color="#FFFFFF" fontSize="36" fontStyle="BOLD"/>
      <Text text="OPEN BETA" color="{PRIMARY}" fontSize="28"/>
      <Text text="layerlight.example.org" color="#CBD5E1" fontSize="24"/>
    </Container>
  </Column>
</Snapshot>'''
    return dsl

output_dir = Path('outputs/20261011-suite/A13')
output_dir.mkdir(parents=True, exist_ok=True)

# Generate and save
with open('tmp/20261011-suite/A13/symbol-color.snapshot', 'w', encoding='utf-8') as f:
    f.write(gen_icon("color"))
with open('tmp/20261011-suite/A13/symbol-black.snapshot', 'w', encoding='utf-8') as f:
    f.write(gen_icon("black"))
with open('tmp/20261011-suite/A13/brand-banner.snapshot', 'w', encoding='utf-8') as f:
    f.write(gen_banner())
with open('tmp/20261011-suite/A13/launch-poster.snapshot', 'w', encoding='utf-8') as f:
    f.write(gen_poster())

print("Generated all A13 DSL files")

# Save brand-system.json
import json
brand = {
    "schema_version": 1,
    "task_id": "A13",
    "path_base": "output_dir",
    "colors": {"primary": PRIMARY, "secondary": SECONDARY, "accent": ACCENT, "dark": DARK},
    "icon_components": [
        {"id": "R1", "shape": "rounded_rect", "color": PRIMARY, "position": "156,156,200,200"},
        {"id": "R2", "shape": "rounded_rect", "color": SECONDARY, "position": "196,196,200,200"},
        {"id": "R3", "shape": "rounded_rect", "color": ACCENT, "position": "236,236,200,200"}
    ],
    "applications": {
        "banner": "brand-banner.png",
        "poster": "launch-poster.png"
    }
}
with open(output_dir / 'brand-system.json', 'w', encoding='utf-8') as f:
    json.dump(brand, f, ensure_ascii=False, indent=2)
print("Saved brand-system.json")
