from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
TEMP = ROOT / "tmp/20261124T113838+0800-aac601/A11"
VERSION = TEMP / "versions/v001"
with Image.open(VERSION / "invoice-page-01-01.png") as image:
    image.crop((620, 970, 1170, 1470)).resize((1100, 1000)).save(TEMP / "inspect-totals.png")
with Image.open(VERSION / "invoice-page-02-01.png") as image:
    image.crop((48, 716, 1160, 1160)).resize((1112, 444)).save(TEMP / "inspect-literals.png")
    image.crop((48, 1170, 1160, 1335)).resize((1112, 165)).save(TEMP / "inspect-status.png")
    image.crop((48, 258, 1160, 710)).resize((1112, 452)).save(TEMP / "inspect-notes.png")
