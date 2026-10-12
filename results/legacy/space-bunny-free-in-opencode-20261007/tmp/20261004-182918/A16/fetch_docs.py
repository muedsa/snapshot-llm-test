import os, sys
ROOT = r'D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004'
sys.path.insert(0, os.path.join(ROOT, 'tmp', '20261004-182918', '_suite'))
import snapkit
snapkit.configure('A16', os.path.join(ROOT, 'outputs', '20261004-182918', 'A16'),
                  os.path.join(ROOT, 'tmp', '20261004-182918', 'A16'))
for url, name in [
    ('https://snapshot.muedsa.com/reference/parser-tags/', 'parser-tags.html'),
    ('https://snapshot.muedsa.com/guides/widgets/', 'guide-widgets.html'),
    ('https://snapshot.muedsa.com/guides/layout/', 'guide-layout.html'),
]:
    print(snapkit.fetch_doc(url, name, 'document'))