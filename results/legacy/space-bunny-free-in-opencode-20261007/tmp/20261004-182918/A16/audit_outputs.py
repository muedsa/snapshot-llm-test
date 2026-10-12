# -*- coding: utf-8 -*-
import re
from PIL import Image

a = open(r'outputs\20261004-182918\A16\corrected-report.snapshot', 'rb').read()
b = open(r'tmp\20261004-182918\A16\drafts\v06.snapshot', 'rb').read()
print('final dsl bytes', len(a), '| draft v06 bytes', len(b), '| identical', a == b)
im = Image.open(r'outputs\20261004-182918\A16\corrected-report.png')
print('png', im.size, im.mode, im.format)
s = a.decode('utf-8')
print('has <Image>:', '<Image' in s, '| has dataUri:', 'dataUri' in s)
print('tags used:', sorted(set(re.findall(r'<([A-Za-z]+)', s))))
print('fontSize values:', sorted(set(re.findall(r'fontSize="([0-9.]+)"', s)), key=float))
print('fontStyle BOLD count:', s.count('BOLD'))
print('lines:', s.count(chr(10)) + 1)
png = open(r'outputs\20261004-182918\A16\corrected-report.png', 'rb').read()
print('png head:', png[:8], '| tail IEND ok:', png[-8:] == b'IEND\xaeB`\x82')