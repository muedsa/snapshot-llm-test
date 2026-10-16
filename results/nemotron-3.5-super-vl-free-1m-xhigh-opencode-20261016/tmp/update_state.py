import json

# Read current state
with open('outputs/run-20261016/_suite/suite-state.json', 'r', encoding='utf-8') as f:
    state = json.load(f)

# Mark A19 as completed
for t in state['tasks']:
    if t['id'] == 'A19':
        t['status'] = 'completed'
        t['started_at'] = '2026-10-16T12:05:00+08:00'
        t['ended_at'] = '2026-10-16T12:35:00+08:00'
        t['artifacts'] = [
            'grid-scene.png', 'grid-scene.snapshot',
            'occlusion.png', 'occlusion.snapshot',
            'occlusion-alternative.png', 'occlusion-alternative.snapshot',
            'scene-data.json', 'questions.json', 'answers.json',
            'equivalence.json', 'sources.md', 'examples.json',
            'snapshot-usage.md', 'task-metrics.json'
        ]
        t['visual_review_evidence'] = [
            'grid-scene.png 1600×1600',
            'occlusion.png 800×800',
            'occlusion-alternative.png 800×800',
            'scene-data.json', 'questions.json',
            'answers.json', 'equivalence.json'
        ]
        t['unresolved_issues'] = [
            '无法直接读取最终图像像素，视觉细节依DSL几何自检及PNG尺寸校验，建议人工复查最终图。'
        ]

with open('outputs/run-20261016/_suite/suite-state.json', 'w', encoding='utf-8') as f:
    json.dump(state, f, ensure_ascii=False, indent=2)
print("suite-state.json updated - A19 marked as completed")