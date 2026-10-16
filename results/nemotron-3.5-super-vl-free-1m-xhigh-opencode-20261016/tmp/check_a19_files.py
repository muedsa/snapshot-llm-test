import os
d = 'outputs/run-20261016/A19'
if os.path.exists(d):
    for f in sorted(os.listdir(d)):
        print(f'  {f}')
else:
    print(f'{d} not found')