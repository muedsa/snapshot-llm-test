import json

with open('outputs/run-20261016/_suite/suite-state.json', 'r', encoding='utf-8') as f:
    state = json.load(f)

# Mark A08, A14, A19 as completed
for t in state['tasks']:
    if t['id'] in ['A08', 'A14', 'A19']:
        t['status'] = 'completed'
        print(f"Marked {t['id']} as completed")

with open('outputs/run-20261016/_suite/suite-state.json', 'w', encoding='utf-8') as f:
    json.dump(state, f, ensure_ascii=False, indent=2)

print("suite-state.json updated - A08, A14, A19 marked as completed")
