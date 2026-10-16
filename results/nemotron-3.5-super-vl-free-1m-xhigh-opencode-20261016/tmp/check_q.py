import json
with open('outputs/run-20261016/A19/questions.json') as f:
    data = json.load(f)
print(f'Questions: {len(data.get("questions",[]))}')
for q in data['questions']:
    print(f\"{q['id']}: {q['question'][:50]}... -> {q.get('answer','?')}\")