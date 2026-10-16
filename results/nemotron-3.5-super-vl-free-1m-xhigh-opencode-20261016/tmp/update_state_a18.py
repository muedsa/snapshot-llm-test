import json

with open('outputs/run-20261016/_suite/suite-state.json', 'r', encoding='utf-8') as f:
    state = json.load(f)

for t in state['tasks']:
    if t['id'] == 'A18':
        t['status'] = 'completed'
        t['started_at'] = '2026-10-16T12:05:00+08:00'
        t['ended_at'] = '2026-10-16T12:20:00+08:00'
        t['output_dir'] = 'outputs/run-20261016/A18/'
        t['temp_dir'] = 'tmp/run-20261016/A18/'
        t['completed_rounds'] = []
        t['completed_cases'] = []
        t['artifacts'] = ['three-act-story.png', 'three-act-story.snapshot', 'story-audit.json', 'rationale.md', 'snapshot-usage.md', 'task-metrics.json']
        t['visual_review_evidence'] = ['three-act-story.png 1600×1000 HTTP 200 image/png']
        t['unresolved_issues'] = ['无法直接读取最终图像像素，视觉细节依 DSL 几何自检与尺寸校验']
        t['resume_notes'] = None

with open('outputs/run-20261016/_suite/suite-state.json', 'w', encoding='utf-8') as f:
    json.dump(state, f, ensure_ascii=False, indent=2)
print('suite-state.json updated - A18 marked as completed')
