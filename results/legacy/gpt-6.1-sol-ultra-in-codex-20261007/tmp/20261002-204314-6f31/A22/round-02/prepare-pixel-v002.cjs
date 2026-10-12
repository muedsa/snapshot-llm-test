const fs=require('node:fs'),path=require('node:path'),rd=__dirname;
let old=fs.readFileSync(path.join(rd,'pixel-regression-v001.py'),'utf8');
old=old.replace('A22-request-000004/response.png','A22-request-000005/response.png').replace('pixel-regression-v001.json','pixel-regression-v002.json').replace('mask[829:872,87:1527]=False','mask[829:872,87:1527]=False\nmask[884:919,87:1527]=False').replace('excludes only conclusion-main text box','excludes conclusion-main and conclusion-detail text boxes');
fs.writeFileSync(path.join(rd,'pixel-regression-v002.py'),old,{flag:'wx'});
