from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
TEMP = ROOT / "tmp/20261124T113838+0800-aac601/A10"
image = Image.open(TEMP / "versions/v003/compositing-lab-01.png").convert("RGBA")
origins = [(208, 220), (560, 220), (912, 220), (208, 600), (560, 600), (912, 600)]
for index, (x, y) in enumerate(origins, 1):
    image.crop((x, y, x + 320, y + 240)).resize((640, 480)).save(TEMP / f"inspect-panel-{index:02d}.png")
image.crop((180, 950, 1260, 1080)).resize((1620, 195)).save(TEMP / "inspect-footer.png")
image.resize((1080, 825)).save(TEMP / "inspect-overview.png")
