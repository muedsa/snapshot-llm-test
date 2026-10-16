import json, os

# Check scene-data.json
d = 'outputs/run-20261016/A19/scene-data.json'
if os.path.exists(d):
    with open(d) as f:
        data = json.load(f)
    print(f'scene-data.json: {len(data.get("units",[]))} units')
    for u in data['units'][:5]:
        print(f'  {u}')
else:
    print('scene-data.json: NOT FOUND')

# Check questions.json
q = 'outputs/run-20261016/A19/questions.json'
if os.path.exists(q):
    with open(q) as f:
        data = json.load(f)
    print(f'questions.json: {len(data.get("questions",[]))} questions')
    for qq in data.get('questions',[])[:3]:
        print(f'  {qq}')
else:
    print('questions.json: NOT FOUND')
