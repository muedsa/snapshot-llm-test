import json
with open('outputs/run-20261016/_suite/suite-state.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
for t in data['tasks']:
    print(f"{t['id']}: {t['status']}")