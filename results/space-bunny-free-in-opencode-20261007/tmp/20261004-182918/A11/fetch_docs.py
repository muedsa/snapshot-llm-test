import os, sys
sys.path.insert(0, r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\tmp\20261004-182918\_suite")
import snapkit

OUT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\outputs\20261004-182918\A11"
TMP = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\tmp\20261004-182918\A11"
snapkit.configure("A11", OUT, TMP)

BASE = "https://snapshot.muedsa.com"
pages = [
    ("/guides/parser/", "parser.html"),
    ("/guides/media-text/", "media-text.html"),
    ("/reference/parser-tags/", "parser-tags.html"),
    ("/guides/widgets/", "widgets.html"),
    ("/guides/layout/", "layout.html"),
    ("/guides/painting/", "painting.html"),
    ("/guides/concepts/", "concepts.html"),
    ("/guides/rendering/", "rendering.html"),
]
for path, name in pages:
    st, p = snapkit.fetch_doc(BASE + path, name, kind="document")
    print(st, path, p)

st, p = snapkit.fetch_doc("https://open-snapshot.muedsa.com/fonts", "fonts-list.txt", kind="font_list")
print("FONTS", st, p)