import shutil, os
os.makedirs("outputs/run-20261016/A17", exist_ok=True)
os.makedirs("outputs/run-20261016/A19", exist_ok=True)

files = [
    ("tmp/run-20261016/A17/handbook-01.v1.snapshot", "outputs/run-20261016/A17/handbook-01.snapshot"),
    ("tmp/run-20261016/A17/handbook-02.v1.snapshot", "outputs/run-20261016/A17/handbook-02.snapshot"),
    ("tmp/run-20261016/A17/handbook-03.v1.snapshot", "outputs/run-20261016/A17/handbook-03.snapshot"),
    ("tmp/run-20261016/A17/handbook-04.v1.snapshot", "outputs/run-20261016/A17/handbook-04.snapshot"),
    ("tmp/run-20261016/A17/example-01.v1.snapshot", "outputs/run-20261016/A17/example-01.snapshot"),
    ("tmp/run-20261016/A17/example-02.v1.snapshot", "outputs/run-20261016/A17/example-02.snapshot"),
    ("tmp/run-20261016/A17/example-03.v1.snapshot", "outputs/run-20261016/A17/example-03.snapshot"),
    ("tmp/run-20261016/A17/example-04.v1.snapshot", "outputs/run-20261016/A17/example-04.snapshot"),
    ("tmp/run-20261016/A19/grid-scene.v1.snapshot", "outputs/run-20261016/A19/grid-scene.snapshot"),
    ("tmp/run-20261016/A19/occlusion.v1.snapshot", "outputs/run-20261016/A19/occlusion.snapshot"),
    ("tmp/run-20261016/A19/example-04.v1.snapshot", "outputs/run-20261016/A17/example-04.snapshot"),
]
for src, dst in files:
    shutil.copy2(src, dst)
    print(f"Copied {src} -> {dst}")
