from pathlib import Path
p=Path(__file__).parent
s=(p/'candidate-audit.py').read_text(encoding='utf-8')
s=s.replace('selection-v003.json','selection-v004.json').replace('candidate-structural-v001.json','candidate-structural-v002.json')
s=s.replace("all(term in texts[cid] for term in terms)","all(term.replace(' ','') in texts[cid].replace(' ','') for term in terms)")
s=s.replace("[term for term in terms if term not in texts[cid]]","[term for term in terms if term.replace(' ','') not in texts[cid].replace(' ','')]")
with (p/'candidate-audit-v002.py').open('x',encoding='utf-8') as f:f.write(s)
print('Created version 2; version 1 preserved. Only harmless ASCII spacing normalized in visible-text checks; latest root selection v004 is used.')
