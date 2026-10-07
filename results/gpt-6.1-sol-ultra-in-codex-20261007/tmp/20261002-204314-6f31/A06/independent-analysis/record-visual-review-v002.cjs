const s = require('../../_suite/suite.cjs');
const v = s.view('A06','D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/A06/requests/A06-request-000002/response.png',{
  tool:'view_image', reviewer:'graph_auditor', version_id:'A06-v002',
  observation:'实际看过1600×1000 v002。14节点编号/完整标签都清晰；16先决实线各箭头朝向后层，N04→N13左侧长线完整，层号02/09在长线左侧无覆盖；两条反馈橙色虚线沿不同右侧轨道回N08，F1/F2解释及专用图例完整。主节点和注释无裁切、没有线压节点文字。JSON独立几何核验另保存，确认路线中段无其他节点内穿越。'
});
console.log(JSON.stringify(v,null,2));
